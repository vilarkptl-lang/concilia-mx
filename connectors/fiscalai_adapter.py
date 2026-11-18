"""Adaptador para descargar INSUMOS FISCALES (declaraciones presentadas + histórico de
CFDI) desde el SAT. En este repo público va con un backend LOCAL por defecto (lee de
una carpeta que el usuario ya descargó), de modo que todo corre sin credenciales.

El backend "fiscalai" (descarga automatizada con la e.firma/CIEC del usuario) es una
pieza SEPARADA y con credenciales del propio usuario; aquí solo se define la INTERFAZ.
Nunca se piden ni se guardan credenciales del SAT en este repo.
"""
import json
import os
from typing import List


class LocalBackend:
    """Lee insumos que el usuario ya exportó a una carpeta (declaraciones .json/.pdf,
    CFDI .xml). No toca el SAT. Es el modo por defecto del repo público."""

    def __init__(self, carpeta: str):
        self.carpeta = carpeta

    def listar_declaraciones(self) -> List[dict]:
        ruta = os.path.join(self.carpeta, "declaraciones.json")
        if not os.path.exists(ruta):
            return []
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)

    def listar_cfdi(self) -> List[str]:
        d = os.path.join(self.carpeta, "cfdi")
        if not os.path.isdir(d):
            return []
        return [os.path.join(d, x) for x in os.listdir(d) if x.lower().endswith(".xml")]


def get_backend(modo: str = "local", **kw):
    """modo='local' (default). modo='fiscalai' se implementa fuera de este repo,
    con las credenciales del propio usuario; aquí se deja el punto de extensión."""
    if modo == "local":
        return LocalBackend(kw["carpeta"])
    raise NotImplementedError(
        "El backend 'fiscalai' (descarga automatizada con e.firma/CIEC del usuario) "
        "es externo a este repo público; usa modo='local' con tus exports.")
