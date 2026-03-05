"""replace hardcoded bank fields with generic JSON columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-04 23:00:00.000000
"""

import json

import sqlalchemy as sa

from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("extraction_logs", sa.Column("extracted_fields", sa.JSON(), nullable=True))
    op.add_column("extraction_logs", sa.Column("final_fields", sa.JSON(), nullable=True))

    conn = op.get_bind()
    results = conn.execute(
        sa.text(
            "SELECT id, extracted_owner, extracted_bank_name, extracted_account_number, "
            "final_owner, final_bank_name, final_account_number FROM extraction_logs"
        )
    )
    for row in results:
        extracted = json.dumps(
            {
                "owner": row[1] or "",
                "bank_name": row[2] or "",
                "account_number": row[3] or "",
            }
        )
        final = json.dumps(
            {
                "owner": row[4] or "",
                "bank_name": row[5] or "",
                "account_number": row[6] or "",
            }
        )
        conn.execute(
            sa.text(
                "UPDATE extraction_logs SET extracted_fields=:ef, final_fields=:ff WHERE id=:id"
            ),
            {"ef": extracted, "ff": final, "id": row[0]},
        )

    with op.batch_alter_table("extraction_logs") as batch_op:
        for col in [
            "extracted_owner",
            "extracted_bank_name",
            "extracted_account_number",
            "final_owner",
            "final_bank_name",
            "final_account_number",
            "owner_corrected",
            "bank_name_corrected",
            "account_number_corrected",
        ]:
            batch_op.drop_column(col)


def downgrade():
    with op.batch_alter_table("extraction_logs") as batch_op:
        batch_op.add_column(sa.Column("extracted_owner", sa.String(), server_default=""))
        batch_op.add_column(sa.Column("extracted_bank_name", sa.String(), server_default=""))
        batch_op.add_column(sa.Column("extracted_account_number", sa.String(), server_default=""))
        batch_op.add_column(sa.Column("final_owner", sa.String(), server_default=""))
        batch_op.add_column(sa.Column("final_bank_name", sa.String(), server_default=""))
        batch_op.add_column(sa.Column("final_account_number", sa.String(), server_default=""))
        batch_op.add_column(sa.Column("owner_corrected", sa.Boolean(), server_default="false"))
        batch_op.add_column(sa.Column("bank_name_corrected", sa.Boolean(), server_default="false"))
        batch_op.add_column(
            sa.Column("account_number_corrected", sa.Boolean(), server_default="false")
        )

    conn = op.get_bind()
    results = conn.execute(
        sa.text("SELECT id, extracted_fields, final_fields FROM extraction_logs")
    )
    for row in results:
        extracted = json.loads(row[1]) if row[1] else {}
        final = json.loads(row[2]) if row[2] else {}
        conn.execute(
            sa.text(
                "UPDATE extraction_logs SET "
                "extracted_owner=:eo, extracted_bank_name=:eb, extracted_account_number=:ea, "
                "final_owner=:fo, final_bank_name=:fb, final_account_number=:fa, "
                "owner_corrected=:oc, bank_name_corrected=:bc, account_number_corrected=:ac "
                "WHERE id=:id"
            ),
            {
                "eo": extracted.get("owner", ""),
                "eb": extracted.get("bank_name", ""),
                "ea": extracted.get("account_number", ""),
                "fo": final.get("owner", ""),
                "fb": final.get("bank_name", ""),
                "fa": final.get("account_number", ""),
                "oc": extracted.get("owner", "") != final.get("owner", ""),
                "bc": extracted.get("bank_name", "") != final.get("bank_name", ""),
                "ac": extracted.get("account_number", "") != final.get("account_number", ""),
                "id": row[0],
            },
        )

    op.drop_column("extraction_logs", "extracted_fields")
    op.drop_column("extraction_logs", "final_fields")
