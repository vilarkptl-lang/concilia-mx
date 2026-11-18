# skill: clasificación de movimientos (capa agente)

Capa de conversación que **maneja el motor** `engine/clasificacion.py` — no calcula por su
cuenta. El agente entrevista al dueño del negocio y orquesta el pipeline.

## Objetivo
Identificar ágilmente los **depósitos NO facturados** (candidatos a venta) y orientar el
**costo fiscal de reclasificarlos**, con las fuentes de verdad del usuario.

## Receta
1. Pide/carga las fuentes: estado de cuenta (CSV), CFDI (histórico), payouts de
   marketplace (CSV de liquidación), órdenes de compra. Si falta algo, dilo; no inventes.
2. Corre `cli/conta.py clasificar …` (o la API). El motor devuelve el estado de cada
   movimiento con **razón y confianza**.
3. Para cada `no_facturado`, pregunta al dueño: ¿es venta? ¿hay orden de compra (COGS)
   relacionada? Con eso llama al estimador de costo (`engine/costo_reclasificacion.py`).
4. Presenta el reporte: cuánto hay no facturado, el costo de ponerse al día, y qué casó
   con CFDI/payout/proveedor. **No reclasifiques nada en firme sin el visto del contador.**

## Invariantes
- El motor hace cumplir los gates NIF; el agente **no** los sortea.
- Datos del usuario en su almacén gateado; nunca al canal ni al repo.
- Cifras indicativas; el reconocimiento formal lo valida un contador.
