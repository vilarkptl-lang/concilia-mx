"""LÍNEA ROJA C-8: la marca propia NO se capitaliza; la representación adquirida con
costo + evidencia SÍ. Estas pruebas son el candado: si alguien afloja el gate, fallan."""
import unittest
from decimal import Decimal

from engine.reconocimiento.base import Evidencia
from engine.reconocimiento.c8_intangibles import (
    CandidatoIntangible, evaluar_intangible, ORIGEN_AUTOGENERADA, ORIGEN_ADQUIRIDA)


class TestC8(unittest.TestCase):

    def test_marca_propia_no_capitaliza(self):
        c = CandidatoIntangible(nombre="MarcaPropia", origen=ORIGEN_AUTOGENERADA,
                                valuacion_referencia=Decimal("5000000"))
        r = evaluar_intangible(c)
        self.assertFalse(r.aceptado)
        self.assertIsNone(r.asiento)                 # NO entra al balance
        self.assertIn("REVELACIÓN", r.nota_revelacion)  # se revela en notas

    def test_representacion_adquirida_con_costo_si(self):
        c = CandidatoIntangible(
            nombre="RepMarcaExtranjera", origen=ORIGEN_ADQUIRIDA,
            costo=Decimal("1200000"), identificable=True, control=True,
            vida_util_meses=36, fecha="2026-11-18",
            evidencia=Evidencia("contrato", "contratos/rep-x.pdf"))
        r = evaluar_intangible(c)
        self.assertTrue(r.aceptado)
        self.assertIsNotNone(r.asiento)
        self.assertTrue(r.asiento.cuadra())
        self.assertEqual(r.asiento.total_debe(), Decimal("1200000.00"))

    def test_adquirida_sin_evidencia_rechaza(self):
        c = CandidatoIntangible(nombre="RepSinPapel", origen=ORIGEN_ADQUIRIDA,
                                costo=Decimal("500000"), identificable=True, control=True)
        r = evaluar_intangible(c)
        self.assertFalse(r.aceptado)                 # gate duro: sin evidencia, no pasa

    def test_adquirida_sin_costo_rechaza(self):
        c = CandidatoIntangible(nombre="RepSinCosto", origen=ORIGEN_ADQUIRIDA,
                                identificable=True, control=True,
                                evidencia=Evidencia("contrato", "x.pdf"))
        r = evaluar_intangible(c)
        self.assertFalse(r.aceptado)


if __name__ == "__main__":
    unittest.main()
