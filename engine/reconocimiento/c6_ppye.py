"""NIF C-6 — Propiedades, planta y equipo (reclasificar consumible -> equipo).

LÍNEA ROJA: solo se capitaliza lo que de verdad es equipo: beneficio económico
futuro probable + VIDA ÚTIL > 12 meses + control + COSTO con factura. Lo que se
agota en la operación o es de bajo valor se queda como gasto/inventario. No se
reetiqueta para inflar el activo.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..money import money
from ..ledger import Asiento, Renglon
from .base import GateResult, Evidencia

CUENTA_EQUIPO = "1240"              # Equipo (placeholder; catálogo real por tenant)
BASE_NIF = "NIF C-6 Propiedades, planta y equipo"
UMBRAL_MESES = 12


@dataclass
class CandidatoEquipo:
    nombre: str
    costo: Optional[Decimal] = None
    vida_util_meses: Optional[int] = None
    control: bool = False
    beneficio_futuro: bool = False
    evidencia: Optional[Evidencia] = None
    cuenta_origen: str = "1150"        # inventario/consumibles de donde se reclasifica
    fecha: str = ""


def evaluar_equipo(c: CandidatoEquipo) -> GateResult:
    faltantes = []
    if c.costo is None or money(c.costo) <= 0:
        faltantes.append("costo con factura")
    if c.vida_util_meses is None or c.vida_util_meses <= UMBRAL_MESES:
        faltantes.append(f"vida útil > {UMBRAL_MESES} meses")
    if not c.control:
        faltantes.append("control")
    if not c.beneficio_futuro:
        faltantes.append("beneficio económico futuro probable")
    if c.evidencia is None:
        faltantes.append("evidencia documental")
    if faltantes:
        return GateResult(False, BASE_NIF,
                          f"No califica como PPyE: {', '.join(faltantes)}. "
                          f"Se mantiene como gasto/inventario.",
                          asiento=None)

    costo = money(c.costo)
    asiento = Asiento(
        fecha=c.fecha,
        descripcion=f"Reclasificación a equipo (PPyE): {c.nombre}",
        renglones=[
            Renglon(CUENTA_EQUIPO, debit=costo, descripcion=f"Equipo {c.nombre}"),
            Renglon(c.cuenta_origen, credit=costo,
                    descripcion="Salida de inventario/consumible reclasificado"),
        ],
        referencia=f"RECON/C6/{c.nombre}/{c.evidencia.ref}",
        origen="reconocimiento",
    )
    asiento.validar()
    return GateResult(True, BASE_NIF,
                      f"Reclasificado a PPyE al costo {costo}; depreciable en "
                      f"{c.vida_util_meses} meses.",
                      asiento=asiento)
