"""Ingest de reportes de liquidación (payouts) de marketplaces: Amazon,
Mercado Libre, TikTok Shop.

Complejidad clave: el DEPÓSITO que llega al banco es el NETO (venta bruta − comisiones
− fees − retenciones). El ingreso contable es la venta BRUTA; la comisión y los fees
son GASTO deducible. Por eso un payout no se contabiliza por el neto: se "explota".
"""
import csv
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from ..money import money


@dataclass
class Payout:
    marketplace: str            # amazon | mercadolibre | tiktok
    periodo: str                # etiqueta del periodo de liquidación
    bruto: Decimal              # ventas brutas (lo que pagó el cliente final)
    comisiones: Decimal         # comisión del marketplace
    fees: Decimal               # otros cargos (envío, publicidad, etc.)
    retenciones: Decimal        # ISR/IVA retenido por el marketplace (si aplica)
    neto: Decimal               # lo efectivamente depositado al banco
    referencia: str = ""

    def cuadra(self, tol=Decimal("0.02")) -> bool:
        calc = money(self.bruto - self.comisiones - self.fees - self.retenciones)
        return abs(calc - money(self.neto)) <= tol


def parse_csv(path: str, marketplace: str) -> List[Payout]:
    """CSV con encabezados: periodo, bruto, comisiones, fees, retenciones, neto, referencia."""
    out: List[Payout] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip().lower(): v for k, v in row.items()}
            out.append(Payout(
                marketplace=marketplace,
                periodo=(row.get("periodo") or "").strip(),
                bruto=money(row.get("bruto")),
                comisiones=money(row.get("comisiones")),
                fees=money(row.get("fees")),
                retenciones=money(row.get("retenciones")),
                neto=money(row.get("neto")),
                referencia=(row.get("referencia") or "").strip(),
            ))
    return out
