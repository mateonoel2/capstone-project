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

NEW_ACCOUNT_DESC = (
    "Número CLABE de 18 dígitos sin espacios. "
    "Si aparece con espacios, elimínalos. Usa '000000000000000000' si no se encuentra."
)
OLD_ACCOUNT_DESC = "Número CLABE de 18 dígitos. Usa '000000000000000000' si no se encuentra."


def upgrade() -> None:
    conn = op.get_bind()

    # Update prompt
    conn.execute(
        sa.text("UPDATE extractor_configs SET prompt = :new_prompt WHERE is_default = true"),
        {"new_prompt": NEW_PROMPT},
    )

    # Update output_schema account_number description
    conn.execute(
        sa.text(
            "UPDATE extractor_configs "
            "SET output_schema = jsonb_set("
            "  output_schema, "
            "  '{properties,account_number,description}', "
            "  :new_desc::jsonb"
            ") "
            "WHERE is_default = true"
        ),
        {"new_desc": f'"{NEW_ACCOUNT_DESC}"'},
    )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text("UPDATE extractor_configs SET prompt = :old_prompt WHERE is_default = true"),
        {"old_prompt": OLD_PROMPT},
    )

    conn.execute(
        sa.text(
            "UPDATE extractor_configs "
            "SET output_schema = jsonb_set("
            "  output_schema, "
            "  '{properties,account_number,description}', "
            "  :old_desc::jsonb"
            ") "
            "WHERE is_default = true"
        ),
        {"old_desc": f'"{OLD_ACCOUNT_DESC}"'},
    )
