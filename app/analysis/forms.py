# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - present Orange Cyberdefense
"""

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, TextAreaField, widgets, SelectField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired

from app.constants import IGNORE_LIST


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ScanForm(FlaskForm):
    project_id = HiddenField(
        "Project id", id="scan-project-id", validators=[DataRequired()]
    )
    ignore_paths = TextAreaField("Ignore paths", id="scan-ignore-paths")
    ignore_filenames = TextAreaField("Ignore files", id="scan-ignore-files", default=IGNORE_LIST)
    rule_packs = MultiCheckboxField("Rule packs", coerce=int)
