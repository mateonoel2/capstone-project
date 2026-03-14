"""Add status column to extractor_configs and create test_extraction_logs table

Revision ID: h8c9d0e1f2a3
Revises: g7b8c9d0e1f2
Create Date: 2026-03-14
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h8c9d0e1f2a3"
down_revision: Union[str, None] = "g7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status column to extractor_configs
    op.add_column(
        "extractor_configs",
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )

    # Create test_extraction_logs table
    op.create_table(
        "test_extraction_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("filename", sa.String, nullable=False),
        sa.Column("s3_key", sa.String, nullable=False),
        sa.Column(
            "extractor_config_id",
            sa.Integer,
            sa.ForeignKey("extractor_configs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("prompt_snapshot", sa.Text, nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("output_schema_snapshot", sa.JSON, nullable=False),
        sa.Column("extracted_fields", sa.JSON, nullable=True),
        sa.Column("success", sa.Boolean, nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("response_time_ms", sa.Float, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("test_extraction_logs")
    op.drop_column("extractor_configs", "status")
