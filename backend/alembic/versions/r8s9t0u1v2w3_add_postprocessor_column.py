"""Add postprocessor column to extractor_configs.

Revision ID: r8s9t0u1v2w3
Revises: q7r8s9t0u1v2
Create Date: 2026-03-27 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "r8s9t0u1v2w3"
down_revision = "q7r8s9t0u1v2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("extractor_configs", sa.Column("postprocessor", sa.String(100), nullable=True))
    # Backfill: default extractors with account_number in schema get the postprocessor
    op.execute(
        "UPDATE extractor_configs SET postprocessor = 'mexican_bank_statement' "
        "WHERE is_default = true "
        "AND output_schema::text LIKE '%account_number%'"
    )


def downgrade() -> None:
    op.drop_column("extractor_configs", "postprocessor")
