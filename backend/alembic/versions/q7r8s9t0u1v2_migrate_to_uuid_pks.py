"""Migrate all tables from Integer PKs to UUID PKs.

Revision ID: q7r8s9t0u1v2
Revises: p6q7r8s9t0u1
Create Date: 2026-03-25 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "q7r8s9t0u1v2"
down_revision = "p6q7r8s9t0u1"
branch_labels = None
depends_on = None

# All tables that need PK migration
ALL_TABLES = [
    "users",
    "api_tokens",
    "extractor_configs",
    "extractor_config_versions",
    "extraction_logs",
    "test_extraction_logs",
    "api_call_logs",
    "ai_usage_logs",
    "audit_logs",
    "data_consents",
]

# FK relationships: (child_table, fk_column, parent_table, parent_column, nullable, ondelete)
FK_RELATIONSHIPS = [
    ("api_tokens", "user_id", "users", "id", False, "CASCADE"),
    ("extractor_configs", "user_id", "users", "id", True, None),
    ("extractor_config_versions", "extractor_config_id", "extractor_configs", "id", False, None),
    ("extraction_logs", "user_id", "users", "id", True, None),
    ("extraction_logs", "extractor_config_id", "extractor_configs", "id", True, None),
    (
        "extraction_logs",
        "extractor_config_version_id",
        "extractor_config_versions",
        "id",
        True,
        None,
    ),
    ("test_extraction_logs", "user_id", "users", "id", True, None),
    ("test_extraction_logs", "extractor_config_id", "extractor_configs", "id", True, "SET NULL"),
    ("api_call_logs", "user_id", "users", "id", True, None),
    ("api_call_logs", "extractor_config_id", "extractor_configs", "id", True, None),
    (
        "api_call_logs",
        "extractor_config_version_id",
        "extractor_config_versions",
        "id",
        True,
        None,
    ),
    ("ai_usage_logs", "user_id", "users", "id", False, None),
    ("audit_logs", "user_id", "users", "id", True, None),
    ("data_consents", "user_id", "users", "id", False, "CASCADE"),
]


def upgrade() -> None:
    # Ensure gen_random_uuid() is available
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    # =========================================================================
    # Step 1: Add new UUID columns for all PKs and FKs
    # =========================================================================

    for table in ALL_TABLES:
        op.add_column(table, sa.Column("new_id", UUID(as_uuid=True), nullable=True))

    for child_table, fk_col, _parent, _pcol, _nullable, _ondelete in FK_RELATIONSHIPS:
        op.add_column(child_table, sa.Column(f"new_{fk_col}", UUID(as_uuid=True), nullable=True))

    # =========================================================================
    # Step 2: Populate new PK UUID columns
    # =========================================================================

    for table in ALL_TABLES:
        op.execute(sa.text(f"UPDATE {table} SET new_id = gen_random_uuid() WHERE new_id IS NULL"))

    # =========================================================================
    # Step 3: Backfill FK UUID columns via JOINs (dependency order)
    # =========================================================================

    for parent in ("users", "extractor_configs", "extractor_config_versions"):
        alias = {"users": "u", "extractor_configs": "ec", "extractor_config_versions": "ecv"}[
            parent
        ]
        for child_table, fk_col, parent_table, _pcol, _nullable, _ondelete in FK_RELATIONSHIPS:
            if parent_table == parent:
                op.execute(
                    sa.text(
                        f"UPDATE {child_table} SET new_{fk_col} = {alias}.new_id "
                        f"FROM {parent} {alias} "
                        f"WHERE {child_table}.{fk_col} = {alias}.id"
                    )
                )

    # =========================================================================
    # Step 4: Drop old FK constraints
    # =========================================================================

    # Actual constraint names from the database (some use fk_ prefix from older migrations)
    fk_constraints = [
        ("api_tokens", "api_tokens_user_id_fkey"),
        ("extractor_configs", "fk_extractor_configs_user_id"),
        ("extractor_config_versions", "extractor_config_versions_extractor_config_id_fkey"),
        ("extraction_logs", "fk_extraction_logs_user_id"),
        ("extraction_logs", "extraction_logs_extractor_config_id_fkey"),
        ("extraction_logs", "extraction_logs_extractor_config_version_id_fkey"),
        ("test_extraction_logs", "fk_test_extraction_logs_user_id"),
        ("test_extraction_logs", "test_extraction_logs_extractor_config_id_fkey"),
        ("api_call_logs", "fk_api_call_logs_user_id"),
        ("api_call_logs", "api_call_logs_extractor_config_id_fkey"),
        ("api_call_logs", "api_call_logs_extractor_config_version_id_fkey"),
        ("ai_usage_logs", "ai_usage_logs_user_id_fkey"),
        ("audit_logs", "audit_logs_user_id_fkey"),
        ("data_consents", "data_consents_user_id_fkey"),
    ]
    for table, constraint in fk_constraints:
        op.drop_constraint(constraint, table, type_="foreignkey")

    # =========================================================================
    # Step 5: Drop unique constraints that reference old columns
    # =========================================================================

    op.drop_constraint("uq_extractor_configs_name_user", "extractor_configs", type_="unique")

    # =========================================================================
    # Step 6: Drop old PK constraints and indexes
    # =========================================================================

    # Actual PK constraint names (some kept old parser_ prefix from rename migration)
    pk_constraints = {
        "users": "users_pkey",
        "api_tokens": "api_tokens_pkey",
        "extractor_configs": "parser_configs_pkey",
        "extractor_config_versions": "parser_config_versions_pkey",
        "extraction_logs": "extraction_logs_pkey",
        "test_extraction_logs": "test_extraction_logs_pkey",
        "api_call_logs": "api_call_logs_pkey",
        "ai_usage_logs": "ai_usage_logs_pkey",
        "audit_logs": "audit_logs_pkey",
        "data_consents": "data_consents_pkey",
    }
    for table in ALL_TABLES:
        op.drop_constraint(pk_constraints[table], table, type_="primary")

    # Actual index names (some kept old parser_ prefix)
    indexes_to_drop = [
        ("ix_api_tokens_user_id", "api_tokens"),
        ("ix_ai_usage_logs_user_id", "ai_usage_logs"),
        ("ix_audit_logs_user_id", "audit_logs"),
        ("ix_audit_logs_timestamp", "audit_logs"),
        ("ix_parser_configs_id", "extractor_configs"),
        ("ix_parser_config_versions_id", "extractor_config_versions"),
        ("ix_extraction_logs_id", "extraction_logs"),
        ("ix_test_extraction_logs_id", "test_extraction_logs"),
        ("ix_api_call_logs_id", "api_call_logs"),
    ]
    for idx_name, table in indexes_to_drop:
        op.drop_index(idx_name, table_name=table)

    # =========================================================================
    # Step 7: Drop old integer columns
    # =========================================================================

    for child_table, fk_col, _parent, _pcol, _nullable, _ondelete in FK_RELATIONSHIPS:
        op.drop_column(child_table, fk_col)

    for table in ALL_TABLES:
        op.drop_column(table, "id")

    # =========================================================================
    # Step 8: Rename new UUID columns to original names
    # =========================================================================

    for table in ALL_TABLES:
        op.alter_column(table, "new_id", new_column_name="id", nullable=False)

    for child_table, fk_col, _parent, _pcol, nullable, _ondelete in FK_RELATIONSHIPS:
        op.alter_column(child_table, f"new_{fk_col}", new_column_name=fk_col, nullable=nullable)

    # =========================================================================
    # Step 9: Recreate PK constraints
    # =========================================================================

    for table in ALL_TABLES:
        op.create_primary_key(f"{table}_pkey", table, ["id"])

    # =========================================================================
    # Step 10: Recreate FK constraints
    # =========================================================================

    for child_table, fk_col, parent_table, pcol, _nullable, ondelete in FK_RELATIONSHIPS:
        kwargs = {}
        if ondelete:
            kwargs["ondelete"] = ondelete
        op.create_foreign_key(
            f"{child_table}_{fk_col}_fkey",
            child_table,
            parent_table,
            [fk_col],
            [pcol],
            **kwargs,
        )

    # =========================================================================
    # Step 11: Recreate indexes and unique constraints
    # =========================================================================

    for idx_name, table in [
        ("ix_extractor_configs_id", "extractor_configs"),
        ("ix_extractor_config_versions_id", "extractor_config_versions"),
        ("ix_extraction_logs_id", "extraction_logs"),
        ("ix_test_extraction_logs_id", "test_extraction_logs"),
        ("ix_api_call_logs_id", "api_call_logs"),
    ]:
        op.create_index(idx_name, table, ["id"])

    for idx_name, table, col in [
        ("ix_api_tokens_user_id", "api_tokens", "user_id"),
        ("ix_ai_usage_logs_user_id", "ai_usage_logs", "user_id"),
        ("ix_audit_logs_user_id", "audit_logs", "user_id"),
        ("ix_audit_logs_timestamp", "audit_logs", "timestamp"),
    ]:
        op.create_index(idx_name, table, [col])

    op.create_unique_constraint(
        "uq_extractor_configs_name_user", "extractor_configs", ["name", "user_id"]
    )

    # =========================================================================
    # Step 12: Drop leftover sequences from old integer PKs
    # =========================================================================

    for table in ALL_TABLES:
        op.execute(sa.text(f"DROP SEQUENCE IF EXISTS {table}_id_seq CASCADE"))


def downgrade() -> None:
    # This migration is irreversible due to data type change from Integer to UUID.
    pass
