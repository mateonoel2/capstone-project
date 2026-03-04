"""Initial extraction_logs table

Revision ID: 554efd373264
Revises:
Create Date: 2026-03-03 20:57:26.612847

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "554efd373264"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extraction_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("extracted_owner", sa.String(), server_default=""),
        sa.Column("extracted_bank_name", sa.String(), server_default=""),
        sa.Column("extracted_account_number", sa.String(), server_default=""),
        sa.Column("final_owner", sa.String(), server_default=""),
        sa.Column("final_bank_name", sa.String(), server_default=""),
        sa.Column("final_account_number", sa.String(), server_default=""),
        sa.Column("owner_corrected", sa.Boolean(), server_default=sa.false()),
        sa.Column("bank_name_corrected", sa.Boolean(), server_default=sa.false()),
        sa.Column("account_number_corrected", sa.Boolean(), server_default=sa.false()),
    )
    op.create_index("ix_extraction_logs_id", "extraction_logs", ["id"])


def downgrade() -> None:
    op.drop_table("extraction_logs")
