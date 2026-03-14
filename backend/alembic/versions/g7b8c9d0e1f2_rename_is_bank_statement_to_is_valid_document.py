"""Rename is_bank_statement to is_valid_document in default extractor schema and prompt

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-03-14
"""

import json
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Update all extractor configs: rename is_bank_statement -> is_valid_document in output_schema
    rows = conn.execute(
        sa.text("SELECT id, output_schema, prompt FROM extractor_configs")
    ).fetchall()

    for row in rows:
        config_id, schema_json, prompt = row
        updated = False

        # Update output_schema JSON
        if schema_json:
            try:
                schema = json.loads(schema_json)
                props = schema.get("properties", {})
                if "is_bank_statement" in props:
                    props["is_valid_document"] = props.pop("is_bank_statement")
                    # Update required array
                    req = schema.get("required", [])
                    schema["required"] = [
                        "is_valid_document" if r == "is_bank_statement" else r for r in req
                    ]
                    schema_json = json.dumps(schema)
                    updated = True
            except (json.JSONDecodeError, TypeError):
                pass

        # Update prompt text
        new_prompt = prompt
        if prompt and "is_bank_statement" in prompt:
            new_prompt = prompt.replace("is_bank_statement", "is_valid_document")
            updated = True

        if updated:
            conn.execute(
                sa.text(
                    "UPDATE extractor_configs SET output_schema = :schema, prompt = :prompt "
                    "WHERE id = :id"
                ),
                {"schema": schema_json, "prompt": new_prompt, "id": config_id},
            )


def downgrade() -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT id, output_schema, prompt FROM extractor_configs")
    ).fetchall()

    for row in rows:
        config_id, schema_json, prompt = row
        updated = False

        if schema_json:
            try:
                schema = json.loads(schema_json)
                props = schema.get("properties", {})
                if "is_valid_document" in props:
                    props["is_bank_statement"] = props.pop("is_valid_document")
                    req = schema.get("required", [])
                    schema["required"] = [
                        "is_bank_statement" if r == "is_valid_document" else r for r in req
                    ]
                    schema_json = json.dumps(schema)
                    updated = True
            except (json.JSONDecodeError, TypeError):
                pass

        new_prompt = prompt
        if prompt and "is_valid_document" in prompt:
            new_prompt = prompt.replace("is_valid_document", "is_bank_statement")
            updated = True

        if updated:
            conn.execute(
                sa.text(
                    "UPDATE extractor_configs SET output_schema = :schema, prompt = :prompt "
                    "WHERE id = :id"
                ),
                {"schema": schema_json, "prompt": new_prompt, "id": config_id},
            )
