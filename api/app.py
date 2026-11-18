"""API opcional (FastAPI). Solo si instalas fastapi+uvicorn. El núcleo NO la necesita.
Expone la clasificación para que una UI/el agente la consuma.

Correr:  uvicorn api.app:app --port 8099
"""
from decimal import Decimal

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except Exception as e:  # pragma: no cover
    raise SystemExit("La API necesita: pip install fastapi uvicorn") from e

from engine.ingest.banco import MovBanco
from engine import clasificacion as clf
from engine.costo_reclasificacion import estimar
from engine.money import money

app = FastAPI(title="concilia-mx")


class MovIn(BaseModel):
    id: str = "m"
    fecha: str
    descripcion: str = ""
    deposito: float = 0
    retiro: float = 0
    referencia: str = ""


class ClasificarIn(BaseModel):
    movimientos: list[MovIn]
    tasa_isr: float = 0.30


@app.post("/clasificar")
def clasificar(body: ClasificarIn):
    movs = [MovBanco(m.fecha, m.descripcion, money(m.deposito), money(m.retiro),
                     m.referencia, m.id) for m in body.movimientos]
    clasifs = clf.clasificar_todo(movs, [], [])
    by_id = {c.mov_id: c for c in clasifs}
    out = []
    for m in movs:
        c = by_id[m.id]
        row = {"id": m.id, "estado": c.estado, "razon": c.razon}
        if c.estado == clf.NO_FACTURADO:
            co = estimar(m.deposito, tasa_isr=Decimal(str(body.tasa_isr)))
            row["costo_reclasificacion"] = str(co.costo_total)
        out.append(row)
    return {"resultado": out, "resumen": clf.resumen(clasifs)}
