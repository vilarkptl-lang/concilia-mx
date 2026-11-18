"""Clasificación: detectar lo NO facturado (el objetivo), casar CFDI y payouts."""
import unittest
from decimal import Decimal

from engine.ingest.banco import MovBanco
from engine.ingest.marketplace import Payout
from engine.clasificacion import (
    CFDI, clasificar_deposito, FACTURADO, MARKETPLACE_PAYOUT, NO_FACTURADO)
from engine.money import money


def dep(monto, fecha, desc="", ref="", _id="m1"):
    return MovBanco(fecha=fecha, descripcion=desc, deposito=money(monto),
                    retiro=money(0), referencia=ref, id=_id)


class TestClasificacion(unittest.TestCase):

    def test_facturado_casa_cfdi(self):
        c = CFDI(uuid="U1", tipo="I", fecha="2026-11-10", total=Decimal("1160.00"))
        r = clasificar_deposito(dep("1160.00", "2026-11-12"), [c], [])
        self.assertEqual(r.estado, FACTURADO)
        self.assertEqual(r.match_ref, "U1")

    def test_payout_marketplace(self):
        p = Payout("mercadolibre", "2026-11-Q1", bruto=Decimal("10000"),
                   comisiones=Decimal("1500"), fees=Decimal("500"),
                   retenciones=Decimal("0"), neto=Decimal("8000"))
        r = clasificar_deposito(dep("8000.00", "2026-11-15"), [], [p])
        self.assertEqual(r.estado, MARKETPLACE_PAYOUT)

    def test_no_facturado_es_candidato(self):
        r = clasificar_deposito(dep("45000.00", "2026-11-15", desc="SPEI de cliente"), [], [])
        self.assertEqual(r.estado, NO_FACTURADO)        # sin CFDI ni payout -> foco

    def test_cfdi_fuera_de_ventana_no_casa(self):
        c = CFDI(uuid="U2", tipo="I", fecha="2026-01-01", total=Decimal("1160.00"))
        r = clasificar_deposito(dep("1160.00", "2026-11-12"), [c], [])
        self.assertEqual(r.estado, NO_FACTURADO)        # mismo monto pero 10 meses después


if __name__ == "__main__":
    unittest.main()
