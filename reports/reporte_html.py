"""Genera un reporte HTML autocontenido (sin dependencias) con el resumen de
clasificación y los candidatos NO facturados con su costo de reclasificación.
Es el embrión del dashboard; un frontend más rico puede consumir el mismo JSON."""
import html
import json
from decimal import Decimal


def _money(x):
    return f"${Decimal(str(x)):,.2f}"


def generar(data: dict) -> str:
    filas = ""
    for c in data.get("candidatos", []):
        costo = c.get("costo", {})
        filas += (f"<tr><td>{html.escape(c['fecha'])}</td>"
                  f"<td>{html.escape(c['descripcion'])}</td>"
                  f"<td style='text-align:right'>{_money(c['monto'])}</td>"
                  f"<td style='text-align:right'>{_money(costo.get('iva_a_pagar',0))}</td>"
                  f"<td style='text-align:right'>{_money(costo.get('isr',0))}</td>"
                  f"<td style='text-align:right'><b>{_money(costo.get('costo_total',0))}</b></td></tr>")
    chips = "".join(
        f"<span class=chip>{html.escape(k)}: <b>{v}</b></span>"
        for k, v in data.get("resumen", {}).items())
    return f"""<!doctype html><meta charset=utf-8>
<title>concilia-mx — reporte</title>
<style>
body{{font:14px system-ui;margin:0;background:#0f1220;color:#e7e9f3}}
.wrap{{max-width:980px;margin:0 auto;padding:24px}}
h1{{font-size:20px}} .sub{{color:#9aa0b5}}
.chip{{display:inline-block;background:#1b2036;border:1px solid #2a3153;border-radius:999px;
padding:4px 10px;margin:3px}}
table{{width:100%;border-collapse:collapse;margin-top:14px;background:#151a2e;border-radius:10px;overflow:hidden}}
th,td{{padding:9px 11px;border-bottom:1px solid #222a44}} th{{text-align:left;color:#9aa0b5;font-weight:600}}
.tot{{margin-top:12px;font-size:15px}}
</style>
<div class=wrap>
<h1>concilia-mx · clasificación de movimientos</h1>
<div class=sub>Foco: depósitos <b>no facturados</b> (candidatos a venta) y su costo de reclasificación.</div>
<div style=margin-top:12px>{chips}</div>
<div class=tot>No facturado detectado: <b>{_money(data.get('total_no_facturado',0))}</b> ·
Costo fiscal estimado de reclasificar todo: <b>{_money(data.get('costo_total_estimado',0))}</b></div>
<table><tr><th>Fecha</th><th>Descripción</th><th>Monto</th><th>IVA</th><th>ISR</th><th>Costo total</th></tr>
{filas}</table>
<div class=sub style=margin-top:14px>Cifras indicativas, pro-cumplimiento. El reconocimiento final lo valida un contador.</div>
</div>"""
