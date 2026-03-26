"""Documentation content for client-facing API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Param:
    name: str
    location: str  # "body", "query", "path", "header"
    type: str
    required: bool
    description: str


@dataclass
class CodeExample:
    language: str  # "curl", "python", "javascript"
    label: str
    code: str


@dataclass
class Endpoint:
    method: str
    path: str
    slug: str
    title: str
    description: str
    group: str
    params: list[Param] = field(default_factory=list)
    request_body: str = ""
    response_body: str = ""
    examples: list[CodeExample] = field(default_factory=list)
    notes: str = ""


API_BASE_PLACEHOLDER = "$$API_BASE$$"
API_BASE = API_BASE_PLACEHOLDER  # replaced at render time with actual request URL
TOKEN_PLACEHOLDER = "exto_tu_token_aqui"

GROUPS = [
    ("tokens", "Tokens"),
    ("extractors", "Extractores"),
    ("extraction", "Extraccion"),
]

ENDPOINTS: list[Endpoint] = [
    # ── Tokens ────────────────────────────────────────────────────────────
    Endpoint(
        method="POST",
        path="/tokens",
        slug="create-token",
        title="Crear token",
        group="tokens",
        description=(
            "Crea un nuevo token de API para autenticacion programatica. "
            "El token solo se muestra una vez en la respuesta; guardalo de forma segura."
        ),
        params=[
            Param("name", "body", "string", True, "Nombre descriptivo del token"),
            Param(
                "expires_at",
                "body",
                "string (ISO 8601)",
                False,
                "Fecha de expiracion (null = sin expiracion)",
            ),
        ],
        request_body="""\
{
  "name": "mi-app-produccion",
  "expires_at": "2026-12-31T23:59:59Z"
}""",
        response_body="""\
{
  "token": "exto_abc123...",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "mi-app-produccion",
  "expires_at": "2026-12-31T23:59:59Z"
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl -X POST {API_BASE}/tokens \\
  -H "Authorization: Bearer {{JWT_TOKEN}}" \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "mi-app-produccion"}}'""",
            ),
            CodeExample(
                "python",
                "Python",
                f"""\
import requests

resp = requests.post(
    "{API_BASE}/tokens",
    headers={{"Authorization": "Bearer {{JWT_TOKEN}}"}},
    json={{"name": "mi-app-produccion"}},
)
token = resp.json()["token"]
print(f"Guarda este token: {{token}}")""",
            ),
            CodeExample(
                "javascript",
                "JavaScript",
                f"""\
const resp = await fetch("{API_BASE}/tokens", {{
  method: "POST",
  headers: {{
    "Authorization": "Bearer {{JWT_TOKEN}}",
    "Content-Type": "application/json",
  }},
  body: JSON.stringify({{ name: "mi-app-produccion" }}),
}});
const {{ token }} = await resp.json();
console.log("Guarda este token:", token);""",
            ),
        ],
        notes=(
            "Los tokens se crean desde la interfaz web de Extracto en "
            "<strong>Configuracion &rarr; Tokens API</strong>. "
            "Este endpoint requiere autenticacion con JWT (sesion web), no con un API token. "
            "Los usuarios invitados no pueden crear tokens."
        ),
    ),
    Endpoint(
        method="GET",
        path="/tokens",
        slug="list-tokens",
        title="Listar tokens",
        group="tokens",
        description="Devuelve todos los tokens del usuario autenticado.",
        response_body="""\
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "mi-app-produccion",
    "created_at": "2026-01-15T10:30:00",
    "expires_at": "2026-12-31T23:59:59Z",
    "last_used_at": "2026-03-20T14:22:00",
    "is_revoked": false
  }
]""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl {API_BASE}/tokens \\
  -H "Authorization: Bearer {{JWT_TOKEN}}" """,
            ),
        ],
    ),
    Endpoint(
        method="DELETE",
        path="/tokens/{token_id}",
        slug="revoke-token",
        title="Revocar token",
        group="tokens",
        description=(
            "Revoca un token de API. Una vez revocado, no se puede usar para autenticarse."
        ),
        params=[
            Param("token_id", "path", "UUID", True, "ID del token a revocar"),
        ],
        response_body='{ "detail": "Token revocado" }',
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl -X DELETE {API_BASE}/tokens/550e8400-e29b-41d4-a716-446655440000 \\
  -H "Authorization: Bearer {{JWT_TOKEN}}" """,
            ),
        ],
    ),
    # ── Extractors ────────────────────────────────────────────────────────
    Endpoint(
        method="GET",
        path="/extractors",
        slug="list-extractors",
        title="Listar extractores",
        group="extractors",
        description=(
            "Devuelve los extractores configurados del usuario. "
            "Cada extractor define un prompt, modelo, y schema de salida."
        ),
        params=[
            Param("status", "query", "string", False, 'Filtrar por estado: "active" o "draft"'),
        ],
        response_body="""\
{
  "configs": [
    {
      "id": "a1b2c3d4-...",
      "name": "Boletas y recibos",
      "description": "Extrae datos de boletas",
      "prompt": "Extrae los campos...",
      "model": "claude-haiku-4-5-20251001",
      "output_schema": {
        "type": "object",
        "properties": {
          "titular": { "type": "string" },
          "monto": { "type": "string" }
        },
        "required": ["titular", "monto"]
      },
      "is_default": true,
      "status": "active",
      "created_at": "2026-01-01T00:00:00",
      "updated_at": "2026-01-15T12:00:00"
    }
  ]
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl {API_BASE}/extractors \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" """,
            ),
            CodeExample(
                "python",
                "Python",
                f"""\
import requests

resp = requests.get(
    "{API_BASE}/extractors",
    headers={{"Authorization": "Bearer {TOKEN_PLACEHOLDER}"}},
)
configs = resp.json()["configs"]
for c in configs:
    print(f"{{c['name']}} ({{c['id']}})")""",
            ),
            CodeExample(
                "javascript",
                "JavaScript",
                f"""\
const resp = await fetch("{API_BASE}/extractors", {{
  headers: {{ "Authorization": "Bearer {TOKEN_PLACEHOLDER}" }},
}});
const {{ configs }} = await resp.json();
configs.forEach(c => console.log(c.name, c.id));""",
            ),
        ],
    ),
    Endpoint(
        method="GET",
        path="/extractors/models",
        slug="list-models",
        title="Modelos disponibles",
        group="extractors",
        description="Devuelve la lista de modelos de IA disponibles para extraccion.",
        response_body="""\
[
  {
    "id": "claude-haiku-4-5-20251001",
    "name": "Claude Haiku 4.5",
    "tier": "fast",
    "cost_hint": "$0.80 / $4.00 por 1M tokens",
    "is_available": true
  }
]""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl {API_BASE}/extractors/models \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" """,
            ),
        ],
    ),
    Endpoint(
        method="GET",
        path="/extractors/{config_id}",
        slug="get-extractor",
        title="Obtener extractor",
        group="extractors",
        description="Devuelve los detalles de un extractor especifico por su ID.",
        params=[
            Param("config_id", "path", "UUID", True, "ID del extractor"),
        ],
        response_body="""\
{
  "id": "a1b2c3d4-...",
  "name": "Boletas y recibos",
  "description": "Extrae datos de boletas",
  "prompt": "Extrae los campos...",
  "model": "claude-haiku-4-5-20251001",
  "output_schema": { ... },
  "is_default": true,
  "status": "active",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-15T12:00:00"
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl {API_BASE}/extractors/a1b2c3d4-... \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" """,
            ),
        ],
    ),
    Endpoint(
        method="GET",
        path="/extractors/{config_id}/versions",
        slug="list-versions",
        title="Listar versiones",
        group="extractors",
        description=(
            "Devuelve las versiones de un extractor. Las versiones se crean automaticamente "
            "al editar un extractor y permiten A/B testing."
        ),
        params=[
            Param("config_id", "path", "UUID", True, "ID del extractor"),
        ],
        response_body="""\
[
  {
    "id": "v1-uuid-...",
    "version_number": 1,
    "prompt": "Prompt original...",
    "model": "claude-haiku-4-5-20251001",
    "output_schema": { ... },
    "is_active": false,
    "created_at": "2026-01-01T00:00:00"
  }
]""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl {API_BASE}/extractors/a1b2c3d4-.../versions \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" """,
            ),
        ],
    ),
    # ── Extraction ────────────────────────────────────────────────────────
    Endpoint(
        method="POST",
        path="/extraction/upload-url",
        slug="upload-url",
        title="Obtener URL de subida",
        group="extraction",
        description=(
            "Genera una URL pre-firmada de S3 para subir un archivo directamente desde el "
            "navegador o cliente. El archivo se sube con un PUT a la URL devuelta."
        ),
        params=[
            Param("filename", "body", "string", True, 'Nombre del archivo (ej: "factura.pdf")'),
            Param(
                "content_type",
                "body",
                "string",
                True,
                'MIME type (ej: "application/pdf", "image/jpeg")',
            ),
        ],
        request_body="""\
{
  "filename": "factura.pdf",
  "content_type": "application/pdf"
}""",
        response_body="""\
{
  "s3_key": "uploads/abc123-factura.pdf",
  "upload_url": "https://s3.amazonaws.com/bucket/uploads/abc123-factura.pdf?...",
  "filename": "factura.pdf"
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
# Paso 1: Obtener URL pre-firmada
curl -X POST {API_BASE}/extraction/upload-url \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" \\
  -H "Content-Type: application/json" \\
  -d '{{"filename": "factura.pdf", "content_type": "application/pdf"}}'

# Paso 2: Subir archivo a la URL devuelta
curl -X PUT "{{upload_url}}" \\
  -H "Content-Type: application/pdf" \\
  --data-binary @factura.pdf""",
            ),
            CodeExample(
                "python",
                "Python",
                f"""\
import requests

API = "{API_BASE}"
TOKEN = "{TOKEN_PLACEHOLDER}"
headers = {{"Authorization": f"Bearer {{TOKEN}}"}}

# Paso 1: Obtener URL pre-firmada
resp = requests.post(
    f"{{API}}/extraction/upload-url",
    headers=headers,
    json={{"filename": "factura.pdf", "content_type": "application/pdf"}},
)
data = resp.json()
s3_key = data["s3_key"]

# Paso 2: Subir archivo
with open("factura.pdf", "rb") as f:
    requests.put(data["upload_url"], data=f, headers={{"Content-Type": "application/pdf"}})

print(f"Archivo subido con clave: {{s3_key}}")""",
            ),
            CodeExample(
                "javascript",
                "JavaScript",
                f"""\
const API = "{API_BASE}";
const TOKEN = "{TOKEN_PLACEHOLDER}";

// Paso 1: Obtener URL pre-firmada
const urlResp = await fetch(`${{API}}/extraction/upload-url`, {{
  method: "POST",
  headers: {{
    "Authorization": `Bearer ${{TOKEN}}`,
    "Content-Type": "application/json",
  }},
  body: JSON.stringify({{
    filename: "factura.pdf",
    content_type: "application/pdf",
  }}),
}});
const {{ s3_key, upload_url }} = await urlResp.json();

// Paso 2: Subir archivo
await fetch(upload_url, {{
  method: "PUT",
  headers: {{ "Content-Type": "application/pdf" }},
  body: fileBlob, // File o Blob
}});

console.log("Archivo subido con clave:", s3_key);""",
            ),
        ],
    ),
    Endpoint(
        method="POST",
        path="/extraction/upload",
        slug="upload-file",
        title="Subir archivo (fallback)",
        group="extraction",
        description=(
            "Sube un archivo directamente al backend como multipart form-data. "
            "Usa este endpoint como fallback cuando las URLs pre-firmadas no esten disponibles."
        ),
        params=[
            Param("file", "body", "file (multipart)", True, "Archivo a subir"),
        ],
        request_body="(multipart/form-data con campo 'file')",
        response_body="""\
{
  "s3_key": "uploads/abc123-factura.pdf",
  "upload_url": null,
  "filename": "factura.pdf"
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl -X POST {API_BASE}/extraction/upload \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" \\
  -F "file=@factura.pdf" """,
            ),
            CodeExample(
                "python",
                "Python",
                f"""\
import requests

resp = requests.post(
    "{API_BASE}/extraction/upload",
    headers={{"Authorization": "Bearer {TOKEN_PLACEHOLDER}"}},
    files={{"file": open("factura.pdf", "rb")}},
)
s3_key = resp.json()["s3_key"]""",
            ),
        ],
    ),
    Endpoint(
        method="POST",
        path="/extraction/extract",
        slug="extract",
        title="Extraer campos",
        group="extraction",
        description=(
            "Ejecuta la extraccion de campos sobre un archivo previamente subido. "
            "Usa el prompt y schema del extractor especificado (o el extractor por defecto). "
            "Los campos extraidos son devueltos como un objeto JSON."
        ),
        params=[
            Param("s3_key", "body", "string", True, "Clave S3 del archivo (de upload-url/upload)"),
            Param("filename", "body", "string", True, "Nombre original del archivo"),
            Param(
                "extractor_config_id",
                "body",
                "UUID",
                False,
                "ID del extractor a usar (null = extractor por defecto)",
            ),
        ],
        request_body="""\
{
  "s3_key": "uploads/abc123-factura.pdf",
  "filename": "factura.pdf",
  "extractor_config_id": "a1b2c3d4-..."
}""",
        response_body="""\
{
  "fields": {
    "titular": "Juan Perez",
    "monto": "$1,500.00",
    "fecha": "2026-03-15"
  },
  "extractor_config_id": "a1b2c3d4-...",
  "extractor_config_name": "Boletas y recibos",
  "extractor_config_version_id": null,
  "extractor_config_version_number": null
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl -X POST {API_BASE}/extraction/extract \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "s3_key": "uploads/abc123-factura.pdf",
    "filename": "factura.pdf",
    "extractor_config_id": "a1b2c3d4-..."
  }}'""",
            ),
            CodeExample(
                "python",
                "Python",
                f"""\
import requests

resp = requests.post(
    "{API_BASE}/extraction/extract",
    headers={{
        "Authorization": "Bearer {TOKEN_PLACEHOLDER}",
        "Content-Type": "application/json",
    }},
    json={{
        "s3_key": s3_key,
        "filename": "factura.pdf",
        "extractor_config_id": "a1b2c3d4-...",
    }},
)
fields = resp.json()["fields"]
for key, value in fields.items():
    print(f"{{key}}: {{value}}")""",
            ),
            CodeExample(
                "javascript",
                "JavaScript",
                """\
const resp = await fetch(`${API}/extraction/extract`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    s3_key,
    filename: "factura.pdf",
    extractor_config_id: "a1b2c3d4-...",
  }),
});
const { fields } = await resp.json();
console.log(fields);""",
            ),
        ],
        notes=(
            "Si el documento no es compatible con el extractor, se devuelve un error 400. "
            "Las extracciones via API se registran en el dashboard del usuario dueno del token."
        ),
    ),
    Endpoint(
        method="POST",
        path="/extraction/submit",
        slug="submit",
        title="Enviar correccion",
        group="extraction",
        description=(
            "Registra el resultado final de una extraccion, incluyendo las correcciones "
            "del usuario. Esto alimenta las metricas de precision en el dashboard."
        ),
        params=[
            Param("filename", "body", "string", True, "Nombre del archivo"),
            Param(
                "extracted_fields",
                "body",
                "object",
                True,
                "Campos tal como fueron extraidos por la IA",
            ),
            Param(
                "final_fields",
                "body",
                "object",
                True,
                "Campos finales despues de correcciones del usuario",
            ),
            Param(
                "extractor_config_id",
                "body",
                "UUID",
                False,
                "ID del extractor usado",
            ),
            Param(
                "extractor_config_version_id",
                "body",
                "UUID",
                False,
                "ID de la version del extractor (si aplica)",
            ),
        ],
        request_body="""\
{
  "filename": "factura.pdf",
  "extracted_fields": {
    "titular": "Juan Peres",
    "monto": "$1,500.00"
  },
  "final_fields": {
    "titular": "Juan Perez",
    "monto": "$1,500.00"
  },
  "extractor_config_id": "a1b2c3d4-..."
}""",
        response_body="""\
{
  "message": "Submission recorded successfully",
  "id": "log-uuid-..."
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl -X POST {API_BASE}/extraction/submit \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "filename": "factura.pdf",
    "extracted_fields": {{"titular": "Juan Peres", "monto": "$1,500.00"}},
    "final_fields": {{"titular": "Juan Perez", "monto": "$1,500.00"}},
    "extractor_config_id": "a1b2c3d4-..."
  }}'""",
            ),
            CodeExample(
                "python",
                "Python",
                f"""\
import requests

resp = requests.post(
    "{API_BASE}/extraction/submit",
    headers={{
        "Authorization": "Bearer {TOKEN_PLACEHOLDER}",
        "Content-Type": "application/json",
    }},
    json={{
        "filename": "factura.pdf",
        "extracted_fields": {{"titular": "Juan Peres", "monto": "$1,500.00"}},
        "final_fields": {{"titular": "Juan Perez", "monto": "$1,500.00"}},
        "extractor_config_id": "a1b2c3d4-...",
    }},
)
print(resp.json())""",
            ),
        ],
        notes=(
            "El sistema compara <code>extracted_fields</code> con <code>final_fields</code> "
            "para determinar que campos fueron corregidos. Esto se usa para calcular la "
            "precision del extractor en el dashboard."
        ),
    ),
    Endpoint(
        method="GET",
        path="/extraction/banks",
        slug="banks",
        title="Listar bancos",
        group="extraction",
        description="Devuelve la lista de bancos mexicanos soportados (nombre y codigo).",
        response_body="""\
{
  "banks": [
    { "name": "BBVA", "code": "012" },
    { "name": "Banorte", "code": "072" },
    ...
  ]
}""",
        examples=[
            CodeExample(
                "curl",
                "cURL",
                f"""\
curl {API_BASE}/extraction/banks \\
  -H "Authorization: Bearer {TOKEN_PLACEHOLDER}" """,
            ),
        ],
    ),
]


def get_endpoints_by_group() -> list[tuple[str, str, list[Endpoint]]]:
    """Return [(group_id, group_label, endpoints)] in display order."""
    result = []
    for gid, glabel in GROUPS:
        eps = [e for e in ENDPOINTS if e.group == gid]
        if eps:
            result.append((gid, glabel, eps))
    return result
