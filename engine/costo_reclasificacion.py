"""Costo fiscal de reclasificar un depósito NO facturado como VENTA.

Orienta — ANTES de decidir — cuánto costaría, en impuestos, reconocer formalmente
ese ingreso, netando los costos deducibles relacionados (COGS: la orden de compra al
proveedor). Es una herramienta PRO-CUMPLIMIENTO: dice el costo real de ponerse al día.

Supuestos explícitos (todos parametrizables desde las declaraciones ya presentadas):
  - iva_incluido: si el depósito ya trae IVA (venta a consumidor final: normalmente sí).
  - tasa_iva: 0.16 por defecto.
  - tasa_isr: tasa efectiva/ marginal de la empresa según sus declaraciones (0.30 PM general).
  - costos_deducibles: base (sin IVA) de la orden de compra relacionada, si la hay.
No calcula recargos/actualización de periodos previos: si el ingreso es de un ejercicio
ya declarado, se marca `periodo_previo=True` para que el contador agregue recargos.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .money import money


@dataclass
class CostoReclasificacion:
    deposito: Decimal
    base_ingreso: Decimal          # ingreso sin IVA
    iva_trasladado: Decimal
    iva_acreditable: Decimal       # del costo deducible, si trae IVA
    iva_a_pagar: Decimal
    utilidad_gravable: Decimal
    isr: Decimal
    costo_total: Decimal           # iva_a_pagar + isr
    tasa_iva: Decimal
    tasa_isr: Decimal
    periodo_previo: bool
    nota: str


def estimar(deposito, iva_incluido: bool = True,
            tasa_iva: Decimal = Decimal("0.16"),
            tasa_isr: Decimal = Decimal("0.30"),
            costos_deducibles: Decimal = Decimal("0"),
            costos_con_iva: bool = True,
            periodo_previo: bool = False) -> CostoReclasificacion:
    deposito = money(deposito)
    tasa_iva = Decimal(str(tasa_iva))
    tasa_isr = Decimal(str(tasa_isr))
    costos_deducibles = money(costos_deducibles)

    if iva_incluido:
        base_ingreso = money(deposito / (Decimal("1") + tasa_iva))
    else:
        base_ingreso = deposito
    iva_trasladado = money(base_ingreso * tasa_iva)
    iva_acreditable = money(costos_deducibles * tasa_iva) if costos_con_iva else money(0)
    iva_a_pagar = money(iva_trasladado - iva_acreditable)

    utilidad_gravable = money(base_ingreso - costos_deducibles)
    if utilidad_gravable < 0:
        utilidad_gravable = money(0)
    isr = money(utilidad_gravable * tasa_isr)
    costo_total = money(iva_a_pagar + isr)

    nota = (f"Reclasificar {deposito} como venta cuesta ~{costo_total} en impuestos "
            f"(IVA {iva_a_pagar} + ISR {isr}), netando COGS {costos_deducibles}.")
    if periodo_previo:
        nota += (" ATENCIÓN: ejercicio ya declarado -> el contador debe sumar "
                 "recargos y actualización (complementaria).")
    return CostoReclasificacion(deposito, base_ingreso, iva_trasladado, iva_acreditable,
                                iva_a_pagar, utilidad_gravable, isr, costo_total,
                                tasa_iva, tasa_isr, periodo_previo, nota)
