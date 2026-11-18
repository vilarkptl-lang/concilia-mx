"""Cliente Alegra para publicar pólizas (comprobantes contables) vía API.
POST /journals. dry_run por defecto; escritura real solo con ALEGRA_ALLOW_LIVE=1.
Credenciales SIEMPRE del entorno (correo API + token self-service de Configuración → API),
nunca en el repo. Base URL pública: https://api.alegra.com/api/v1
"""
import base64
import json
import os
import urllib.error
import urllib.request

BASE = (os.environ.get("ALEGRA_BASE_URL") or "https://api.alegra.com/api/v1").rstrip("/")


def _auth() -> str:
    email = os.environ["ALEGRA_API_EMAIL"]
    token = os.environ["ALEGRA_API_TOKEN"]
    return "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()


def asiento_a_alegra(asiento, cuenta_a_id: dict) -> dict:
    """Convierte un Asiento del motor al cuerpo de /journals de Alegra.
    cuenta_a_id mapea el código de cuenta del catálogo al id interno de Alegra."""
    entries = []
    for r in asiento.renglones:
        e = {"account": {"id": cuenta_a_id[r.cuenta]}}
        if r.debit > 0:
            e["debit"] = float(r.debit)
        else:
            e["credit"] = float(r.credit)
        entries.append(e)
    return {"date": asiento.fecha, "observations": asiento.descripcion,
            "reference": asiento.referencia, "entries": entries}


def crear_poliza(body: dict, dry_run: bool = True) -> dict:
    if dry_run or os.environ.get("ALEGRA_ALLOW_LIVE") != "1":
        return {"dry_run": True, "endpoint": "POST /journals", "body": body}
    req = urllib.request.Request(BASE + "/journals", method="POST",
                                 data=json.dumps(body).encode())
    req.add_header("Authorization", _auth())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"status": r.status, "body": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read().decode()}
