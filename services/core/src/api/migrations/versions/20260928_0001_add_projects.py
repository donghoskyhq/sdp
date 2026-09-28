"""add projects

Revision ID: 20260928_0001
Revises:
Create Date: 2026-09-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260928_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("repository_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=350), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("github_url", sa.String(length=500), nullable=True),
        sa.Column("github_full_name", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_repository_name", "projects", ["repository_name"], unique=True)
    op.create_index("ix_projects_status", "projects", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_repository_name", table_name="projects")
    op.drop_table("projects")
