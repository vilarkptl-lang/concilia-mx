-- concilia-mx: esquema núcleo multi-tenant (NIF, doble libro, clasificación).
-- Postgres. Montos NUMERIC(18,2). Sin PII en el esquema (los documentos viven aparte).
CREATE SCHEMA IF NOT EXISTS conta;
SET search_path TO conta;

CREATE TABLE empresa (
  id            BIGSERIAL PRIMARY KEY,
  rfc           TEXT NOT NULL UNIQUE,
  razon_social  TEXT NOT NULL,
  regimen       TEXT,
  tasa_isr      NUMERIC(5,4) DEFAULT 0.30,
  creado        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cuenta (                       -- catálogo de cuentas por empresa
  empresa_id        BIGINT NOT NULL REFERENCES empresa(id),
  codigo            TEXT NOT NULL,
  nombre            TEXT NOT NULL,
  naturaleza        TEXT NOT NULL CHECK (naturaleza IN ('deudora','acreedora')),
  codigo_agrupador  TEXT,                   -- SAT Anexo 24
  PRIMARY KEY (empresa_id, codigo)
);

CREATE TABLE asiento (
  id            BIGSERIAL PRIMARY KEY,
  empresa_id    BIGINT NOT NULL REFERENCES empresa(id),
  fecha         DATE NOT NULL,
  descripcion   TEXT NOT NULL,
  libro         TEXT NOT NULL CHECK (libro IN ('interno','fiscal')),
  referencia    TEXT,                        -- llave natural / idempotencia
  origen        TEXT,                         -- banco|cfdi|marketplace|reconocimiento|manual
  creado        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (empresa_id, libro, referencia)
);

CREATE TABLE renglon (
  id            BIGSERIAL PRIMARY KEY,
  asiento_id    BIGINT NOT NULL REFERENCES asiento(id) ON DELETE CASCADE,
  cuenta        TEXT NOT NULL,
  debit         NUMERIC(18,2) NOT NULL DEFAULT 0,
  credit        NUMERIC(18,2) NOT NULL DEFAULT 0,
  descripcion   TEXT,
  CHECK (debit >= 0 AND credit >= 0),
  CHECK (NOT (debit > 0 AND credit > 0))
);

CREATE TABLE movimiento_banco (
  id            BIGSERIAL PRIMARY KEY,
  empresa_id    BIGINT NOT NULL REFERENCES empresa(id),
  fecha         DATE NOT NULL,
  descripcion   TEXT,
  deposito      NUMERIC(18,2) NOT NULL DEFAULT 0,
  retiro        NUMERIC(18,2) NOT NULL DEFAULT 0,
  referencia    TEXT,
  estado        TEXT,          -- facturado|marketplace_payout|traspaso|no_facturado|...
  confianza     TEXT,
  match_ref     TEXT,
  conciliado    BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE payout_marketplace (
  id            BIGSERIAL PRIMARY KEY,
  empresa_id    BIGINT NOT NULL REFERENCES empresa(id),
  marketplace   TEXT NOT NULL,              -- amazon|mercadolibre|tiktok
  periodo       TEXT NOT NULL,
  bruto         NUMERIC(18,2) NOT NULL,
  comisiones    NUMERIC(18,2) NOT NULL DEFAULT 0,
  fees          NUMERIC(18,2) NOT NULL DEFAULT 0,
  retenciones   NUMERIC(18,2) NOT NULL DEFAULT 0,
  neto          NUMERIC(18,2) NOT NULL,
  referencia    TEXT
);

CREATE TABLE orden_compra (
  id            BIGSERIAL PRIMARY KEY,
  empresa_id    BIGINT NOT NULL REFERENCES empresa(id),
  proveedor     TEXT,
  fecha         DATE,
  monto         NUMERIC(18,2) NOT NULL,
  con_iva       BOOLEAN NOT NULL DEFAULT true,
  referencia    TEXT
);

CREATE TABLE ajuste_reconocimiento (        -- bitácora de las palancas NIF
  id              BIGSERIAL PRIMARY KEY,
  empresa_id      BIGINT NOT NULL REFERENCES empresa(id),
  palanca         TEXT NOT NULL,            -- c6_ppye|c8_intangibles|d1_ingreso|c9_pasivos
  base_nif        TEXT NOT NULL,
  aceptado        BOOLEAN NOT NULL,
  razon           TEXT NOT NULL,
  asiento_id      BIGINT REFERENCES asiento(id),
  nota_revelacion TEXT,
  creado          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evidencia (
  id            BIGSERIAL PRIMARY KEY,
  empresa_id    BIGINT NOT NULL REFERENCES empresa(id),
  ajuste_id     BIGINT REFERENCES ajuste_reconocimiento(id),
  tipo          TEXT NOT NULL,              -- factura|contrato|cep|acta|estado_cuenta
  ref           TEXT NOT NULL,              -- ruta en el almacén gateado del usuario
  sha256        TEXT,
  creado        TIMESTAMPTZ NOT NULL DEFAULT now()
);
