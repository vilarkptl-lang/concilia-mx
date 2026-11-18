"""Tipos compartidos del motor de reconocimiento NIF.

Cada palanca (C-6, C-8, D-1, C-9) devuelve un GateResult. Regla transversal:
NINGÚN ajuste se acepta sin (a) evidencia documental y (b) pasar el test NIF.
El GateResult rechazado NO produce asiento; puede traer `nota_revelacion`
(lo que se revela en notas en vez de capitalizar/ocultar).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Evidencia:
    tipo: str              # factura | contrato | cep | acta | estado_cuenta | ...
    ref: str               # ruta en el dropzone gateado del tenant / id del documento
    sha256: str = ""       # huella del documento (no el documento)


@dataclass
class GateResult:
    aceptado: bool
    base_nif: str
    razon: str
    asiento: Optional[object] = None        # Asiento si aceptado y genera registro
    nota_revelacion: Optional[str] = None   # disclosure cuando NO se reconoce
