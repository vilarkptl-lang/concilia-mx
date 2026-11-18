"""Ingest de CFDI (XML 3.3/4.0) -> objetos CFDI para el matching de clasificación.
Lee UUID (TimbreFiscalDigital), Fecha, Total y tipo de comprobante. Tolerante a
namespaces. No valida el sello (eso es del PAC); aquí solo extraemos datos."""
import os
import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import List

from ..clasificacion import CFDI

_TIPO = {"I": "I", "E": "E", "P": "P", "N": "N", "T": "T"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_xml(path: str) -> CFDI:
    root = ET.parse(path).getroot()
    total = root.attrib.get("Total") or root.attrib.get("total") or "0"
    fecha = (root.attrib.get("Fecha") or root.attrib.get("fecha") or "")[:10]
    tipo = root.attrib.get("TipoDeComprobante") or root.attrib.get("tipoDeComprobante") or "I"
    uuid = ""
    for el in root.iter():
        if _local(el.tag) == "TimbreFiscalDigital":
            uuid = el.attrib.get("UUID", "")
            break
    return CFDI(uuid=uuid or os.path.basename(path), tipo=_TIPO.get(tipo, tipo),
                fecha=fecha, total=Decimal(str(total)))


def parse_dir(carpeta: str) -> List[CFDI]:
    out = []
    for name in sorted(os.listdir(carpeta)):
        if name.lower().endswith(".xml"):
            out.append(parse_xml(os.path.join(carpeta, name)))
    return out
