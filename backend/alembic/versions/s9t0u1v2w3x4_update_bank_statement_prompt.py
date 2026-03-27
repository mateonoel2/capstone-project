"""Update default bank statement prompt with improved CLABE instructions.

Revision ID: s9t0u1v2w3x4
Revises: r8s9t0u1v2w3
Create Date: 2026-03-27 01:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "s9t0u1v2w3x4"
down_revision = "r8s9t0u1v2w3"
branch_labels = None
depends_on = None

NEW_PROMPT = """\
Analiza este documento y determina si es un estado de
cuenta o carátula bancaria mexicana.

Si ES un estado de cuenta o carátula bancaria, extrae:

1. Titular/Owner: Nombre completo del titular de la cuenta (persona o empresa).
   Busca el nombre que aparece en la sección de datos del cliente, NO el nombre
   del asesor, ejecutivo, o personas mencionadas en transacciones.

2. CLABE Interbancaria: Número de EXACTAMENTE 18 dígitos.
   IMPORTANTE — Distingue entre estos campos que son DIFERENTES:
   - CLABE Interbancaria: SIEMPRE tiene 18 dígitos. Busca etiquetas como
     "CLABE", "CLABE Interbancaria", "No. Cuenta CLABE", "Cuenta CLABE".
   - Número de cuenta: Típicamente 10-11 dígitos. NO es la CLABE.
   - Número de cliente: Típicamente 7-8 dígitos. NO es la CLABE.
   La CLABE aparece inmediatamente al costado o debajo de su etiqueta
   "CLABE Interbancaria". Lee el número que está junto a esa etiqueta.

   FORMATOS COMUNES en que aparece la CLABE en documentos:
   - Con espacios cada 3 dígitos: "014 027 001 234 567 890"
   - Con espacios irregulares: "014 027 00123456789 0"
   - Sin espacios: "014027001234567890"
   - Con guiones: "014-027-001234567890"
   Elimina todos los espacios/guiones y devuelve SOLO los 18 dígitos consecutivos.

   Lee cada dígito individualmente de izquierda a derecha con cuidado.
   No agrupes, no asumas, no reordenes dígitos.
   Si ves la CLABE en la sección "PRODUCTOS DE VISTA" o "RESUMEN INTEGRAL",
   usa ese valor.

3. Banco: Nombre del banco (debe ser uno de: BBVA MEXICO, SANTANDER, BANAMEX,
   BANORTE, HSBC, SCOTIABANK, AFIRME, BAJIO, BANREGIO, MIFEL, BMONEX, INBURSA)

Si NO es un estado de cuenta bancario (por ejemplo: facturas, contratos, recibos,
comprobantes de transferencia, documentos legales, etc.), marca is_valid_document
como false.

Si no encuentras algún campo, usa "Unknown" para owner y bank_name,
y "000000000000000000" para account_number.
NO inventes información. Solo extrae lo que está claramente visible en el documento."""


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE extractor_configs SET prompt = :prompt "
            "WHERE postprocessor = 'mexican_bank_statement'"
        ).bindparams(prompt=NEW_PROMPT)
    )


def downgrade() -> None:
    pass
