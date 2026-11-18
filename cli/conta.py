#!/usr/bin/env python3
"""concilia-mx — CLI.

Pipeline: importa banco (+ CFDI + payouts) -> clasifica -> aísla lo NO facturado ->
estima el costo fiscal de reclasificarlo como venta -> escribe report.json + report.html.

Uso:
  python3 cli/conta.py demo                         # corre con datos de ejemplo
  python3 cli/conta.py clasificar --banco banco.csv [--cfdi cfdi.json] \
      [--marketplace mercadolibre:ml.csv] [--isr 0.30] [--out out/]
"""
import argparse
import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ingest import banco as banco_ingest           # noqa: E402
from engine.ingest import marketplace as mp_ingest         # noqa: E402
from engine import clasificacion as clf                    # noqa: E402
from engine.costo_reclasificacion import estimar           # noqa: E402
from reports import reporte_html                            # noqa: E402


def _load_cfdi(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [clf.CFDI(uuid=x["uuid"], tipo=x.get("tipo", "I"), fecha=x["fecha"],
                         total=Decimal(str(x["total"])), contraparte=x.get("contraparte", ""),
                         referencia=x.get("referencia", "")) for x in json.load(f)]


def _load_marketplace(specs):
    payouts = []
    for spec in specs or []:
        mkt, _, path = spec.partition(":")
        payouts += mp_ingest.parse_csv(path, mkt)
    return payouts


def run(banco_csv, cfdi_path, mp_specs, tasa_isr, out_dir,
        cuentas_propias=None, proveedores=None):
    movs = banco_ingest.parse_csv(banco_csv)
    cfdis = _load_cfdi(cfdi_path)
    payouts = _load_marketplace(mp_specs)
    clasifs = clf.clasificar_todo(movs, cfdis, payouts, cuentas_propias, proveedores)
    by_id = {c.mov_id: c for c in clasifs}

    candidatos, total_nf, costo_total = [], Decimal("0"), Decimal("0")
    for m in movs:
        c = by_id[m.id]
        if c.estado == clf.NO_FACTURADO:
            co = estimar(m.deposito, tasa_isr=Decimal(str(tasa_isr)))
            total_nf += m.deposito
            costo_total += co.costo_total
            candidatos.append({
                "fecha": m.fecha, "descripcion": m.descripcion, "monto": str(m.deposito),
                "costo": {"iva_a_pagar": str(co.iva_a_pagar), "isr": str(co.isr),
                          "costo_total": str(co.costo_total)}})

    data = {"resumen": clf.resumen(clasifs),
            "total_no_facturado": str(total_nf),
            "costo_total_estimado": str(costo_total),
            "candidatos": candidatos}

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "report.html"), "w", encoding="utf-8") as f:
        f.write(reporte_html.generar(data))

    print("Resumen de clasificación:", json.dumps(data["resumen"], ensure_ascii=False))
    print(f"NO facturado: ${total_nf:,.2f}  ·  costo fiscal estimado de reclasificar: "
          f"${costo_total:,.2f}")
    print(f"Reporte -> {os.path.join(out_dir, 'report.html')}")


def main():
    ap = argparse.ArgumentParser(description="concilia-mx")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo")
    d.add_argument("--out", default="out")
    c = sub.add_parser("clasificar")
    c.add_argument("--banco", required=True)
    c.add_argument("--cfdi")
    c.add_argument("--marketplace", nargs="*", default=[])
    c.add_argument("--isr", default="0.30")
    c.add_argument("--out", default="out")
    a = ap.parse_args()
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if a.cmd == "demo":
        ex = os.path.join(base, "examples")
        run(os.path.join(ex, "banco.csv"), os.path.join(ex, "cfdi.json"),
            [f"mercadolibre:{os.path.join(ex, 'mercadolibre.csv')}"], "0.30", a.out,
            cuentas_propias=["cuenta propia"], proveedores=["proveedor"])
    else:
        run(a.banco, a.cfdi, a.marketplace, a.isr, a.out)


if __name__ == "__main__":
    main()
