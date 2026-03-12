"""Update default extractor prompt to handle CLABE with spaces

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-03-11
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PROMPT = """Analiza este documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:
1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa)
2. CLABE: Número de 18 dígitos (CLABE interbancaria).
   La CLABE puede aparecer con espacios entre grupos de dígitos
   (ej: "072 691 00844421773 3"). Elimina todos los espacios y devuelve
   solo los 18 dígitos consecutivos.
3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos, documentos
legales, etc.), marca is_bank_statement como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""

OLD_PROMPT = """Analiza esta imagen de un documento y determina si es un estado de
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

import json

NEW_SCHEMA = json.dumps(
    {
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
                    "Número CLABE de 18 dígitos sin espacios. "
                    "Si aparece con espacios, elimínalos. "
                    "Usa '000000000000000000' si no se encuentra."
                ),
            },
            "bank_name": {
                "type": "string",
                "description": (
                    "Nombre del banco en mayúsculas. Usa 'Unknown' si no se encuentra."
                ),
            },
        },
        "required": ["is_bank_statement", "owner", "account_number", "bank_name"],
    }
)

OLD_SCHEMA = json.dumps(
    {
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
                "description": (
                    "Nombre del banco en mayúsculas. Usa 'Unknown' si no se encuentra."
                ),
            },
        },
        "required": ["is_bank_statement", "owner", "account_number", "bank_name"],
    }
)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE extractor_configs "
            "SET prompt = :new_prompt, output_schema = :new_schema "
            "WHERE is_default = true"
        ),
        {"new_prompt": NEW_PROMPT, "new_schema": NEW_SCHEMA},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE extractor_configs "
            "SET prompt = :old_prompt, output_schema = :old_schema "
            "WHERE is_default = true"
        ),
        {"old_prompt": OLD_PROMPT, "old_schema": OLD_SCHEMA},
    )
