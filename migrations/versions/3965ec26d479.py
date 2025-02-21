"""Add __repr__ for project in db

Revision ID: 3965ec26d479
Revises: 0914a29d984d
Create Date: 2024-03-01 15:28:50.439943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3965ec26d479'
down_revision = '0914a29d984d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('Project', schema=None) as batch_op:
        batch_op.drop_constraint('fk_project_team_id', type_='foreignkey')
        batch_op.drop_column('team_id')

    with op.batch_alter_table('team_members', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'Team', ['team_id'], ['id'])
        batch_op.create_foreign_key(None, 'User', ['user_id'], ['id'])

    with op.batch_alter_table('team_projets', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'Team', ['team_id'], ['id'])
        batch_op.create_foreign_key(None, 'Project', ['project_id'], ['id'])


def downgrade():
    with op.batch_alter_table('team_projets', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'project', ['project_id'], ['id'])
        batch_op.create_foreign_key(None, 'team', ['team_id'], ['id'])

    with op.batch_alter_table('team_members', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'team', ['team_id'], ['id'])

    with op.batch_alter_table('Project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_project_team_id', 'Team', ['team_id'], ['id'])
