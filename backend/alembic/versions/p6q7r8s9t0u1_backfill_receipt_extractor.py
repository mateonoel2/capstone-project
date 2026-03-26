"""Backfill receipt extractor for users missing it

Revision ID: p6q7r8s9t0u1
Revises: o5p6q7r8s9t0
Create Date: 2026-03-25
"""

import json

from sqlalchemy import text

from alembic import op

revision = "p6q7r8s9t0u1"
down_revision = "o5p6q7r8s9t0"
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
    # Find users that don't have a "Boletas y recibos" extractor
    users_missing = conn.execute(
        text("""
            SELECT u.id FROM users u
            WHERE NOT EXISTS (
                SELECT 1 FROM extractor_configs ec
                WHERE ec.user_id = u.id
                AND ec.name = 'Boletas y recibos'
            )
        """)
    ).fetchall()

    for (user_id,) in users_missing:
        # Check if user already has a default extractor
        has_default = conn.execute(
            text("""
                SELECT 1 FROM extractor_configs
                WHERE user_id = :user_id AND is_default = true
                LIMIT 1
            """),
            {"user_id": user_id},
        ).fetchone()

        conn.execute(
            text("""
                INSERT INTO extractor_configs
                    (name, description, prompt, model, output_schema, is_default, status, user_id,
                     created_at, updated_at)
                VALUES
                    ('Boletas y recibos',
                     'Extrae información de boletas, recibos de compra y tickets de venta',
                     :prompt, 'claude-haiku-4-5-20251001', :schema,
                     :is_default, 'active', :user_id, NOW(), NOW())
            """),
            {
                "prompt": DEFAULT_PROMPT,
                "schema": DEFAULT_RECEIPT_SCHEMA,
                "user_id": user_id,
                "is_default": not has_default,
            },
        )


def downgrade() -> None:
    pass
