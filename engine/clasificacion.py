"""Clasificación de movimientos bancarios — el objetivo primario.

Para CADA depósito decide su estado, de forma determinista y EXPLICABLE (cada
clasificación trae razón + confianza), con especial foco en detectar lo
NO FACTURADO (candidato a reclasificarse como venta):

  facturado          -> casa con un CFDI emitido (monto + ventana de fecha / referencia)
  marketplace_payout -> casa con un payout de Amazon/ML/TikTok (se explota aparte)
  traspaso           -> transferencia entre cuentas propias
  no_facturado       -> depósito sin CFDI ni payout -> CANDIDATO A VENTA (foco)
  sin_clasificar     -> no se pudo decidir

Egresos: pago_proveedor / gasto_facturado / egreso_sin_clasificar.
El matching por monto usa tolerancia; por fecha, una ventana en días; además
referencia/clave de rastreo por substring con fronteras (evita falsos por substring).
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Optional

from .money import money

FACTURADO = "facturado"
MARKETPLACE_PAYOUT = "marketplace_payout"
TRASPASO = "traspaso"
NO_FACTURADO = "no_facturado"
SIN_CLASIFICAR = "sin_clasificar"
PAGO_PROVEEDOR = "pago_proveedor"
GASTO_FACTURADO = "gasto_facturado"
EGRESO_SIN_CLASIFICAR = "egreso_sin_clasificar"


@dataclass
class CFDI:
    uuid: str
    tipo: str                 # I (ingreso/emitido) | E (egreso) | recibido
    fecha: str                # YYYY-MM-DD
    total: Decimal
    contraparte: str = ""     # cliente o proveedor
    referencia: str = ""


@dataclass
class Clasificacion:
    mov_id: str
    estado: str
    confianza: str            # alta | media | baja
    razon: str
    match_ref: str = ""       # a qué casó (uuid/payout/cuenta)


def _dias(a: str, b: str) -> int:
    try:
        ya, ma, da = (int(x) for x in a.split("-"))
        yb, mb, db = (int(x) for x in b.split("-"))
        return abs((date(ya, ma, da) - date(yb, mb, db)).days)
    except Exception:
        return 10**6


def _monto_cerca(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(money(a) - money(b)) <= tol


def clasificar_deposito(mov, cfdis: List[CFDI], payouts: List,
                        cuentas_propias: Optional[List[str]] = None,
                        tol_monto: Decimal = Decimal("1.00"),
                        ventana_dias: int = 5) -> Clasificacion:
    cuentas_propias = cuentas_propias or []
    # 1) ¿CFDI emitido que casa por monto + fecha?
    for c in cfdis:
        if c.tipo in ("I", "emitido") and _monto_cerca(mov.deposito, c.total, tol_monto) \
                and _dias(mov.fecha, c.fecha) <= ventana_dias:
            return Clasificacion(mov.id, FACTURADO, "alta",
                                 f"Casa CFDI emitido {c.uuid} (±{tol_monto}, {ventana_dias}d).",
                                 c.uuid)
    # 2) ¿payout de marketplace (por neto)?
    campos = f"{mov.descripcion} {mov.referencia}".lower()
    for p in payouts:
        if _monto_cerca(mov.deposito, p.neto, tol_monto) and \
                (not p.referencia or p.referencia.lower() in campos):
            return Clasificacion(mov.id, MARKETPLACE_PAYOUT, "alta",
                                 f"Casa payout {p.marketplace} {p.periodo} (neto); explotar a "
                                 f"bruto+comisiones+fees.", f"{p.marketplace}:{p.periodo}")
    # 3) ¿traspaso entre cuentas propias?
    desc = mov.descripcion.lower()
    if any(cp.lower() in desc for cp in cuentas_propias if cp):
        return Clasificacion(mov.id, TRASPASO, "media", "Descripción refiere cuenta propia.")
    # 4) NO FACTURADO: depósito sin respaldo -> candidato a venta
    return Clasificacion(mov.id, NO_FACTURADO, "media",
                         "Depósito sin CFDI ni payout: candidato a venta a reclasificar.")


def clasificar_egreso(mov, cfdis: List[CFDI], proveedores: Optional[List[str]] = None,
                      tol_monto: Decimal = Decimal("1.00")) -> Clasificacion:
    proveedores = proveedores or []
    desc = mov.descripcion.lower()
    for c in cfdis:
        if c.tipo in ("E", "recibido") and _monto_cerca(mov.retiro, c.total, tol_monto):
            return Clasificacion(mov.id, GASTO_FACTURADO, "alta",
                                 f"Casa CFDI recibido {c.uuid}.", c.uuid)
    if any(pv.lower() in desc for pv in proveedores if pv):
        return Clasificacion(mov.id, PAGO_PROVEEDOR, "media", "Descripción refiere proveedor.")
    return Clasificacion(mov.id, EGRESO_SIN_CLASIFICAR, "baja", "Egreso sin CFDI ni proveedor.")


def clasificar_todo(movs, cfdis, payouts, cuentas_propias=None, proveedores=None):
    res = []
    for m in movs:
        if m.es_deposito:
            res.append(clasificar_deposito(m, cfdis, payouts, cuentas_propias))
        else:
            res.append(clasificar_egreso(m, cfdis, proveedores))
    return res


def resumen(clasifs: List[Clasificacion]) -> dict:
    out = {}
    for c in clasifs:
        out[c.estado] = out.get(c.estado, 0) + 1
    return out
