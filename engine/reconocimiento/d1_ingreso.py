"""NIF D-1 — Ingresos por contratos (reconocer lo NO facturado, con evidencia).

Bajo devengo, el ingreso se reconoce cuando se gana, se haya facturado o no. Si hay
depósito bancario real + evidencia (contrato/orden/entrega), es ingreso en el libro
INTERNO.

LÍNEA ROJA: reconocer ingreso no facturado crea una BRECHA FISCAL (ingreso omitido =
contingencia). El gate la marca SIEMPRE (`brecha_fiscal=True`) para que la conciliación
la cuantifique y surja la ruta de remediación (complementarias). No se oculta, no se
fabrica ingreso sin evidencia + depósito.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..money import money
from ..ledger import Asiento, Renglon
from .base import GateResult, Evidencia

CUENTA_BANCO = "1020"
CUENTA_INGRESO = "4010"            # Ingresos (placeholder; catálogo real por tenant)
BASE_NIF = "NIF D-1 Ingresos por contratos con clientes"


@dataclass
class IngresoNoFacturado:
    descripcion: str
    monto: Optional[Decimal] = None
    deposito_bancario: bool = False       # ¿hay depósito real en banco?
    evidencia: Optional[Evidencia] = None
    fecha: str = ""


@dataclass
class ResultadoIngreso(GateResult):
    brecha_fiscal: bool = False           # True => ingreso reconocido interno, no facturado


def evaluar_ingreso(i: IngresoNoFacturado) -> ResultadoIngreso:
    faltantes = []
    if i.monto is None or money(i.monto) <= 0:
        faltantes.append("monto")
    if not i.deposito_bancario:
        faltantes.append("depósito bancario (fuente más fehaciente)")
    if i.evidencia is None:
        faltantes.append("evidencia (contrato/orden/entrega)")
    if faltantes:
        return ResultadoIngreso(False, BASE_NIF,
                                f"Ingreso no reconocido por falta de: {', '.join(faltantes)}.",
                                asiento=None)

    monto = money(i.monto)
    asiento = Asiento(
        fecha=i.fecha,
        descripcion=f"Ingreso devengado no facturado: {i.descripcion}",
        renglones=[
            Renglon(CUENTA_BANCO, debit=monto, descripcion="Depósito recibido"),
            Renglon(CUENTA_INGRESO, credit=monto, descripcion="Ingreso devengado (no facturado)"),
        ],
        referencia=f"RECON/D1/{i.evidencia.ref}",
        origen="reconocimiento",
    )
    asiento.validar()
    return ResultadoIngreso(
        True, BASE_NIF,
        f"Ingreso reconocido {monto} en libro interno. BRECHA FISCAL: no facturado -> "
        f"cuantificar en conciliación y evaluar complementaria.",
        asiento=asiento, brecha_fiscal=True)
