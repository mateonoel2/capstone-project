"""Add privacy and security tables: audit_logs, data_consents, encrypted extraction fields

Revision ID: l2g3h4i5j6k7
Revises: k1f2a3b4c5d6
Create Date: 2026-03-21 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "l2g3h4i5j6k7"
down_revision: str | None = "k1f2a3b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Audit logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(50), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True, index=True),
    )

    # Data consents table
    op.create_table(
        "data_consents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("consent_type", sa.String(100), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("granted_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("policy_version", sa.String(20), nullable=False, server_default="1.0"),
    )

    # Convert extraction_logs JSON columns to Text for encryption
    # The EncryptedJSON TypeDecorator stores encrypted ciphertext as Text
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        # PostgreSQL: cast JSON to Text
        op.execute(
            "ALTER TABLE extraction_logs "
            "ALTER COLUMN extracted_fields TYPE TEXT "
            "USING extracted_fields::TEXT"
        )
        op.execute(
            "ALTER TABLE extraction_logs "
            "ALTER COLUMN final_fields TYPE TEXT "
            "USING final_fields::TEXT"
        )
    # SQLite: columns are already flexible, no action needed


def downgrade() -> None:
    op.drop_table("data_consents")
    op.drop_table("audit_logs")

    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute(
            "ALTER TABLE extraction_logs "
            "ALTER COLUMN extracted_fields TYPE JSON "
            "USING extracted_fields::JSON"
        )
        op.execute(
            "ALTER TABLE extraction_logs "
            "ALTER COLUMN final_fields TYPE JSON "
            "USING final_fields::JSON"
        )
