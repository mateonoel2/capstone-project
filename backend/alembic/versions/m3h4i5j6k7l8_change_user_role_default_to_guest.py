"""Change user role server_default from 'user' to 'guest'

Revision ID: m3h4i5j6k7l8
Revises: l2g3h4i5j6k7
Create Date: 2026-03-25
"""

from alembic import op

revision = "m3h4i5j6k7l8"
down_revision = "l2g3h4i5j6k7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("role", server_default="guest")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("role", server_default="user")
