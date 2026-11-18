"""Invariante del ledger: partida doble cuadra; debe XOR haber por renglón."""
import unittest
from decimal import Decimal

from engine.ledger import Asiento, Renglon


class TestPartidaDoble(unittest.TestCase):

    def test_cuadra(self):
        a = Asiento("2026-11-18", "venta", [
            Renglon("1020", debit=Decimal("116")),
            Renglon("4010", credit=Decimal("100")),
            Renglon("2080", credit=Decimal("16")),
        ])
        self.assertTrue(a.validar())

    def test_no_cuadra_lanza(self):
        a = Asiento("2026-11-18", "x", [
            Renglon("1020", debit=Decimal("100")),
            Renglon("4010", credit=Decimal("90")),
        ])
        with self.assertRaises(ValueError):
            a.validar()

    def test_debe_y_haber_mismo_renglon_lanza(self):
        a = Asiento("2026-11-18", "x", [
            Renglon("1020", debit=Decimal("100"), credit=Decimal("100")),
        ])
        with self.assertRaises(ValueError):
            a.validar()


if __name__ == "__main__":
    unittest.main()
