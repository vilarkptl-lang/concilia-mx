# concilia-mx

Toolkit **open-source** para vendedores en México (especialmente en marketplaces:
**Amazon, Mercado Libre, TikTok Shop**) que necesitan **conciliar y clasificar** sus
movimientos bancarios contra sus CFDI, sus payouts de marketplace y sus órdenes de
compra — y, sobre todo, **detectar ágilmente los depósitos NO facturados** y estimar el
**costo fiscal (IVA + ISR) de reconocerlos como ventas**.

Es una herramienta **pro-cumplimiento**: te dice, con cifras, cuánto cuesta ponerte al
día; no evade nada. El reconocimiento contable final lo valida tu contador.

## Clonar / fork (un comando)

```bash
git clone https://github.com/Vilarkptl-lang/concilia-mx.git && cd concilia-mx && python3 cli/conta.py demo
```

El núcleo **no requiere dependencias** (solo Python 3.10+ de stdlib). El `demo` corre con
datos de ejemplo y genera `out/report.html`.

## Qué hace

1. **Importa tus fuentes de verdad** — estado de cuenta (CSV), CFDI (histórico), payouts
   de marketplace (CSV de liquidación), órdenes de compra / pagos a proveedores.
2. **Clasifica cada movimiento** de forma determinista y explicable:
   `facturado` · `marketplace_payout` · `traspaso` · **`no_facturado`** (el foco) ·
   `pago_proveedor` · `gasto_facturado` · `sin_clasificar`.
3. **Aísla lo NO facturado** (depósitos sin CFDI ni payout = candidatos a venta) y
   **estima el costo de reclasificarlos** (IVA a pagar + ISR, netando el COGS de la orden
   de compra relacionada), según las tasas de tus declaraciones.
4. **Explota los payouts de marketplace** a venta bruta + comisiones + fees (el depósito
   que llega al banco es el NETO; el ingreso es el BRUTO).
5. **Dashboard interactivo** ([`web/dashboard.html`](web/dashboard.html)): clasifica cada
   depósito, asígnale concepto, y mira **en vivo** el impacto en ingresos/utilidad y en los
   impuestos a pagar (IVA + ISR) si lo reconoces. Carga tu `out/report.json` o úsalo con el demo.
6. (Opcional) **Conecta tus fuentes en vivo**: ventas de marketplaces
   ([`connectors/canalpulse_client.py`](connectors/canalpulse_client.py), read-only) y tu ERP
   ([`connectors/odoo_client.py`](connectors/odoo_client.py)); **publica pólizas** validadas a tu
   contabilidad en la nube ([`connectors/alegra_client.py`](connectors/alegra_client.py)). Las
   credenciales viven en tu `.env` (gitignored), nunca en el repo.

## Uso

```bash
# Con tus propios archivos:
python3 cli/conta.py clasificar \
  --banco estado_cuenta.csv \
  --cfdi cfdi.json \
  --marketplace mercadolibre:ml.csv amazon:amz.csv tiktok:tk.csv \
  --isr 0.30 --out out/
```

Formatos en [`examples/`](examples/). Columnas del banco: `fecha, descripcion, deposito,
retiro, referencia`. Payout: `periodo, bruto, comisiones, fees, retenciones, neto, referencia`.

## Descargar tus insumos fiscales

El histórico de CFDI y tus declaraciones se cargan desde una carpeta que exportas tú
(modo `local`, por defecto — ver [`connectors/fiscalai_adapter.py`](connectors/fiscalai_adapter.py)).
La descarga **automatizada** desde el SAT (con tu propia e.firma/CIEC) es un backend
externo y opcional; este repo nunca pide ni guarda tus credenciales del SAT.

## Correctitud: los "gates" NIF

El motor **no infla** los números: reglas con pruebas de oro ([`tests/golden/`](tests/golden/))
hacen cumplir los criterios de reconocimiento de las NIF —p.ej. **una marca generada
internamente NO se capitaliza** (NIF C-8), **un consumible solo pasa a equipo si cumple
vida útil + control + costo** (NIF C-6), y **todo ingreso reconocido sin factura emite una
bandera de brecha fiscal** (NIF D-1). Si alguien afloja un gate, los tests fallan.

## Arquitectura

```
engine/            motor determinista (money, ledger de partida doble, clasificación,
                   costo de reclasificación, reconocimiento NIF)
engine/ingest/     parsers: banco, marketplace, CFDI, órdenes de compra
connectors/        alegra_client (publicar pólizas) · fiscalai_adapter (insumos SAT)
reports/           reporte HTML/JSON (dashboard)
cli/ · api/        CLI y API opcional (FastAPI)
tests/golden/      candados de correctitud
```

## Aviso

Herramienta de apoyo; **no es asesoría fiscal ni contable**. Las cifras son indicativas y
deben validarse con tu contador antes de presentar cualquier declaración.

## Licencia

MIT — ver [LICENSE](LICENSE).
