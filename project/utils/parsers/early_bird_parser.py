from dataclasses import dataclass
from typing import List
import json


@dataclass
class DescuentoInfo:
    name: str  # Nombre del descuento
    up_to_days: int  # Número de días antes de la fecha límite de pago
    discount_type: str  # AMOUNT o PERCENT
    discount_value: float  # Valor del descuento


def parse_descuentos(json_data: str) -> List[DescuentoInfo]:
    descuentos_list = json.loads(json_data)
    descuentos = []
    for descuento in descuentos_list:
        descuento_info = DescuentoInfo(
            name=descuento["name"],
            up_to_days=descuento["up_to_days"],
            discount_type=descuento["discount_type"],
            discount_value=descuento["discount_value"],
        )
        descuentos.append(descuento_info)
    return descuentos


def describe_descuento(descuento: DescuentoInfo) -> str:
    type_map = {"AMOUNT": "un descuento fijo de", "PERCENT": "un descuento del"}
    type_desc = type_map.get(descuento.discount_type, descuento.discount_type.lower())

    if descuento.up_to_days > 0:
        days_desc = f"si el pago se realiza hasta {descuento.up_to_days} días antes de la fecha límite"
    else:
        days_desc = "si el pago se realiza antes de la fecha límite"

    if descuento.discount_type == "PERCENT":
        description = (
            f"{descuento.name}: {type_desc} {descuento.discount_value}% {days_desc}."
        )
    else:
        description = (
            f"{descuento.name}: {type_desc} ${descuento.discount_value} {days_desc}."
        )

    return description


def generate_descriptions(descuentos: List[DescuentoInfo]) -> List[str]:
    descriptions = []
    for descuento in descuentos:
        description = describe_descuento(descuento)
        descriptions.append(description)
    return descriptions


if __name__ == "__main__":

    json_data = """
    [
        {
            "name": "Descuento 20% antes del día 5",
            "up_to_days": 25,
            "discount_type": "PERCENT",
            "discount_value": 20
        },
        {
            "name": "Descuento 5% antes del día 10",
            "up_to_days": 20,
            "discount_type": "PERCENT",
            "discount_value": 5
        }
    ]
    """

    descuentos = parse_descuentos(json_data)

    descriptions = generate_descriptions(descuentos)

    for desc in descriptions:
        print(desc)
