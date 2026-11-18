"""Ingest de órdenes de compra / pagos a proveedores (CSV).
Sirven de COGS para el estimador de costo de reclasificación y para clasificar egresos.
Columnas: proveedor, fecha, monto, con_iva, referencia."""
import csv
from dataclasses import dataclass
from decimal import Decimal
from typing import List

from ..money import money


@dataclass
class OrdenCompra:
    proveedor: str
    fecha: str
    monto: Decimal
    con_iva: bool = True
    referencia: str = ""


def parse_csv(path: str) -> List[OrdenCompra]:
    out: List[OrdenCompra] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip().lower(): v for k, v in row.items()}
            con_iva = str(row.get("con_iva", "true")).strip().lower() in ("1", "true", "si", "sí")
            out.append(OrdenCompra(
                proveedor=(row.get("proveedor") or "").strip(),
                fecha=(row.get("fecha") or "").strip(),
                monto=money(row.get("monto")),
                con_iva=con_iva,
                referencia=(row.get("referencia") or "").strip(),
            ))
    return out
