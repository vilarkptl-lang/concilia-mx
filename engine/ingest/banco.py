"""Ingest de estado de cuenta bancario (CSV genérico).

Columnas esperadas (encabezados, en minúsculas): fecha, descripcion, deposito,
retiro, referencia. El banco es la fuente MÁS fehaciente de la fecha real del
movimiento. No se asume nada del "Concepto": la clasificación va aparte (clasificacion.py).
"""
import csv
from dataclasses import dataclass
from decimal import Decimal
from typing import List

from ..money import money


@dataclass
class MovBanco:
    fecha: str
    descripcion: str
    deposito: Decimal
    retiro: Decimal
    referencia: str = ""
    id: str = ""

    @property
    def es_deposito(self) -> bool:
        return self.deposito > 0


def parse_csv(path: str) -> List[MovBanco]:
    movs: List[MovBanco] = []
    with open(path, newline="", encoding="utf-8") as f:
        for n, row in enumerate(csv.DictReader(f), 1):
            row = {(k or "").strip().lower(): v for k, v in row.items()}
            movs.append(MovBanco(
                fecha=(row.get("fecha") or "").strip(),
                descripcion=(row.get("descripcion") or "").strip(),
                deposito=money(row.get("deposito")),
                retiro=money(row.get("retiro")),
                referencia=(row.get("referencia") or "").strip(),
                id=(row.get("id") or f"mov-{n}"),
            ))
    return movs
