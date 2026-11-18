"""Dinero = Decimal a 2 decimales, redondeo half-up. Nunca float para montos."""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(x) -> Decimal:
    """Normaliza cualquier entrada numérica/str a Decimal con 2 decimales."""
    if x is None or x == "":
        x = 0
    return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)
