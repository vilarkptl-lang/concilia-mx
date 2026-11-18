"""Ledger: partida doble + doble libro (interno / fiscal).

Invariantes DUROS (no son opcionales):
  - cada renglón tiene debe XOR haber (nunca ambos), nunca negativos;
  - el asiento cuadra (Σdebe == Σhaber) y es > 0.
Si no se cumplen, `validar()` lanza ValueError. El resto del motor construye
asientos SOLO a través de estas clases, así la partida doble se garantiza una vez.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from .money import money

LIBRO_INTERNO = "interno"
LIBRO_FISCAL = "fiscal"


@dataclass
class Renglon:
    cuenta: str                       # código de cuenta del catálogo
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    descripcion: str = ""

    def __post_init__(self):
        self.debit = money(self.debit)
        self.credit = money(self.credit)


@dataclass
class Asiento:
    fecha: str                        # YYYY-MM-DD
    descripcion: str
    renglones: List[Renglon]
    libro: str = LIBRO_INTERNO
    referencia: str = ""              # llave natural / idempotencia / evidencia
    origen: str = "manual"            # banco | cfdi | reconocimiento | manual

    def total_debe(self) -> Decimal:
        return money(sum((r.debit for r in self.renglones), Decimal("0")))

    def total_haber(self) -> Decimal:
        return money(sum((r.credit for r in self.renglones), Decimal("0")))

    def cuadra(self) -> bool:
        return self.total_debe() == self.total_haber() and self.total_debe() > 0

    def validar(self) -> bool:
        for r in self.renglones:
            if r.debit > 0 and r.credit > 0:
                raise ValueError(
                    f"Renglón {r.cuenta}: no puede tener debe y haber a la vez.")
            if r.debit < 0 or r.credit < 0:
                raise ValueError(f"Renglón {r.cuenta}: montos negativos no permitidos.")
        if not self.cuadra():
            raise ValueError(
                f"Partida doble no cuadra: debe {self.total_debe()} != "
                f"haber {self.total_haber()}.")
        return True
