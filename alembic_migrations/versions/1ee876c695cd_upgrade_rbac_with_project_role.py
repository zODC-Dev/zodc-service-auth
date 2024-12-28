"""Upgrade RBAC with Project Role

Revision ID: 1ee876c695cd
Revises: ed1e4f679af1
Create Date: 2024-12-15 23:31:41.944199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1ee876c695cd'
down_revision: Union[str, None] = 'ed1e4f679af1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_key'), 'projects', ['key'], unique=True)

    # Create user_project_roles table
    op.create_table('user_project_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add name column as nullable first
    op.add_column('users', sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Update existing users to use email as name
    op.execute("UPDATE users SET name = email WHERE name IS NULL")

    # Make name column not nullable
    op.alter_column('users', 'name',
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False
    )

    # Add other user columns
    op.add_column('users', sa.Column('jira_refresh_token', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))

    # Add foreign key for role_id
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])

    # Drop old tables and columns
    op.drop_table('user_roles')
    op.drop_constraint('users_microsoft_id_key', 'users', type_='unique')
    op.drop_column('users', 'password')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'microsoft_token')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'microsoft_id')
    op.drop_column('users', 'roles')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'permissions')
    op.drop_column('users', 'is_active')


def downgrade() -> None:
    # Restore old columns
    op.add_column('users', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('full_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('roles', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('microsoft_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text("'2024-12-10 18:42:51.471978'::timestamp without time zone"), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('microsoft_token', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=60), autoincrement=False, nullable=True))

    # Restore constraints
    op.create_unique_constraint('users_microsoft_id_key', 'users', ['microsoft_id'])

    # Drop new columns
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    op.drop_column('users', 'jira_refresh_token')
    op.drop_column('users', 'name')

    # Drop new tables
    op.drop_table('user_project_roles')
    op.drop_index(op.f('ix_projects_key'), table_name='projects')
    op.drop_table('projects')

    # Restore old tables
    op.create_table('user_roles',
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('role_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='user_roles_role_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_roles_user_id_fkey'),
        sa.PrimaryKeyConstraint('user_id', 'role_id', name='user_roles_pkey')
    )
