"""add parser_configs and parser_config_versions tables

Revision ID: a1b2c3d4e5f6
Revises: 934e52b9a9b3
Create Date: 2026-03-04 22:00:00.000000

"""

import json
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "934e52b9a9b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_PROMPT = """Analiza esta imagen de un documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:
1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa)
2. CLABE: Número de 18 dígitos (CLABE interbancaria).
   IMPORTANTE: debe ser exactamente 18 dígitos numéricos consecutivos.
3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos, documentos
legales, etc.), marca is_bank_statement como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""

DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        "is_bank_statement": {
            "type": "boolean",
            "description": (
                "True si el documento es un estado de cuenta o carátula bancaria mexicana, "
                "False si es otro tipo de documento"
            ),
        },
        "owner": {
            "type": "string",
            "description": (
                "Nombre completo del titular de la cuenta. Usa 'Unknown' si no se encuentra."
            ),
        },
        "account_number": {
            "type": "string",
            "description": (
                "Número CLABE de 18 dígitos. Usa '000000000000000000' si no se encuentra."
            ),
        },
        "bank_name": {
            "type": "string",
            "description": "Nombre del banco en mayúsculas. Usa 'Unknown' si no se encuentra.",
        },
    },
    "required": ["is_bank_statement", "owner", "account_number", "bank_name"],
}


def upgrade() -> None:
    # Create parser_configs table
    op.create_table(
        "parser_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column(
            "model", sa.String(100), nullable=False, server_default="claude-haiku-4-5-20251001"
        ),
        sa.Column("output_schema", sa.JSON(), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_parser_configs_id"), "parser_configs", ["id"], unique=False)

    # Create parser_config_versions table
    op.create_table(
        "parser_config_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parser_config_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("output_schema", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["parser_config_id"], ["parser_configs.id"]),
    )
    op.create_index(
        op.f("ix_parser_config_versions_id"), "parser_config_versions", ["id"], unique=False
    )

    # Add parser_config_id to extraction_logs and api_call_logs
    # Use nullable Integer without FK constraint for SQLite compatibility
    op.add_column(
        "extraction_logs",
        sa.Column("parser_config_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "api_call_logs",
        sa.Column("parser_config_id", sa.Integer(), nullable=True),
    )

    # Seed the default bank statement parser config
    parser_configs = sa.table(
        "parser_configs",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("prompt", sa.Text),
        sa.column("model", sa.String),
        sa.column("output_schema", sa.JSON),
        sa.column("is_default", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    now = datetime.now(timezone.utc)
    # For SQLite, JSON must be stored as string; for PostgreSQL, as dict
    dialect = op.get_bind().dialect.name
    schema_value = json.dumps(DEFAULT_SCHEMA) if dialect == "sqlite" else DEFAULT_SCHEMA
    op.bulk_insert(
        parser_configs,
        [
            {
                "name": "Estado de Cuenta Bancario",
                "description": "Parser por defecto para estados de cuenta bancarias mexicanas",
                "prompt": DEFAULT_PROMPT,
                "model": "claude-haiku-4-5-20251001",
                "output_schema": schema_value,
                "is_default": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.drop_column("api_call_logs", "parser_config_id")
    op.drop_column("extraction_logs", "parser_config_id")
    op.drop_index(op.f("ix_parser_config_versions_id"), table_name="parser_config_versions")
    op.drop_table("parser_config_versions")
    op.drop_index(op.f("ix_parser_configs_id"), table_name="parser_configs")
    op.drop_table("parser_configs")
