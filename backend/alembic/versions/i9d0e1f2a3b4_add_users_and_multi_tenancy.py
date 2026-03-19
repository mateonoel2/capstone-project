"""Add users table and multi-tenancy support

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
Create Date: 2026-03-18
"""

import sqlalchemy as sa

from alembic import context, op

revision = "i9d0e1f2a3b4"
down_revision = "h8c9d0e1f2a3"
branch_labels = None
depends_on = None


def _is_sqlite() -> bool:
    return context.get_context().dialect.name == "sqlite"


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("github_id", sa.Integer(), unique=True, nullable=True, index=True),
        sa.Column("github_username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
    )

    # 2. Seed admin user
    op.execute(sa.text("INSERT INTO users (github_username, role) VALUES ('mateonoel2', 'admin')"))

    # 3. Add user_id column + FK to existing tables
    tables_needing_user_id = [
        "extraction_logs",
        "api_call_logs",
        "test_extraction_logs",
    ]

    if _is_sqlite():
        # SQLite: use batch mode for ALTER support
        for table in tables_needing_user_id:
            with op.batch_alter_table(table) as batch_op:
                batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
                batch_op.create_foreign_key(f"fk_{table}_user_id", "users", ["user_id"], ["id"])

        # extractor_configs: also replace unique(name)
        naming = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
        with op.batch_alter_table("extractor_configs", naming_convention=naming) as batch_op:
            batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_extractor_configs_user_id",
                "users",
                ["user_id"],
                ["id"],
            )
            batch_op.drop_constraint("uq_extractor_configs_name", type_="unique")
            batch_op.create_unique_constraint("uq_extractor_configs_name_user", ["name", "user_id"])
    else:
        # PostgreSQL: direct ALTER
        for table in tables_needing_user_id:
            op.add_column(table, sa.Column("user_id", sa.Integer(), nullable=True))
            op.create_foreign_key(f"fk_{table}_user_id", table, "users", ["user_id"], ["id"])

        op.add_column(
            "extractor_configs",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_extractor_configs_user_id",
            "extractor_configs",
            "users",
            ["user_id"],
            ["id"],
        )
        # Constraint kept old name from when table was parser_configs
        op.drop_constraint(
            "parser_configs_name_key",
            "extractor_configs",
            type_="unique",
        )
        op.create_unique_constraint(
            "uq_extractor_configs_name_user",
            "extractor_configs",
            ["name", "user_id"],
        )

    # 4. Backfill: assign all existing rows to admin user
    admin_sub = "(SELECT id FROM users WHERE role = 'admin' LIMIT 1)"
    all_tables = ["extractor_configs"] + tables_needing_user_id
    for table in all_tables:
        op.execute(sa.text(f"UPDATE {table} SET user_id = {admin_sub}"))


def downgrade() -> None:
    if _is_sqlite():
        naming = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
        with op.batch_alter_table("extractor_configs", naming_convention=naming) as batch_op:
            batch_op.drop_constraint("uq_extractor_configs_name_user", type_="unique")
            batch_op.create_unique_constraint("uq_extractor_configs_name", ["name"])
            batch_op.drop_constraint("fk_extractor_configs_user_id", type_="foreignkey")
            batch_op.drop_column("user_id")

        for table in [
            "test_extraction_logs",
            "api_call_logs",
            "extraction_logs",
        ]:
            with op.batch_alter_table(table) as batch_op:
                batch_op.drop_constraint(f"fk_{table}_user_id", type_="foreignkey")
                batch_op.drop_column("user_id")
    else:
        op.drop_constraint(
            "uq_extractor_configs_name_user",
            "extractor_configs",
            type_="unique",
        )
        op.create_unique_constraint("parser_configs_name_key", "extractor_configs", ["name"])
        op.drop_constraint(
            "fk_extractor_configs_user_id",
            "extractor_configs",
            type_="foreignkey",
        )
        op.drop_column("extractor_configs", "user_id")

        for table in [
            "test_extraction_logs",
            "api_call_logs",
            "extraction_logs",
        ]:
            op.drop_constraint(f"fk_{table}_user_id", table, type_="foreignkey")
            op.drop_column(table, "user_id")

    op.drop_table("users")
