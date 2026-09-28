"""add deployment provider fields

Revision ID: 20260928_0002
Revises: 20260928_0001
Create Date: 2026-09-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260928_0002"
down_revision: str | None = "20260928_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("deployment_target", sa.String(length=20), nullable=True))
    op.add_column(
        "projects", sa.Column("deployment_project_id", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "projects", sa.Column("deployment_service_id", sa.String(length=255), nullable=True)
    )
    op.add_column("projects", sa.Column("deployment_id", sa.String(length=255), nullable=True))
    op.add_column("projects", sa.Column("deployment_url", sa.String(length=500), nullable=True))
    op.add_column(
        "projects", sa.Column("deployment_project_url", sa.String(length=500), nullable=True)
    )
    op.create_index(
        "ix_projects_deployment_target", "projects", ["deployment_target"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_projects_deployment_target", table_name="projects")
    op.drop_column("projects", "deployment_project_url")
    op.drop_column("projects", "deployment_url")
    op.drop_column("projects", "deployment_id")
    op.drop_column("projects", "deployment_service_id")
    op.drop_column("projects", "deployment_project_id")
    op.drop_column("projects", "deployment_target")
