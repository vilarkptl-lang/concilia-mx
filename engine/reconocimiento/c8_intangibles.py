"""NIF C-8 — Activos intangibles (marcas, derechos de representación/distribución).

LÍNEA ROJA (el corazón del gate): un intangible GENERADO INTERNAMENTE —marca propia,
"efecto de marca", plusvalía autogenerada, listas de clientes— NO se reconoce como
activo (NIF C-8, alineado a IAS 38.63). Se puede VALUAR para revelación en notas,
nunca subir al balance.

SÍ se reconoce el intangible ADQUIRIDO (p.ej. derechos de representación/distribución
de marcas extranjeras comprados por un costo, licencias, marcas compradas) cuando
cumple: costo confiable + identificable + control + evidencia documental. Se registra
al costo y se amortiza sobre su vida útil (vigencia del contrato).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..money import money
from ..ledger import Asiento, Renglon
from .base import GateResult, Evidencia

ORIGEN_AUTOGENERADA = "autogenerada"
ORIGEN_ADQUIRIDA = "adquirida"

CUENTA_INTANGIBLE = "1250"          # Activos intangibles (placeholder; catálogo real por tenant)
BASE_NIF = "NIF C-8 Activos intangibles"


@dataclass
class CandidatoIntangible:
    nombre: str
    origen: str                                  # autogenerada | adquirida
    costo: Optional[Decimal] = None
    identificable: bool = False                  # separable o por derecho contractual/legal
    control: bool = False
    vida_util_meses: Optional[int] = None
    evidencia: Optional[Evidencia] = None
    cuenta_contrapartida: str = "1020"           # bancos por defecto (o pasivo)
    fecha: str = ""
    valuacion_referencia: Optional[Decimal] = None   # para nota (relief-from-royalty), NO capitaliza


def evaluar_intangible(c: CandidatoIntangible) -> GateResult:
    # --- LÍNEA ROJA: autogenerado => NO se capitaliza ---
    if c.origen == ORIGEN_AUTOGENERADA:
        nota = (f"Marca/intangible autogenerado '{c.nombre}': NO se capitaliza "
                f"(NIF C-8 prohíbe intangibles generados internamente). ")
        if c.valuacion_referencia is not None:
            nota += (f"Valor estimado para REVELACIÓN en notas: "
                     f"{money(c.valuacion_referencia)} (no reconocido en balance).")
        return GateResult(False, BASE_NIF,
                          "Intangible autogenerado: reconocimiento prohibido.",
                          asiento=None, nota_revelacion=nota)

    if c.origen != ORIGEN_ADQUIRIDA:
        return GateResult(False, BASE_NIF, f"Origen desconocido: '{c.origen}'.")

    # --- ADQUIRIDO: exige los 4 criterios (gate duro) ---
    faltantes = []
    if c.costo is None or money(c.costo) <= 0:
        faltantes.append("costo confiable")
    if not c.identificable:
        faltantes.append("identificable (separable o por derecho contractual/legal)")
    if not c.control:
        faltantes.append("control sobre beneficios futuros")
    if c.evidencia is None:
        faltantes.append("evidencia documental")
    if faltantes:
        nota = (f"Intangible adquirido '{c.nombre}' NO reconocido por falta de: "
                f"{', '.join(faltantes)}. Revelar en notas si procede.")
        return GateResult(False, BASE_NIF,
                          f"No cumple criterios NIF C-8: {', '.join(faltantes)}.",
                          asiento=None, nota_revelacion=nota)

    costo = money(c.costo)
    asiento = Asiento(
        fecha=c.fecha,
        descripcion=f"Reconocimiento de intangible adquirido: {c.nombre}",
        renglones=[
            Renglon(CUENTA_INTANGIBLE, debit=costo, descripcion=f"Intangible {c.nombre}"),
            Renglon(c.cuenta_contrapartida, credit=costo,
                    descripcion="Pago/pasivo por adquisición del intangible"),
        ],
        referencia=f"RECON/C8/{c.nombre}/{c.evidencia.ref}",
        origen="reconocimiento",
    )
    asiento.validar()
    vu = (f"; amortizable en {c.vida_util_meses} meses" if c.vida_util_meses
          else "; vida útil a definir con el contador")
    return GateResult(True, BASE_NIF,
                      f"Intangible adquirido reconocido al costo {costo}{vu}.",
                      asiento=asiento, nota_revelacion=None)
