"""add A/B testing columns

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-11 14:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"


def upgrade() -> None:
    op.add_column(
        "parser_config_versions",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    dialect = op.get_bind().dialect.name

    if dialect == "sqlite":
        # SQLite doesn't support ALTER with FK constraints
        op.add_column(
            "extraction_logs",
            sa.Column("parser_config_version_id", sa.Integer(), nullable=True),
        )
        op.add_column(
            "api_call_logs",
            sa.Column("parser_config_version_id", sa.Integer(), nullable=True),
        )
    else:
        op.add_column(
            "extraction_logs",
            sa.Column(
                "parser_config_version_id",
                sa.Integer(),
                sa.ForeignKey("parser_config_versions.id"),
                nullable=True,
            ),
        )
        op.add_column(
            "api_call_logs",
            sa.Column(
                "parser_config_version_id",
                sa.Integer(),
                sa.ForeignKey("parser_config_versions.id"),
                nullable=True,
            ),
        )


def downgrade() -> None:
    op.drop_column("api_call_logs", "parser_config_version_id")
    op.drop_column("extraction_logs", "parser_config_version_id")
    op.drop_column("parser_config_versions", "is_active")
