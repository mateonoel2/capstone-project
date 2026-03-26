"""Add default receipt extractor for existing users without extractors

Revision ID: n4i5j6k7l8m9
Revises: m3h4i5j6k7l8
Create Date: 2026-03-25
"""

import json

from sqlalchemy import text

from alembic import op

revision = "n4i5j6k7l8m9"
down_revision = "m3h4i5j6k7l8"
branch_labels = None
depends_on = None

DEFAULT_RECEIPT_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "comercio": {"type": "string", "description": "Nombre del comercio o negocio"},
            "fecha": {
                "type": "string",
                "description": "Fecha de la compra (formato YYYY-MM-DD)",
            },
            "productos": {
                "type": "array",
                "description": "Lista de productos o servicios",
                "items": {
                    "type": "object",
                    "properties": {
                        "nombre": {
                            "type": "string",
                            "description": "Nombre del producto o servicio",
                        },
                        "cantidad": {"type": "number", "description": "Cantidad comprada"},
                        "precio_unitario": {
                            "type": "number",
                            "description": "Precio por unidad",
                        },
                    },
                    "required": ["nombre", "cantidad", "precio_unitario"],
                },
            },
            "subtotal": {"type": "number", "description": "Subtotal antes de impuestos"},
            "impuesto": {
                "type": "number",
                "description": "Monto del impuesto (IVA u otro)",
            },
            "total": {"type": "number", "description": "Total de la compra"},
            "metodo_pago": {
                "type": "string",
                "description": "Método de pago (efectivo, tarjeta, etc.)",
            },
        },
        "required": ["comercio", "fecha", "total"],
    }
)

DEFAULT_PROMPT = (
    "Extrae la información de esta boleta o recibo de compra. "
    "Si algún campo no está presente en el documento, devuelve null para ese campo. "
    "Para los productos, extrae cada línea con su nombre, cantidad y precio unitario."
)


def upgrade() -> None:
    conn = op.get_bind()
    # Find users that have no extractor configs
    users_without_extractors = conn.execute(
        text("""
            SELECT u.id FROM users u
            WHERE NOT EXISTS (
                SELECT 1 FROM extractor_configs ec WHERE ec.user_id = u.id
            )
        """)
    ).fetchall()

    for (user_id,) in users_without_extractors:
        conn.execute(
            text("""
                INSERT INTO extractor_configs
                    (name, description, prompt, model, output_schema, is_default, status, user_id,
                     created_at, updated_at)
                VALUES
                    ('Boletas y recibos',
                     'Extrae información de boletas, recibos de compra y tickets de venta',
                     :prompt, 'claude-haiku-4-5-20251001', :schema,
                     true, 'active', :user_id, NOW(), NOW())
            """),
            {"prompt": DEFAULT_PROMPT, "schema": DEFAULT_RECEIPT_SCHEMA, "user_id": user_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("""
            DELETE FROM extractor_configs
            WHERE name = 'Boletas y recibos'
            AND NOT EXISTS (
                SELECT 1 FROM extraction_logs el WHERE el.extractor_config_id = extractor_configs.id
            )
        """)
    )
