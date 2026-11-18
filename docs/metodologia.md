# Metodología

## Dos capas
- **Motor determinista (código + pruebas):** hace la partida doble, clasifica, estima
  costos y aplica los criterios de reconocimiento NIF. Es auditable: las reglas viven en
  `tests/golden/`.
- **Capa agente (skills, Markdown):** entrevista al dueño del negocio y **orquesta** el
  motor. No calcula ni decide reconocimiento por su cuenta.

Principio: *el agente conversa, el motor calcula.* Un skill nunca inventa un asiento ni
capitaliza un activo — solo el motor, y lo rechaza si no pasa el gate.

## Doble libro (interno ↔ fiscal)
Dos vistas de la MISMA realidad que **siempre se concilian**. El estado de cuenta bancario
es la fuente más fehaciente de la fecha real del movimiento. Cuando el libro interno
reconoce algo que el fiscal no (p.ej. un ingreso no facturado), la **brecha se cuantifica
y se muestra** — nunca se oculta — y se evalúa su remediación.

## Foco: clasificar lo no facturado
Para cada depósito el motor decide, con razón y confianza, si está `facturado`, es un
`marketplace_payout`, un `traspaso`, o **`no_facturado`** (candidato a venta). Para lo no
facturado estima el **costo fiscal de reconocerlo** (IVA + ISR, netando el COGS de la orden
de compra relacionada), con las tasas de las declaraciones del usuario.

## Gates de reconocimiento NIF (correctitud)
- **NIF C-6 (PPyE):** un consumible pasa a equipo solo si cumple vida útil > 12 meses +
  control + beneficio futuro + costo con factura. Si no, se queda como gasto/inventario.
- **NIF C-8 (intangibles):** solo se capitalizan los **adquiridos con costo confiable +
  identificables + control + evidencia**. Un intangible **generado internamente** (marca
  propia, listas de clientes, plusvalía) **no se reconoce**; a lo sumo se revela en notas.
- **NIF D-1 (ingresos):** el ingreso se reconoce al devengarse; reconocer lo no facturado
  **siempre emite una bandera de brecha fiscal**.
- **NIF C-9/C-19 (pasivos):** solo obligaciones reales; se depuran ficticios/duplicados.

## Aviso
Herramienta de apoyo, **no asesoría fiscal/contable**. El reconocimiento final lo valida un
contador antes de cualquier declaración.
