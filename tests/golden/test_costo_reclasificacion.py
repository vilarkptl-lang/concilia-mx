"""Costo de reclasificar un depósito no facturado como venta (IVA + ISR, netando COGS)."""
import unittest
from decimal import Decimal

from engine.costo_reclasificacion import estimar


class TestCosto(unittest.TestCase):

    def test_sin_costos_iva_incluido(self):
        # Depósito 11,600 IVA incluido, sin COGS, ISR 30%.
        r = estimar(Decimal("11600"), iva_incluido=True,
                    tasa_iva=Decimal("0.16"), tasa_isr=Decimal("0.30"))
        self.assertEqual(r.base_ingreso, Decimal("10000.00"))
        self.assertEqual(r.iva_a_pagar, Decimal("1600.00"))
        self.assertEqual(r.isr, Decimal("3000.00"))
        self.assertEqual(r.costo_total, Decimal("4600.00"))

    def test_con_cogs_reduce_isr_e_iva(self):
        # Misma venta pero con COGS 6,000 (orden de compra) con IVA acreditable.
        r = estimar(Decimal("11600"), iva_incluido=True,
                    tasa_iva=Decimal("0.16"), tasa_isr=Decimal("0.30"),
                    costos_deducibles=Decimal("6000"), costos_con_iva=True)
        self.assertEqual(r.iva_acreditable, Decimal("960.00"))
        self.assertEqual(r.iva_a_pagar, Decimal("640.00"))
        self.assertEqual(r.utilidad_gravable, Decimal("4000.00"))
        self.assertEqual(r.isr, Decimal("1200.00"))
        self.assertEqual(r.costo_total, Decimal("1840.00"))

    def test_periodo_previo_marca_recargos(self):
        r = estimar(Decimal("11600"), periodo_previo=True)
        self.assertTrue(r.periodo_previo)
        self.assertIn("recargos", r.nota)


if __name__ == "__main__":
    unittest.main()
