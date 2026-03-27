from src.domain.entities import ExtractorConfigData

DEFAULT_RECEIPT_EXTRACTOR = ExtractorConfigData(
    id=None,
    name="Boletas y recibos",
    description="Extrae información de boletas, recibos de compra y tickets de venta",
    prompt=(
        "Extrae la información de esta boleta o recibo de compra. "
        "Si algún campo no está presente en el documento, devuelve null para ese campo. "
        "Para los productos, extrae cada línea con su nombre, cantidad y precio unitario."
    ),
    model="claude-haiku-4-5-20251001",
    output_schema={
        "type": "object",
        "properties": {
            "comercio": {
                "type": "string",
                "description": "Nombre del comercio o negocio",
            },
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
                        "cantidad": {
                            "type": "number",
                            "description": "Cantidad comprada",
                        },
                        "precio_unitario": {
                            "type": "number",
                            "description": "Precio por unidad",
                        },
                    },
                    "required": ["nombre", "cantidad", "precio_unitario"],
                },
            },
            "subtotal": {
                "type": "number",
                "description": "Subtotal antes de impuestos",
            },
            "impuesto": {
                "type": "number",
                "description": "Monto del impuesto (IVA u otro)",
            },
            "total": {
                "type": "number",
                "description": "Total de la compra",
            },
            "metodo_pago": {
                "type": "string",
                "description": "Método de pago (efectivo, tarjeta, etc.)",
            },
        },
        "required": ["comercio", "fecha", "total"],
    },
    is_default=True,
    status="active",
)
