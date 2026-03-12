"""rename parser to extractor

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-11 18:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def _drop_all_fks(table_name: str) -> None:
    """Drop all foreign key constraints on a table, using introspection."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    for fk in inspector.get_foreign_keys(table_name):
        if fk.get("name"):
            op.drop_constraint(fk["name"], table_name, type_="foreignkey")


def upgrade() -> None:
    if not _is_sqlite():
        # 1. Drop FK constraints (PostgreSQL only) — use introspection
        #    because constraint names vary depending on how they were created
        _drop_all_fks("extraction_logs")
        _drop_all_fks("api_call_logs")
        _drop_all_fks("parser_config_versions")

    # 2. Rename tables
    op.rename_table("parser_configs", "extractor_configs")
    op.rename_table("parser_config_versions", "extractor_config_versions")

    # 3. Rename columns in extractor_config_versions
    op.alter_column(
        "extractor_config_versions",
        "parser_config_id",
        new_column_name="extractor_config_id",
    )

    # 4. Rename columns in extraction_logs
    op.alter_column(
        "extraction_logs",
        "parser_config_id",
        new_column_name="extractor_config_id",
    )
    op.alter_column(
        "extraction_logs",
        "parser_config_version_id",
        new_column_name="extractor_config_version_id",
    )

    # 5. Rename columns in api_call_logs
    op.alter_column(
        "api_call_logs",
        "parser_config_id",
        new_column_name="extractor_config_id",
    )
    op.alter_column(
        "api_call_logs",
        "parser_config_version_id",
        new_column_name="extractor_config_version_id",
    )

    if not _is_sqlite():
        # 6. Re-create FK constraints with new names (PostgreSQL only)
        op.create_foreign_key(
            "extractor_config_versions_extractor_config_id_fkey",
            "extractor_config_versions",
            "extractor_configs",
            ["extractor_config_id"],
            ["id"],
        )
        op.create_foreign_key(
            "extraction_logs_extractor_config_id_fkey",
            "extraction_logs",
            "extractor_configs",
            ["extractor_config_id"],
            ["id"],
        )
        op.create_foreign_key(
            "extraction_logs_extractor_config_version_id_fkey",
            "extraction_logs",
            "extractor_config_versions",
            ["extractor_config_version_id"],
            ["id"],
        )
        op.create_foreign_key(
            "api_call_logs_extractor_config_id_fkey",
            "api_call_logs",
            "extractor_configs",
            ["extractor_config_id"],
            ["id"],
        )
        op.create_foreign_key(
            "api_call_logs_extractor_config_version_id_fkey",
            "api_call_logs",
            "extractor_config_versions",
            ["extractor_config_version_id"],
            ["id"],
        )

    # 7. Update seeded default description text
    op.execute(
        sa.text(
            "UPDATE extractor_configs "
            "SET description = 'Extractor por defecto para estados de cuenta bancarias mexicanas' "
            "WHERE description = 'Parser por defecto para estados de cuenta bancarias mexicanas'"
        )
    )


def downgrade() -> None:
    # Reverse description update (table is still named extractor_configs at this point)
    op.execute(
        sa.text(
            "UPDATE extractor_configs "
            "SET description = 'Parser por defecto para estados de cuenta bancarias mexicanas' "
            "WHERE description = "
            "'Extractor por defecto para estados de cuenta bancarias mexicanas'"
        )
    )

    if not _is_sqlite():
        # Drop new FK constraints (PostgreSQL only)
        op.drop_constraint(
            "api_call_logs_extractor_config_version_id_fkey",
            "api_call_logs",
            type_="foreignkey",
        )
        op.drop_constraint(
            "api_call_logs_extractor_config_id_fkey", "api_call_logs", type_="foreignkey"
        )
        op.drop_constraint(
            "extraction_logs_extractor_config_version_id_fkey",
            "extraction_logs",
            type_="foreignkey",
        )
        op.drop_constraint(
            "extraction_logs_extractor_config_id_fkey", "extraction_logs", type_="foreignkey"
        )
        op.drop_constraint(
            "extractor_config_versions_extractor_config_id_fkey",
            "extractor_config_versions",
            type_="foreignkey",
        )

    # Rename columns back in api_call_logs
    op.alter_column(
        "api_call_logs",
        "extractor_config_version_id",
        new_column_name="parser_config_version_id",
    )
    op.alter_column(
        "api_call_logs",
        "extractor_config_id",
        new_column_name="parser_config_id",
    )

    # Rename columns back in extraction_logs
    op.alter_column(
        "extraction_logs",
        "extractor_config_version_id",
        new_column_name="parser_config_version_id",
    )
    op.alter_column(
        "extraction_logs",
        "extractor_config_id",
        new_column_name="parser_config_id",
    )

    # Rename columns back in extractor_config_versions
    op.alter_column(
        "extractor_config_versions",
        "extractor_config_id",
        new_column_name="parser_config_id",
    )

    # Rename tables back
    op.rename_table("extractor_config_versions", "parser_config_versions")
    op.rename_table("extractor_configs", "parser_configs")

    if not _is_sqlite():
        # Re-create original FK constraints (PostgreSQL only)
        op.create_foreign_key(
            "parser_config_versions_parser_config_id_fkey",
            "parser_config_versions",
            "parser_configs",
            ["parser_config_id"],
            ["id"],
        )
        op.create_foreign_key(
            "extraction_logs_parser_config_id_fkey",
            "extraction_logs",
            "parser_configs",
            ["parser_config_id"],
            ["id"],
        )
        op.create_foreign_key(
            "extraction_logs_parser_config_version_id_fkey",
            "extraction_logs",
            "parser_config_versions",
            ["parser_config_version_id"],
            ["id"],
        )
        op.create_foreign_key(
            "api_call_logs_parser_config_id_fkey",
            "api_call_logs",
            "parser_configs",
            ["parser_config_id"],
            ["id"],
        )
        op.create_foreign_key(
            "api_call_logs_parser_config_version_id_fkey",
            "api_call_logs",
            "parser_config_versions",
            ["parser_config_version_id"],
            ["id"],
        )
