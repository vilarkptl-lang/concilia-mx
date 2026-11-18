"""Evidencia: cada ajuste/clasificación se respalda con un documento. Guardamos la
RUTA y la HUELLA (sha256) del documento, nunca el documento ni su contenido en claro
dentro del repo. Los documentos viven en el almacén gateado del usuario."""
import hashlib
import os
from dataclasses import dataclass


@dataclass
class Evidencia:
    tipo: str
    ref: str
    sha256: str = ""


def huella(path: str) -> str:
    """sha256 de un archivo (para ligar evidencia sin copiar el documento al repo)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def evidencia_de(path: str, tipo: str) -> Evidencia:
    return Evidencia(tipo=tipo, ref=os.path.basename(path), sha256=huella(path))
