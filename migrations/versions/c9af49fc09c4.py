"""Init

Revision ID: c9af49fc09c4
Revises: 
Create Date: 2023-02-02 22:44:35.807919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9af49fc09c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('LdapConfiguration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ldap_activated', sa.Boolean(), nullable=False),
    sa.Column('server_host', sa.String(), nullable=True),
    sa.Column('server_port', sa.Integer(), nullable=True),
    sa.Column('use_tls', sa.Boolean(), nullable=True),
    sa.Column('cacert_path', sa.String(), nullable=True),
    sa.Column('users_approval', sa.Boolean(), nullable=True),
    sa.Column('bind_dn', sa.String(), nullable=True),
    sa.Column('bind_password', sa.String(), nullable=True),
    sa.Column('base_dn', sa.String(), nullable=True),
    sa.Column('users_dn', sa.String(), nullable=True),
    sa.Column('groups_dn', sa.String(), nullable=True),
    sa.Column('user_rdn_attr', sa.String(), nullable=True),
    sa.Column('user_login_attr', sa.String(), nullable=True),
    sa.Column('user_object_filter', sa.String(), nullable=True),
    sa.Column('group_object_filter', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('RulePack',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('RuleRepository',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('uri', sa.String(), nullable=True),
    sa.Column('last_update_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('SupportedLanguage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('extensions', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('local', sa.Boolean(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.LargeBinary(), nullable=True),
    sa.Column('dark_theme', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('archive_filename', sa.String(), nullable=True),
    sa.Column('archive_sha256sum', sa.String(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('occurences_count', sa.Integer(), nullable=True),
    sa.Column('risk_level', sa.Integer(), nullable=True),
    sa.Column('error_message', sa.String(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Rule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('severity', sa.String(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('cwe', sa.String(), nullable=True),
    sa.Column('owasp', sa.String(), nullable=True),
    sa.Column('repository_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['repository_id'], ['RuleRepository.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('RulePackToSupportedLanguageAssociation',
    sa.Column('rule_pack_id', sa.Integer(), nullable=True),
    sa.Column('supported_language_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rule_pack_id'], ['RulePack.id'], ),
    sa.ForeignKeyConstraint(['supported_language_id'], ['SupportedLanguage.id'], )
    )
    op.create_table('Analysis',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('started_on', sa.DateTime(), nullable=True),
    sa.Column('finished_on', sa.DateTime(), nullable=True),
    sa.Column('ignore_paths', sa.String(), nullable=True),
    sa.Column('ignore_filenames', sa.String(), nullable=True),
    sa.Column('task_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('AppInspector',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ProjectLinesCount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total_file_count', sa.Integer(), nullable=True),
    sa.Column('total_line_count', sa.Integer(), nullable=True),
    sa.Column('total_blank_count', sa.Integer(), nullable=True),
    sa.Column('total_comment_count', sa.Integer(), nullable=True),
    sa.Column('total_code_count', sa.Integer(), nullable=True),
    sa.Column('total_complexity_count', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('RuleToRulePackAssociation',
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.Column('rule_pack_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['Rule.id'], ),
    sa.ForeignKeyConstraint(['rule_pack_id'], ['RulePack.id'], )
    )
    op.create_table('RuleToSupportedLanguageAssociation',
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.Column('supported_language_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['Rule.id'], ),
    sa.ForeignKeyConstraint(['supported_language_id'], ['SupportedLanguage.id'], )
    )
    op.create_table('AnalysisToRulePackAssociation',
    sa.Column('analysis_id', sa.Integer(), nullable=True),
    sa.Column('rule_pack_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['analysis_id'], ['Analysis.id'], ),
    sa.ForeignKeyConstraint(['rule_pack_id'], ['RulePack.id'], )
    )
    op.create_table('LanguageLinesCount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('file_count', sa.Integer(), nullable=True),
    sa.Column('line_count', sa.Integer(), nullable=True),
    sa.Column('blank_count', sa.Integer(), nullable=True),
    sa.Column('comment_count', sa.Integer(), nullable=True),
    sa.Column('code_count', sa.Integer(), nullable=True),
    sa.Column('complexity_count', sa.Integer(), nullable=True),
    sa.Column('project_lines_count_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_lines_count_id'], ['ProjectLinesCount.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('app_inspector_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('pattern', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('tags', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['app_inspector_id'], ['AppInspector.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Vulnerability',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('analysis_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('severity', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('cwe', sa.String(), nullable=True),
    sa.Column('owasp', sa.String(), nullable=True),
    sa.Column('references', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['analysis_id'], ['Analysis.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('InspectorTag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=False),
    sa.Column('excerpt', sa.String(), nullable=True),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('severity', sa.String(), nullable=False),
    sa.Column('start_column', sa.Integer(), nullable=True),
    sa.Column('start_line', sa.Integer(), nullable=True),
    sa.Column('end_column', sa.Integer(), nullable=True),
    sa.Column('end_line', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['Match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Occurence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vulnerability_id', sa.Integer(), nullable=False),
    sa.Column('match_string', sa.String(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['vulnerability_id'], ['Vulnerability.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Position',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('occurence_id', sa.Integer(), nullable=True),
    sa.Column('line_start', sa.Integer(), nullable=True),
    sa.Column('line_end', sa.Integer(), nullable=True),
    sa.Column('column_start', sa.Integer(), nullable=True),
    sa.Column('column_end', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['occurence_id'], ['Occurence.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('Position')
    op.drop_table('Occurence')
    op.drop_table('InspectorTag')
    op.drop_table('Vulnerability')
    op.drop_table('Match')
    op.drop_table('LanguageLinesCount')
    op.drop_table('AnalysisToRulePackAssociation')
    op.drop_table('RuleToSupportedLanguageAssociation')
    op.drop_table('RuleToRulePackAssociation')
    op.drop_table('ProjectLinesCount')
    op.drop_table('AppInspector')
    op.drop_table('Analysis')
    op.drop_table('RulePackToSupportedLanguageAssociation')
    op.drop_table('Rule')
    op.drop_table('Project')
    op.drop_table('User')
    op.drop_table('SupportedLanguage')
    op.drop_table('RuleRepository')
    op.drop_table('RulePack')
    op.drop_table('LdapConfiguration')
