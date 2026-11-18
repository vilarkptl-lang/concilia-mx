"""Conector Odoo (ERP del usuario) — lectura vía JSON-RPC (/jsonrpc).
Útil para leer de su Odoo lo ya cargado (facturas, ventas, movimientos de banco) y
conciliarlo. Credenciales SIEMPRE del entorno (ODOO_URL, ODOO_DB, ODOO_USERNAME,
ODOO_API_KEY); NUNCA en el repo.
"""
import json
import os
import urllib.request


def _cfg():
    for v in ("ODOO_URL", "ODOO_DB", "ODOO_USERNAME", "ODOO_API_KEY"):
        if not os.environ.get(v):
            raise SystemExit(f"Falta {v} en el entorno.")
    return (os.environ["ODOO_URL"].rstrip("/"), os.environ["ODOO_DB"],
            os.environ["ODOO_USERNAME"], os.environ["ODOO_API_KEY"])


def _rpc(url, service, method, args, timeout=30):
    payload = {"jsonrpc": "2.0", "method": "call",
               "params": {"service": service, "method": method, "args": args}}
    req = urllib.request.Request(url + "/jsonrpc", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.loads(r.read().decode())
    if res.get("error"):
        raise RuntimeError(res["error"])
    return res["result"]


def search_read(model, domain=None, fields=None, limit=100):
    """Lectura genérica de un modelo de Odoo (p.ej. 'account.move', 'sale.order',
    'account.bank.statement.line'). Read-only."""
    url, db, user, key = _cfg()
    uid = _rpc(url, "common", "login", [db, user, key])
    return _rpc(url, "object", "execute_kw",
                [db, uid, key, model, "search_read",
                 [domain or []], {"fields": fields or [], "limit": limit}])
