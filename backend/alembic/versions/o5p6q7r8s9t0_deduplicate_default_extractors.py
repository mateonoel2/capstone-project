"""Remove duplicate default receipt extractors

Revision ID: o5p6q7r8s9t0
Revises: n4i5j6k7l8m9
Create Date: 2026-03-25
"""

from sqlalchemy import text

from alembic import op

revision = "o5p6q7r8s9t0"
down_revision = "n4i5j6k7l8m9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # For each user, keep only the oldest "Boletas y recibos" extractor and delete duplicates
    conn.execute(
        text("""
            DELETE FROM extractor_configs
            WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (
                        PARTITION BY user_id, name
                        ORDER BY created_at ASC
                    ) AS rn
                    FROM extractor_configs
                    WHERE name = 'Boletas y recibos'
                ) dupes
                WHERE rn > 1
            )
        """)
    )

    # If a user already has another default extractor, unmark "Boletas y recibos" as default
    conn.execute(
        text("""
            UPDATE extractor_configs
            SET is_default = false
            WHERE name = 'Boletas y recibos'
            AND is_default = true
            AND user_id IN (
                SELECT user_id FROM extractor_configs
                WHERE is_default = true
                GROUP BY user_id
                HAVING COUNT(*) > 1
            )
        """)
    )


def downgrade() -> None:
    # Cannot restore deleted duplicates
    pass
