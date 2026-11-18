"""Conector CanalPulse (agregador de ventas de marketplaces: Amazon/ML/TikTok).
SOLO LECTURA (GET). Trae las ventas/órdenes reales para cruzarlas contra el banco y
los CFDI y así detectar lo no facturado.

Credenciales SIEMPRE del entorno del usuario (CANALPULSE_API_URL, CANALPULSE_ORDERS_KEY);
NUNCA en el repo ni en el código. Patrón adaptador: el repo público trae el conector,
las llaves viven en el .env del usuario (gitignored).
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request


def _cfg():
    url = os.environ.get("CANALPULSE_API_URL")
    key = os.environ.get("CANALPULSE_ORDERS_KEY")
    if not url or not key:
        raise SystemExit("Falta CANALPULSE_API_URL / CANALPULSE_ORDERS_KEY en el entorno.")
    return url.rstrip("/"), key


def get_orders(start=None, end=None, path="/orders", extra=None, timeout=30):
    """GET read-only de órdenes/ventas. Ajusta `path`/params al contrato real de CanalPulse.
    Devuelve {status, data|error}. No imprime la llave."""
    base, key = _cfg()
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    if extra:
        params.update(extra)
    url = base + path + (("?" + urllib.parse.urlencode(params)) if params else "")
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "data": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read().decode()[:500]}
    except Exception as e:
        return {"status": None, "error": f"ERROR_CONEXION: {e}"}
