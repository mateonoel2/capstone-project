"""backfill NULL parser_config_id with default config

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-11 12:00:00.000000
"""

from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"


def upgrade() -> None:
    op.execute("UPDATE extraction_logs SET parser_config_id = 1 WHERE parser_config_id IS NULL")
    op.execute("UPDATE api_call_logs SET parser_config_id = 1 WHERE parser_config_id IS NULL")


def downgrade() -> None:
    op.execute("UPDATE extraction_logs SET parser_config_id = NULL WHERE parser_config_id = 1")
    op.execute("UPDATE api_call_logs SET parser_config_id = NULL WHERE parser_config_id = 1")
