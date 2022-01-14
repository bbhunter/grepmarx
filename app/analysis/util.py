# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - present Orange Cyberdefense
"""

import json
import multiprocessing
import os
import re
from datetime import datetime
from glob import glob
from io import StringIO
from shutil import copyfile, rmtree

from flask import current_app
from app import celery, db
from app.analysis.models import (
    Analysis,
    Occurence,
    Position,
    Vulnerability,
)
from app.constants import (
    EXTRACT_FOLDER_NAME,
    PROJECTS_SRC_PATH,
    RULE_EXTENSIONS,
    RULES_PATH,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    STATUS_ANALYZING,
    STATUS_ERROR,
    STATUS_FINISHED,
)
from app.rules.util import generate_severity
from semgrep import semgrep_main, util
from semgrep.constants import OutputFormat

from semgrep.error import SemgrepError
from semgrep.output import OutputHandler, OutputSettings

##
## Analysis utils
##


@celery.task(name="grepmarx-scan")
def async_scan(analysis_id):
    """Launch a new code scan on the project corresponding to the given analysis ID, asynchronously through celery.

    Args:
        analysis_id (int): ID of the analysis to populate with the results
    """
    current_app.logger.debug("Entering async scan for analysis with id=%i", analysis_id)
    analysis = Analysis.query.filter_by(id=analysis_id).first()
    # Status in now Analysing
    analysis.started_on = datetime.now()
    analysis.project.status = STATUS_ANALYZING
    db.session.commit()
    # Prepare semgrep options
    files_to_scan, project_rules_path, ignore = generate_semgrep_options(analysis)
    # Invoke semgrep
    try:
        semgrep_result = semgrep_scan(files_to_scan, project_rules_path, ignore)
        save_result(analysis, semgrep_result)
        load_scan_results(analysis, semgrep_result)
        analysis.project.status = STATUS_FINISHED
    except SemgrepError as e:
        analysis.project.error_message = repr(e)
        analysis.project.status = STATUS_ERROR
        current_app.logger.error(
            "Error while scanning project with id=%i: %s", analysis.project.id, str(e)
        )
    # Done
    analysis.finished_on = datetime.now()
    db.session.commit()


def semgrep_scan(files_to_scan, project_rules_path, ignore):
    """Launch the actual semgrep scan.

    Args:
        files_to_scan (list): files' paths to be scanned
        project_rules_path (str): path to the folder with semgrep YML rules
        ignore (list): patterns of paths / filenames to skip

    Returns:
        [str]: Semgrep JSON output
    """
    cpu_count = multiprocessing.cpu_count()
    util.set_flags(verbose=False, debug=False, quiet=True, force_color=False)
    semgrep_output = StringIO()
    output_handler = OutputHandler(
        OutputSettings(
            output_format=OutputFormat.JSON,
            output_destination=None,
            error_on_findings=False,
            verbose_errors=False,
            strict=False,
            timeout_threshold=3,
            json_stats=False,
            output_per_finding_max_lines_limit=None,
        ),
        stdout=semgrep_output,
    )
    semgrep_main.main(
        output_handler=output_handler,
        target=files_to_scan,
        jobs=cpu_count,
        pattern=None,
        lang=None,
        configs=[project_rules_path],
        timeout=5,
        timeout_threshold=3,
        exclude=ignore,
    )
    output_handler.close()
    return semgrep_output.getvalue()


def save_result(analysis, semgrep_result):
    """Save Semgrep JSON results as a file in the project's directory.

    Args:
        analysis (Analysis): corresponding analysis
        semgrep_result (str): Semgrep JSON results as string
    """    
    filename = os.path.join(
        PROJECTS_SRC_PATH,
        str(analysis.project.id),
        "analysis_" + str(analysis.id) + ".json",
    )
    f = open(filename, "a")
    f.write(semgrep_result)
    f.close()


def load_scan_results(analysis, semgrep_output):
    """Populate an Analysis object with the result of a Semgrep scan.

    Args:
        semgrep_output (str): Semgrep JSON output as string
    """
    vulns = list()
    json_result = json.loads(semgrep_output)
    if json_result is not None:
        # Ignore errors, focus on results
        if "results" in json_result:
            results = json_result["results"]
            for c_result in results:
                title = c_result["check_id"].split(".")[-1]
                # Is it a new vulnerability or another occurence of a known one?
                e_vulns = [v for v in vulns if v.title == title]
                if len(e_vulns) == 0:
                    # Create a new vulnerability
                    n_vuln = load_vulnerability(title, c_result)
                    n_vuln.occurences.append(load_occurence(c_result))
                    vulns.append(n_vuln)
                else:
                    # Add an occurence to an existing vulnerability
                    e_vuln = e_vulns[0]
                    e_vuln.occurences.append(load_occurence(c_result))
    analysis.vulnerabilities = vulns


def load_vulnerability(title, semgrep_result):
    """Create a vulnerability object from a 'result' element of semgrep JSON results.

    Args:
        title (string): finding's title
        match_dict (dict): match element with its properties

    Returns:
        Vulnerability: fully populated vulnerability
    """
    vuln = Vulnerability(title=title)
    extra = semgrep_result["extra"]
    if "message" in extra:
        vuln.description = extra["message"]
    if "metadata" in extra:
        metadata = extra["metadata"]
        if "cwe" in metadata:
            vuln.cwe = metadata["cwe"]
        if "owasp" in metadata:
            vuln.owasp = metadata["owasp"]
        if "references" in metadata:
            vuln.references = " ".join(metadata["references"])
        vuln.severity = generate_severity(vuln.cwe)
    return vuln


def load_occurence(semgrep_result):
    """Create an occurence object from a 'result' element of semgrep JSON results.

    Args:
        semgrep_result (dict): 'result' elements with its properties

    Returns:
        Occurence: fully populated occurence
    """
    pattern = PROJECTS_SRC_PATH + "[\\/]?\d+[\\/]" + EXTRACT_FOLDER_NAME + "[\\/]?"
    clean_path = re.sub(pattern, "", semgrep_result["path"])
    occurence = Occurence(
        file_path=clean_path, match_string=semgrep_result["extra"]["lines"]
    )
    occurence.position = Position(
        line_start=semgrep_result["start"]["line"],
        line_end=semgrep_result["end"]["line"],
        column_start=semgrep_result["start"]["col"],
        column_end=semgrep_result["end"]["col"],
    )
    return occurence


def generate_semgrep_options(analysis):
    """Generate semgrep options depending on the attributes of an analysis.

    Args:
        analysis (Analysis): generate options for this analysis and parent project

    Returns:
        files_to_scan (list): files' paths to be scanned
        project_rules_path (str): path to the folder with semgrep YML rules
        ignore (list): patterns of paths / filenames to skip
    """
    # Define the scan path
    scan_path = os.path.join(
        PROJECTS_SRC_PATH, str(analysis.project.id), EXTRACT_FOLDER_NAME
    )
    # Define rules path
    project_rules_path = os.path.join(
        PROJECTS_SRC_PATH, str(analysis.project.id), "rules"
    )
    # Consolidate ignore list
    ignore = set(
        # Remove empty elements
        filter(None, analysis.ignore_filenames.split(","))
    )
    # Get all files corresponding to target extensions in project's source
    files_to_scan = list()
    for c_rule_pack in analysis.rule_packs:
        for c_language in c_rule_pack.languages:
            # Remove empty elements
            extensions = filter(None, c_language.extensions.split(","))
            for c_ext in extensions:
                files_to_scan += glob(
                    pathname=os.path.join(scan_path, "**", "*" + c_ext), recursive=True
                )
    return (files_to_scan, project_rules_path, ignore)


def import_rules(analysis, rule_folder):
    """Copy all YML files corresponding to rules of an analysis' rule packs into a (project) folder.

    Args:
        analysis (Analysis): analysis object of the project in whose folder rules should be imported
        rule_folder (str): destination folder (usually data/projects/<project_id>/rules/)
    """
    if os.path.isdir(rule_folder):
        rmtree(rule_folder)
    os.mkdir(rule_folder)
    for c_rule_pack in analysis.rule_packs:
        for c_rule in c_rule_pack.rules:
            src = os.path.join(RULES_PATH, c_rule.file_path)
            dst = os.path.join(
                rule_folder,
                c_rule.repository.name
                + "_"
                + c_rule.category
                + "."
                + c_rule.title
                + next(iter(RULE_EXTENSIONS)),
            )
            copyfile(src, dst)
            current_app.logger.debug(
                "Imported rule for project with id=%i: %s",
                analysis.project.id,
                dst,
            )


def vulnerabilities_sorted_by_severity(analysis):
    """Get vulnerabilities of an analysis sorted by their severity level (most critical first).

    Args:
        analysis (Analysis): analysis object populated with vulnerabilities

    Returns:
        list: vulnerability objects sorted by severity
    """
    r_vulns = list()
    low_vulns = list()
    for c_vulns in analysis.vulnerabilities:
        if c_vulns.severity == SEVERITY_HIGH:
            r_vulns.insert(0, c_vulns)
        elif c_vulns.severity == SEVERITY_MEDIUM:
            r_vulns.append(c_vulns)
        else:
            low_vulns.append(c_vulns)
    r_vulns.extend(low_vulns)
    return r_vulns