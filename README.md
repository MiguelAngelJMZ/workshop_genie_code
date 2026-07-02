# Genie Code Workshop — PUC

Workshop práctico que enseña a los equipos de datos y analítica de la **Pontificia Universidad Católica de Chile (PUC)** cómo usar **Genie Code dentro de Databricks** para acelerar el trabajo diario en cuatro tracks:

- ⚙️ **Data Engineering** — pipelines medallion, ingestas desde SIGUC, Lakeflow Jobs
- 📊 **BI & Analytics** — SQL desde lenguaje natural, Metric Views, Genie Spaces, AI/BI Dashboards
- 🧠 **Data Science & ML** — EDA, feature engineering, MLflow, applyInPandas, forecasting de matrículas
- 🛡️ **Data Governance** — framework de data quality, CLS/RLS, Data Academy

Todo el contenido está en español y contextualizado al ecosistema universitario chileno de [UC](https://www.uc.cl/): campus, matrículas diarias, Mi Portal UC, campañas de admisión y KPIs por macro-zona.


## Estructura

| Archivo / Carpeta | Propósito |
|---|---|
| `generate_workshop_data.py` | Notebook Databricks que crea 5 tablas académicas en `workshop_genie_code.gold` con ~360 defectos de calidad intencionales. |
| `data/tracks.json` | Contenido activo: 4 tracks × 5 pasos (versión reducida ~2–3 h). |
| `data/tracks.full.json` | Respaldo con los 8 pasos originales por track. |
| `main.py` | Backend FastAPI que sirve `/api/tracks` y el frontend estático. |
| `frontend/index.html` | SPA con branding UC (azul institucional). |
| `frontend/img/` | Íconos de tracks, logo UC, símbolo Databricks. |
| `app.yaml` | Configuración para Databricks Apps (uvicorn en puerto 8000). |
| `requirements.txt` | FastAPI + uvicorn. |

## Dataset sintético

`workshop_genie_code.gold` se puebla con `generate_workshop_data.py` y contiene 5 tablas distribuidas en 7 macro-zonas UC (MET, ARA, BIO, VAL, NAC, SUR, DIG).

El mismo notebook crea el volume `workshop_genie_code.gold.raw` con el CSV `/Volumes/workshop_genie_code/gold/raw/new_campus.csv` (12 filas con defectos intencionales para el pipeline medallion del paso 2 DE). Los schemas `bronze` y `silver` los crea el participante al ejecutar ese ejercicio.

| Tabla | Descripción |
|---|---|
| `dim_campus` | ~60 campus/unidades UC con código UC, macro-zona, comuna, tipo y aulas habilitadas |
| `fact_matriculas_diarias` | Matrículas diarias por campus — solicitudes, ingresos CLP, becas, SLA, tasa de éxito |
| `fact_portal_uc_activity` | 200K actividades Mi Portal UC / Canvas — segmento, plan de estudio, canal, monto CLP |
| `fact_campanas_admision` | ~150 campañas de admisión (Pregrado, Magíster, UC Online) entre 2024 y 2026 |
| `fact_daily_kpis` | KPIs diarios por macro-zona — matrículas, ingresos, estudiantes activos, crecimiento YoY |

Cada tabla incluye defectos de calidad intencionales para el track de Governance (~360 en total).

## Convención de tablas en los prompts

- **Lectura (compartidas):** `workshop_genie_code.gold.<tabla>` — las 5 del setup
- **Escritura (personales):** `workshop_genie_code.<schema>.{nombre_usuario}_<tabla>`
- `{nombre_usuario}` = parte de `current_user()` antes del `@`, minúsculas, puntos → `_`
- `{current_user}` solo para rutas `/Workspace/Users/{current_user}/...`

## Ejecutar localmente

```bash
cd puc_geniecode
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Abre http://localhost:8000.

## Setup del workshop (facilitador)

Orden recomendado: **datos → permisos UC → app → permisos app → verificación**.

### Prerrequisitos

| Requisito | Detalle |
|---|---|
| **Rol** | Metastore admin o permisos para `CREATE CATALOG` en el workspace |
| **CLI** | [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/) v0.22+ |
| **Grupo de participantes** | Un grupo de workspace, p. ej. `puc_workshop_participants` (40 usuarios aprox.) |
| **Compute** | Cluster serverless o compartido para ejecutar `generate_workshop_data.py` |

Variables de entorno usadas en los ejemplos (ajústalas):

```bash
export DBX_PROFILE="<tu-perfil>"          # ej. fevm-classic-stable-rpm8ba
export DBX_HOST="https://<workspace>.cloud.databricks.com"
export DBX_USER="<tu-email>"              # ej. facilitador@empresa.com
export APP_NAME="puc-geniecode"
export REMOTE_PATH="/Workspace/Users/${DBX_USER}/puc_geniecode"
export PARTICIPANTS_GROUP="puc_workshop_participants"
```

### 1. Autenticación en el workspace

Si el workspace aún no está en `~/.databrickscfg`:

```bash
databricks auth login --host "$DBX_HOST" --profile "$DBX_PROFILE"
databricks current-user me --profile "$DBX_PROFILE"
```

### 2. Generar los datos del workshop

El notebook `generate_workshop_data.py` crea en Unity Catalog:

| Objeto | Nombre completo |
|---|---|
| Catálogo | `workshop_genie_code` |
| Schema (datos compartidos) | `workshop_genie_code.gold` |
| Volume (CSV de ingestión DE) | `workshop_genie_code.gold.raw` |
| CSV fuente | `/Volumes/workshop_genie_code/gold/raw/new_campus.csv` |
| Tablas compartidas (solo lectura) | `dim_campus`, `fact_matriculas_diarias`, `fact_portal_uc_activity`, `fact_campanas_admision`, `fact_daily_kpis` |

Los schemas `bronze` y `silver` **no** los crea el notebook; el facilitador debe crearlos antes del workshop (ver paso 3).

**Subir y ejecutar el notebook:**

```bash
# Subir el notebook al workspace (si aún no está)
databricks workspace import generate_workshop_data.py \
  "${REMOTE_PATH}/generate_workshop_data.py" \
  --format SOURCE --language PYTHON --overwrite \
  --profile "$DBX_PROFILE"
```

Luego en la UI de Databricks:

1. Abre `generate_workshop_data.py` como notebook.
2. Adjunta un cluster serverless o compartido.
3. Ejecuta todas las celdas (idempotente — usa `CREATE OR REPLACE TABLE`).

**Permisos del facilitador para este paso:** `CREATE CATALOG`, `CREATE SCHEMA`, `CREATE TABLE`, `CREATE VOLUME` (o metastore admin). Quien ejecuta el notebook queda como **owner** del catálogo.

### 3. Permisos del catálogo Unity Catalog

Ejecuta como **owner del catálogo** o metastore admin. Crea los schemas de medallion y otorga acceso al grupo de participantes.

```sql
-- ── Schemas de medallion (bronze/silver los crea el facilitador; gold ya existe) ──
CREATE SCHEMA IF NOT EXISTS workshop_genie_code.bronze;
CREATE SCHEMA IF NOT EXISTS workshop_genie_code.silver;

-- ── Acceso base al catálogo ──
GRANT USE CATALOG ON CATALOG workshop_genie_code TO `puc_workshop_participants`;

-- ── Schemas: uso + escritura de tablas personales ({nombre_usuario}_*) ──
GRANT USE SCHEMA ON SCHEMA workshop_genie_code.gold   TO `puc_workshop_participants`;
GRANT USE SCHEMA ON SCHEMA workshop_genie_code.bronze TO `puc_workshop_participants`;
GRANT USE SCHEMA ON SCHEMA workshop_genie_code.silver TO `puc_workshop_participants`;

GRANT CREATE TABLE, MODIFY ON SCHEMA workshop_genie_code.gold   TO `puc_workshop_participants`;
GRANT CREATE TABLE, MODIFY ON SCHEMA workshop_genie_code.bronze TO `puc_workshop_participants`;
GRANT CREATE TABLE, MODIFY ON SCHEMA workshop_genie_code.silver TO `puc_workshop_participants`;

-- ── Tablas compartidas: SOLO LECTURA (no otorgar MODIFY sobre estas tablas) ──
GRANT SELECT ON TABLE workshop_genie_code.gold.dim_campus              TO `puc_workshop_participants`;
GRANT SELECT ON TABLE workshop_genie_code.gold.fact_matriculas_diarias TO `puc_workshop_participants`;
GRANT SELECT ON TABLE workshop_genie_code.gold.fact_portal_uc_activity TO `puc_workshop_participants`;
GRANT SELECT ON TABLE workshop_genie_code.gold.fact_campanas_admision  TO `puc_workshop_participants`;
GRANT SELECT ON TABLE workshop_genie_code.gold.fact_daily_kpis          TO `puc_workshop_participants`;

-- ── Volume: lectura del CSV para el ejercicio DE (paso 2) ──
GRANT READ VOLUME ON VOLUME workshop_genie_code.gold.raw TO `puc_workshop_participants`;

-- ── Opcional: track Data Science (registro de modelos en UC) ──
GRANT CREATE MODEL ON SCHEMA workshop_genie_code.gold TO `puc_workshop_participants`;
```

**Resumen de permisos por rol:**

| Privilegio | Participantes | Facilitador |
|---|---|---|
| `USE CATALOG` | ✅ | ✅ |
| `USE SCHEMA` (gold, bronze, silver) | ✅ | ✅ |
| `SELECT` en las 5 tablas compartidas | ✅ | ✅ |
| `CREATE TABLE` / `MODIFY` en schemas | ✅ (tablas `{nombre_usuario}_*`) | ✅ |
| `READ VOLUME` en `gold.raw` | ✅ | ✅ |
| `CREATE MODEL` en `gold` | ✅ (opcional, track DS) | ✅ |
| `MODIFY` en tablas compartidas | ❌ | ✅ (owner) |

> **Convención:** cada participante escribe solo en tablas con prefijo `{nombre_usuario}_`. Las tablas compartidas en `workshop_genie_code.gold.*` (sin prefijo) son de solo lectura.

> **Track Governance (CLS/RLS):** los ejercicios generan el SQL pero no se ejecutan en el workshop porque requieren `OWN` en las tablas personales. No se necesitan grants adicionales para el día del evento.

### 4. Desplegar la Databricks App

La app es una SPA estática + API FastAPI (`/api/tracks`). No requiere SQL warehouse ni recursos adicionales en `app.yaml`.

**4.1 Subir el código al workspace** (excluye `.venv`):

```bash
cd puc_geniecode
rsync -a --exclude='.venv' --exclude='__pycache__' ./ /tmp/puc_geniecode_deploy/

databricks workspace import-dir /tmp/puc_geniecode_deploy "$REMOTE_PATH" \
  --overwrite --profile "$DBX_PROFILE"
```

**4.2 Crear la app** (solo la primera vez):

```bash
databricks apps create "$APP_NAME" \
  --description "Genie Code Workshop — PUC edition" \
  --profile "$DBX_PROFILE"
```

**4.3 Iniciar el compute de la app** (requerido antes del primer deploy):

```bash
databricks apps start "$APP_NAME" --profile "$DBX_PROFILE"
```

**4.4 Desplegar el código:**

```bash
databricks apps deploy "$APP_NAME" \
  --source-code-path "$REMOTE_PATH" \
  --profile "$DBX_PROFILE"
```

**4.5 Verificar estado y obtener la URL:**

```bash
databricks apps get "$APP_NAME" --profile "$DBX_PROFILE" -o json
databricks apps logs "$APP_NAME" --profile "$DBX_PROFILE"
```

Busca `"state": "RUNNING"` y `"state": "SUCCEEDED"` en el deployment. La URL tendrá la forma:

`https://puc-geniecode-<workspace-id>.aws.databricksapps.com`

### 5. Permisos de la App para participantes

Los participantes necesitan `CAN USE` en la app para abrirla con SSO del workspace.

**Opción A — UI:** *Compute → Apps → puc-geniecode → Permissions* → agrega el grupo `puc_workshop_participants` con **Can Use**. Mantén `Can Manage` solo para facilitadores.

**Opción B — CLI:**

```bash
databricks apps update-permissions "$APP_NAME" --profile "$DBX_PROFILE" --json '{
  "access_control_list": [
    {
      "group_name": "puc_workshop_participants",
      "permission_level": "CAN_USE"
    },
    {
      "user_name": "'"$DBX_USER"'",
      "permission_level": "CAN_MANAGE"
    }
  ]
}'
```

| Nivel | Quién | Para qué |
|---|---|---|
| `CAN USE` | Participantes | Abrir la app y seguir los tracks |
| `CAN MANAGE` | Facilitadores | Redesplegar, ver logs, cambiar permisos |

### 6. Verificación final

**App:**

```bash
databricks apps get "$APP_NAME" --profile "$DBX_PROFILE"
```

Abre la URL desde el workspace (requiere sesión activa de Databricks).

**Datos** (como participante de prueba):

```sql
SHOW TABLES IN workshop_genie_code.gold;
SELECT COUNT(*) FROM workshop_genie_code.gold.dim_campus;
LIST '/Volumes/workshop_genie_code/gold/raw';
```

**Tabla personales** (smoke test):

```sql
CREATE OR REPLACE TABLE workshop_genie_code.gold.<tu_usuario>_smoke_test AS
SELECT 1 AS ok;
DROP TABLE workshop_genie_code.gold.<tu_usuario>_smoke_test;
```

### Redespliegue tras cambios

Si modificas `tracks.json`, `frontend/` o `main.py`:

```bash
rsync -a --exclude='.venv' --exclude='__pycache__' ./ /tmp/puc_geniecode_deploy/
databricks workspace import-dir /tmp/puc_geniecode_deploy "$REMOTE_PATH" \
  --overwrite --profile "$DBX_PROFILE"
databricks apps deploy "$APP_NAME" \
  --source-code-path "$REMOTE_PATH" \
  --profile "$DBX_PROFILE"
```

Para regenerar solo los datos del workshop, re-ejecuta todas las celdas de `generate_workshop_data.py` (sobrescribe las tablas compartidas; no afecta tablas personales de participantes).

## Branding UC

Paleta alineada con [uc.cl](https://www.uc.cl/) — **azul institucional** con acento dorado:

| Token | Hex | Uso |
|---|---|---|
| Azul UC | `#003DA5` | Header, botones, acentos principales |
| Azul oscuro | `#001A5C` | Hero, footer, hover |
| Azul suave | `#E8EEF8` | Fondos secundarios, categorías |
| Dorado UC | `#C5A572` | Acentos en hero y footer |
| Tracks | `#E40006` / `#B0000B` / `#7C3AED` / `#0891B2` | DE / BI / DS / Gov |

Fuente: DM Sans (con DM Mono para bloques de código).
