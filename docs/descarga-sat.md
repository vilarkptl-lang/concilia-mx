# Descarga de insumos fiscales (declaraciones + CFDI)

`concilia-mx` necesita dos insumos del SAT para conciliar y estimar costos:
- **Histórico de CFDI** (emitidos y recibidos).
- **Declaraciones ya presentadas** (para tomar las tasas/bases reales del contribuyente).

## Modo `local` (por defecto, sin credenciales)
Exporta tú esos insumos a una carpeta y el adaptador los lee. No se tocan credenciales del
SAT. Estructura:

```
mis_insumos/
├─ declaraciones.json      # [{ejercicio, periodo, concepto, base, impuesto, ...}]
└─ cfdi/                    # *.xml (CFDI 3.3/4.0)
```

Ver `connectors/fiscalai_adapter.py` (`LocalBackend`).

## Modo automatizado (opcional, externo)
La descarga automatizada desde el SAT —con la **e.firma/CIEC del propio usuario**— es un
backend **externo** a este repo público. El punto de extensión está definido
(`get_backend(modo="...")`), pero este repositorio **no implementa ni almacena** esas
credenciales: cada usuario conecta su propio mecanismo de descarga. Así el repo queda
limpio, público y sin secretos.
