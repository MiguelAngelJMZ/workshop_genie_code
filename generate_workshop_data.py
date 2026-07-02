# Databricks notebook source
# MAGIC %md
# MAGIC # Workshop Data Generator — PUC Genie Code Workshop
# MAGIC
# MAGIC Generates 5 synthetic UC-themed tables in `workshop_genie_code.gold`,
# MAGIC plus volume `raw` and CSV `new_campus.csv` for the DE ingest exercise.
# MAGIC Includes intentional data quality issues for the Governance track.
# MAGIC
# MAGIC **Idempotent** — safe to re-run. Uses `CREATE OR REPLACE TABLE`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

CATALOG = "workshop_genie_code"
SCHEMA = "gold"
VOLUME_NAME = "raw"

# Macro-zonas de la Pontificia Universidad Católica de Chile
REGIONS = {
    "MET": {"region_name": "Región Metropolitana", "campuses": 14, "sites": [
        ("MET-CC", "Casa Central Alameda", "Santiago"),
        ("MET-OR", "Campus Oriente", "Santiago"),
        ("MET-SJ", "Campus San Joaquín", "Santiago"),
        ("MET-LC", "Lo Contador", "Santiago"),
        ("MET-CE", "Centro de Extensión Alameda", "Santiago"),
        ("MET-DA", "Facultad Derecho", "Santiago"),
        ("MET-ME", "Facultad Medicina", "Santiago"),
        ("MET-IN", "Facultad Ingeniería", "Santiago"),
        ("MET-AR", "Facultad Arquitectura", "Santiago"),
        ("MET-TE", "Facultad Teología", "Santiago"),
        ("MET-EC", "Facultad Economía y Administración", "Santiago"),
        ("MET-CS", "Facultad Ciencias Sociales", "Santiago"),
        ("MET-AG", "Facultad Agronomía", "Santiago"),
        ("MET-ED", "Facultad Educación", "Santiago"),
    ]},
    "ARA": {"region_name": "Araucanía", "campuses": 8, "sites": [
        ("ARA-VI", "Campus Villarrica", "Villarrica"),
        ("ARA-PU", "Extensión Pucón", "Pucón"),
        ("ARA-TE", "Extensión Temuco", "Temuco"),
        ("ARA-VL", "Extensión Villarrica Centro", "Villarrica"),
        ("ARA-LQ", "Extensión Lago Villarrica", "Villarrica"),
        ("ARA-AN", "Extensión Angol", "Angol"),
        ("ARA-PA", "Extensión Padre Las Casas", "Padre Las Casas"),
        ("ARA-PU2", "Programa Turismo Villarrica", "Villarrica"),
    ]},
    "BIO": {"region_name": "Biobío", "campuses": 8, "sites": [
        ("BIO-CC", "Extensión Concepción", "Concepción"),
        ("BIO-TA", "Extensión Talcahuano", "Talcahuano"),
        ("BIO-CH", "Extensión Chillán", "Chillán"),
        ("BIO-LO", "Extensión Los Ángeles", "Los Ángeles"),
        ("BIO-LE", "Extensión Lebu", "Lebu"),
        ("BIO-AR", "Extensión Arauco", "Arauco"),
        ("BIO-CO", "Extensión Coronel", "Coronel"),
        ("BIO-SA", "Extensión San Pedro de la Paz", "San Pedro de la Paz"),
    ]},
    "VAL": {"region_name": "Valparaíso", "campuses": 8, "sites": [
        ("VAL-VI", "Extensión Viña del Mar", "Viña del Mar"),
        ("VAL-VA", "Extensión Valparaíso", "Valparaíso"),
        ("VAL-QE", "Extensión Quillota", "Quillota"),
        ("VAL-SA", "Extensión San Antonio", "San Antonio"),
        ("VAL-LC", "Extensión La Calera", "La Calera"),
        ("VAL-QU", "Extensión Quilpué", "Quilpué"),
        ("VAL-LL", "Extensión Los Andes", "Los Andes"),
        ("VAL-CA", "Extensión Casablanca", "Casablanca"),
    ]},
    "NAC": {"region_name": "Macrozona Norte", "campuses": 8, "sites": [
        ("NAC-LQ", "Extensión La Serena", "La Serena"),
        ("NAC-CO", "Extensión Coquimbo", "Coquimbo"),
        ("NAC-AN", "Extensión Antofagasta", "Antofagasta"),
        ("NAC-IQ", "Extensión Iquique", "Iquique"),
        ("NAC-AR", "Extensión Arica", "Arica"),
        ("NAC-CA", "Extensión Calama", "Calama"),
        ("NAC-OV", "Extensión Ovalle", "Ovalle"),
        ("NAC-CO2", "Extensión Copiapó", "Copiapó"),
    ]},
    "SUR": {"region_name": "Macrozona Sur", "campuses": 8, "sites": [
        ("SUR-PU", "Extensión Puerto Montt", "Puerto Montt"),
        ("SUR-OS", "Extensión Osorno", "Osorno"),
        ("SUR-VA", "Extensión Valdivia", "Valdivia"),
        ("SUR-CY", "Extensión Coyhaique", "Coyhaique"),
        ("SUR-PU2", "Extensión Punta Arenas", "Punta Arenas"),
        ("SUR-CH", "Extensión Chiloé", "Castro"),
        ("SUR-AN", "Extensión Ancud", "Ancud"),
        ("SUR-PU3", "Extensión Puerto Varas", "Puerto Varas"),
    ]},
    "DIG": {"region_name": "UC Online / Digital", "campuses": 6, "sites": [
        ("DIG-ON", "UC Online Hub", "Santiago"),
        ("DIG-ED", "Educación Continua Digital", "Santiago"),
        ("DIG-MG", "Magísteres Online", "Santiago"),
        ("DIG-IA", "Nodo IA UC", "Santiago"),
        ("DIG-EX", "Extensión Digital Nacional", "Santiago"),
        ("DIG-CE", "Capacitación Corporativa", "Santiago"),
    ]},
}

CAMPUS_TYPES = ["Casa Central", "Campus Regional", "Centro Extensión", "Digital Hub", "Investigación"]
STUDENT_SEGMENTS = ["Pregrado", "Magíster", "Doctorado", "Educación Continua", "UC Online"]
ACTIVITY_TYPES = ["Inscripción Curso", "Consulta Académica", "Pago Arancel", "Reserva Biblioteca", "Acceso Canvas", "Trámite Secretaría"]
PLAN_ESTUDIO = ["Plan Regular", "Intercambio", "Beca Excelencia", "Programa Especial", "Doble Titulación"]
CHANNELS = ["Mi Portal UC", "Canvas UC", "Presencial", "UC Online", "App Móvil UC"]
DISCOUNT_TYPES = ["percentage", "fixed_amount", "beca_parcial", "matricula_cero"]
PRODUCTOS_ANCILLARY = ["Certificación", "Taller", "Diplomado", "Evento", "Investigación", "Mentoría"]

print(f"Target: {CATALOG}.{SCHEMA}")
print(f"Total campus/unidades: {sum(r['campuses'] for r in REGIONS.values())}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Catalog & Schema

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME_NAME}")
print(f"✅ {CATALOG}.{SCHEMA} ready")
print(f"✅ volume {CATALOG}.{SCHEMA}.{VOLUME_NAME} ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Raw CSV for DE ingest exercise (`new_campus.csv`)

# COMMAND ----------

import pandas as pd

NEW_CAMPUS_ROWS = [
    {"campus_id": "CAM-MET-0991", "codigo_uc": "met-nw", "region": "MET", "region_nombre": "Región Metropolitana", "comuna": "Santiago", "localidad": "Ñuñoa", "tipo_campus": "digital hub", "fecha_inauguracion": "2025-11-01", "latitude": -33.4569, "longitude": -70.6483, "es_24x7": True, "aulas_habilitadas": 12, "capacidad_estudiantes_anual": 4500},
    {"campus_id": "CAM-VAL-0992", "codigo_uc": "val-vi", "region": "VAL", "region_nombre": "Valparaíso", "comuna": "Viña del Mar", "localidad": "Reñaca", "tipo_campus": "centro extensión", "fecha_inauguracion": "2024-03-15", "latitude": -32.9667, "longitude": -71.5500, "es_24x7": False, "aulas_habilitadas": 8, "capacidad_estudiantes_anual": 2200},
    {"campus_id": "CAM-BIO-0993", "codigo_uc": "bio-ch", "region": "BIO", "region_nombre": "Biobío", "comuna": "Chillán", "localidad": "Chillán Centro", "tipo_campus": "campus regional", "fecha_inauguracion": "2023-08-20", "latitude": -36.6067, "longitude": -72.1034, "es_24x7": False, "aulas_habilitadas": 10, "capacidad_estudiantes_anual": 3100},
    {"campus_id": "CAM-ARA-0994", "codigo_uc": "ara-pu", "region": None, "region_nombre": "Araucanía", "comuna": "Pucón", "localidad": "Pucón", "tipo_campus": "Centro Extensión", "fecha_inauguracion": "2022-01-10", "latitude": -39.2820, "longitude": -71.9545, "es_24x7": False, "aulas_habilitadas": 6, "capacidad_estudiantes_anual": 900},
    {"campus_id": "CAM-NAC-0995", "codigo_uc": "nac-lq", "region": "NAC", "region_nombre": "Macrozona Norte", "comuna": "La Serena", "localidad": "La Serena", "tipo_campus": "investigación", "fecha_inauguracion": "2021-06-30", "latitude": -29.9027, "longitude": -71.2519, "es_24x7": True, "aulas_habilitadas": 14, "capacidad_estudiantes_anual": 2800},
    {"campus_id": "CAM-SUR-0996", "codigo_uc": "sur-pm", "region": "SUR", "region_nombre": "Macrozona Sur", "comuna": "Puerto Montt", "localidad": "Puerto Montt", "tipo_campus": "Digital Hub", "fecha_inauguracion": "2025-02-14", "latitude": -41.4693, "longitude": -72.9424, "es_24x7": True, "aulas_habilitadas": 8, "capacidad_estudiantes_anual": 1600},
    {"campus_id": "CAM-MET-0997", "codigo_uc": "met-rg", "region": "MET", "region_nombre": "Región Metropolitana", "comuna": "Santiago", "localidad": "Providencia", "tipo_campus": "centro extensión", "fecha_inauguracion": "2020-12-01", "latitude": -33.4372, "longitude": -70.6340, "es_24x7": False, "aulas_habilitadas": 6, "capacidad_estudiantes_anual": 1200},
    {"campus_id": "CAM-MET-0998", "codigo_uc": "met-cc2", "region": "MET", "region_nombre": "Región Metropolitana", "comuna": "Santiago", "localidad": "Centro Histórico", "tipo_campus": "Casa Central", "fecha_inauguracion": "1888-02-11", "latitude": -33.4417, "longitude": -70.6536, "es_24x7": True, "aulas_habilitadas": 40, "capacidad_estudiantes_anual": 18000},
    {"campus_id": "CAM-VAL-0999", "codigo_uc": "val-ol", "region": None, "region_nombre": "Valparaíso", "comuna": "Valparaíso", "localidad": "Playa Ancha", "tipo_campus": "centro extensión", "fecha_inauguracion": "2024-09-09", "latitude": -33.0472, "longitude": -71.6127, "es_24x7": False, "aulas_habilitadas": 5, "capacidad_estudiantes_anual": 850},
    {"campus_id": "CAM-DIG-1000", "codigo_uc": "dig-ia", "region": "DIG", "region_nombre": "UC Online / Digital", "comuna": "Santiago", "localidad": "Nodo IA UC", "tipo_campus": "digital hub", "fecha_inauguracion": "2026-01-15", "latitude": -33.4410, "longitude": -70.6500, "es_24x7": True, "aulas_habilitadas": 4, "capacidad_estudiantes_anual": 5000},
    {"campus_id": "CAM-MET-0991", "codigo_uc": "met-dup", "region": "MET", "region_nombre": "Región Metropolitana", "comuna": "Santiago", "localidad": "Duplicado", "tipo_campus": "centro extensión", "fecha_inauguracion": "2025-12-01", "latitude": -33.4400, "longitude": -70.6400, "es_24x7": False, "aulas_habilitadas": 2, "capacidad_estudiantes_anual": 200},
    {"campus_id": "CAM-ARA-1001", "codigo_uc": "ara-te", "region": "ARA", "region_nombre": "Araucanía", "comuna": "Temuco", "localidad": "Temuco", "tipo_campus": "Centro Extensión", "fecha_inauguracion": "2022-11-11", "latitude": -38.7359, "longitude": -72.5904, "es_24x7": False, "aulas_habilitadas": 7, "capacidad_estudiantes_anual": 1100},
]

df_new_campus = pd.DataFrame(NEW_CAMPUS_ROWS)
csv_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}/new_campus.csv"
tmp_dir = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}/_tmp_new_campus"

(
    spark.createDataFrame(df_new_campus)
    .coalesce(1)
    .write.mode("overwrite")
    .option("header", True)
    .csv(tmp_dir)
)

part_file = next(f.path for f in dbutils.fs.ls(tmp_dir) if f.name.startswith("part-"))
dbutils.fs.cp(part_file, csv_path)
dbutils.fs.rm(tmp_dir, recurse=True)

print(f"✅ {csv_path} written ({len(df_new_campus)} rows, incl. 2 null regions + 1 duplicate ID)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table 1: dim_campus

# COMMAND ----------

import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

LAT_RANGES = {"MET": (-34, -33), "ARA": (-40, -38), "BIO": (-37, -36),
              "VAL": (-33, -32), "NAC": (-30, -18), "SUR": (-54, -40), "DIG": (-34, -33)}
LON_RANGES = {"MET": (-71, -70), "ARA": (-73, -71), "BIO": (-73, -72),
              "VAL": (-72, -71), "NAC": (-71, -69), "SUR": (-74, -70), "DIG": (-71, -70)}

rows = []
campus_seq = 0

for region_code, info in REGIONS.items():
    for i in range(info["campuses"]):
        codigo, localidad, comuna = info["sites"][i % len(info["sites"])]
        campus_seq += 1
        campus_id = f"CAM-{region_code}-{campus_seq:04d}"
        ctype = np.random.choice(CAMPUS_TYPES, p=[0.08, 0.45, 0.25, 0.12, 0.10])
        opened = date(1888, 1, 1) + timedelta(days=int(np.random.uniform(0, 365 * 138)))
        lat = round(np.random.uniform(*LAT_RANGES[region_code]), 6)
        lon = round(np.random.uniform(*LON_RANGES[region_code]), 6)
        is_24x7 = np.random.random() < 0.30
        n_aulas = int(np.random.choice([4, 8, 12, 16, 24, 32], p=[0.20, 0.30, 0.25, 0.12, 0.08, 0.05]))
        capacidad_anual = int(n_aulas * np.random.uniform(120, 450))

        rows.append({
            "campus_id": campus_id,
            "codigo_uc": codigo,
            "campus_nombre": f"UC {localidad}",
            "region": region_code,
            "region_nombre": info["region_name"],
            "comuna": comuna,
            "localidad": localidad,
            "tipo_campus": ctype,
            "fecha_inauguracion": opened,
            "latitude": lat,
            "longitude": lon,
            "es_24x7": is_24x7,
            "aulas_habilitadas": n_aulas,
            "capacidad_estudiantes_anual": capacidad_anual,
        })

df_campus = pd.DataFrame(rows)

null_idx = np.random.choice(len(df_campus), 15, replace=False)
df_campus.loc[null_idx, "region"] = None

future_idx = np.random.choice(len(df_campus), 8, replace=False)
df_campus.loc[future_idx, "fecha_inauguracion"] = pd.Timestamp("2027-06-15").date()

zero_idx = np.random.choice(len(df_campus), 12, replace=False)
df_campus.loc[zero_idx, ["latitude", "longitude"]] = 0.0

dup_idx = np.random.choice(len(df_campus), 5, replace=False)
for idx in dup_idx:
    source_idx = np.random.choice([i for i in range(len(df_campus)) if i != idx])
    df_campus.loc[idx, "campus_id"] = df_campus.loc[source_idx, "campus_id"]

case_idx = np.random.choice(len(df_campus), 20, replace=False)
df_campus.loc[case_idx, "tipo_campus"] = df_campus.loc[case_idx, "tipo_campus"].str.lower()

outlier_idx = np.random.choice(len(df_campus), 8, replace=False)
outlier_vals = [0, 0, -2, 80, 120, 500, 999, -5]
for i, idx in enumerate(outlier_idx):
    df_campus.loc[idx, "aulas_habilitadas"] = outlier_vals[i]

print(f"dim_campus: {len(df_campus)} rows")
print(f"  DQ issues: 15 null regions, 8 future dates, 12 zero coords, 5 dup IDs, 20 bad casing, 8 aulas outliers")

sdf = spark.createDataFrame(df_campus)
sdf.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.dim_campus")
print(f"✅ {CATALOG}.{SCHEMA}.dim_campus written")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table 2: fact_matriculas_diarias

# COMMAND ----------

valid_campus = df_campus.dropna(subset=["region"])["campus_id"].unique().tolist()
campus_region = df_campus.set_index("campus_id")["region"].to_dict()

date_range = pd.date_range("2024-01-01", "2026-04-13", freq="D")
all_ops = []

sample_campus = valid_campus[:int(len(valid_campus) * 0.7)]

for campus_id in sample_campus:
    region = campus_region.get(campus_id, "MET")
    base_ops = {"MET": 1800, "ARA": 900, "BIO": 1100, "VAL": 1000, "NAC": 700, "SUR": 650, "DIG": 2200}.get(region, 800)
    base_ticket = {"MET": 420000, "ARA": 380000, "BIO": 390000, "VAL": 400000, "NAC": 360000, "SUR": 370000, "DIG": 350000}.get(region, 380000)

    for d in date_range:
        dow_mult = {0: 1.10, 1: 1.05, 2: 1.00, 3: 1.02, 4: 1.08, 5: 0.60, 6: 0.40}[d.dayofweek]
        month_mult = {1: 0.85, 2: 0.90, 3: 1.15, 4: 1.05, 5: 0.95, 6: 0.80,
                      7: 0.75, 8: 1.20, 9: 1.10, 10: 0.95, 11: 0.90, 12: 0.70}[d.month]
        years_from_start = (d - pd.Timestamp("2024-01-01")).days / 365
        growth = 1 + 0.04 * years_from_start
        noise = np.random.normal(1.0, 0.10)

        n_ops = max(int(base_ops * dow_mult * month_mult * growth * noise), 1)
        tasa_exito = round(np.clip(np.random.normal(0.96, 0.02), 0.85, 1.0), 3)
        matriculas = int(n_ops * tasa_exito)
        arancel_promedio = round(base_ticket * month_mult * np.random.normal(1.0, 0.10), 2)
        ingreso = round(matriculas * arancel_promedio, 2)
        sla_pct = round(np.clip(np.random.normal(0.95, 0.03), 0.80, 1.0), 3)
        rechazadas = int(n_ops * np.random.uniform(0, 0.05))
        becas = round(ingreso * np.random.uniform(0.05, 0.18), 2)
        costo_proc = round(ingreso * np.random.uniform(0.02, 0.08), 2)

        all_ops.append({
            "fecha_matricula": d.date(),
            "campus_id": campus_id,
            "solicitudes_totales": n_ops,
            "solicitudes_rechazadas": rechazadas,
            "matriculas_exitosas": matriculas,
            "tasa_exito_pct": tasa_exito,
            "arancel_promedio_clp": arancel_promedio,
            "ingreso_matricula_clp": ingreso,
            "monto_becas_clp": becas,
            "costo_procesamiento_clp": costo_proc,
            "sla_cumplimiento_pct": sla_pct,
        })

df_ops = pd.DataFrame(all_ops)

zero_vol_idx = np.random.choice(len(df_ops), 200, replace=False)
df_ops.loc[zero_vol_idx, "ingreso_matricula_clp"] = 0.0

neg_ticket_idx = np.random.choice(len(df_ops), 50, replace=False)
df_ops.loc[neg_ticket_idx, "arancel_promedio_clp"] = -1.0

null_date_idx = np.random.choice(len(df_ops), 30, replace=False)
df_ops.loc[null_date_idx, "fecha_matricula"] = None

bad_sla_idx = np.random.choice(len(df_ops), 40, replace=False)
df_ops.loc[bad_sla_idx, "sla_cumplimiento_pct"] = df_ops.loc[bad_sla_idx, "sla_cumplimiento_pct"] + 0.20

print(f"fact_matriculas_diarias: {len(df_ops)} rows")
print(f"  DQ issues: 200 zero ingreso, 50 negative aranceles, 30 null dates, 40 bad sla_pct")

sdf_ops = spark.createDataFrame(df_ops)
sdf_ops.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.fact_matriculas_diarias")
print(f"✅ {CATALOG}.{SCHEMA}.fact_matriculas_diarias written")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table 3: fact_portal_uc_activity

# COMMAND ----------

activity_rows = []
n_estudiantes = 5000
estudiante_ids = [f"EST-{np.random.choice(list(REGIONS.keys()))}-{i:07d}" for i in range(1, n_estudiantes + 1)]
activity_dates = pd.date_range("2025-10-01", "2026-04-13", freq="D")

for _ in range(200000):
    eid = np.random.choice(estudiante_ids)
    region_code = eid.split("-")[1]
    origen = np.random.choice(sample_campus)
    destino = np.random.choice(sample_campus)
    ad = pd.Timestamp(np.random.choice(activity_dates)).date()
    segmento = np.random.choice(STUDENT_SEGMENTS, p=[0.55, 0.18, 0.07, 0.12, 0.08])
    tipo_actividad = np.random.choice(ACTIVITY_TYPES, p=[0.25, 0.20, 0.15, 0.12, 0.18, 0.10])
    plan = np.random.choice(PLAN_ESTUDIO, p=[0.40, 0.15, 0.15, 0.15, 0.15])
    sesiones = int(np.random.uniform(1, 20))
    creditos_ganados = int(np.random.uniform(0, 12))
    monto = round(np.random.uniform(50000, 3500000), 2)
    ancillary = np.random.choice(PRODUCTOS_ANCILLARY + [None], p=[0.15, 0.15, 0.12, 0.10, 0.10, 0.08, 0.30])
    channel = np.random.choice(CHANNELS, p=[0.35, 0.30, 0.15, 0.12, 0.08])

    activity_rows.append({
        "fecha_actividad": ad,
        "estudiante_id": eid,
        "campus_origen_id": origen,
        "campus_destino_id": destino,
        "region": region_code,
        "segmento_estudiante": segmento,
        "tipo_actividad": tipo_actividad,
        "plan_estudio": plan,
        "sesiones_portal": sesiones,
        "creditos_registrados": creditos_ganados,
        "monto_clp": monto,
        "producto_ancillary": ancillary,
        "canal": channel,
    })

df_portal = pd.DataFrame(activity_rows)

tier_case_idx = np.random.choice(len(df_portal), 100, replace=False)
df_portal.loc[tier_case_idx, "segmento_estudiante"] = df_portal.loc[tier_case_idx, "segmento_estudiante"].str.lower()

neg_pts_idx = np.random.choice(len(df_portal), 40, replace=False)
df_portal.loc[neg_pts_idx, "creditos_registrados"] = -3

orphan_idx = np.random.choice(len(df_portal), 25, replace=False)
df_portal.loc[orphan_idx, "region"] = "XX"
df_portal.loc[orphan_idx, "estudiante_id"] = "EST-XX-0000000"

fake_cids = [f"CAM-ZZ-{9000+i:04d}" for i in range(80)]
ref_break_idx = np.random.choice(len(df_portal), 80, replace=False)
for i, idx in enumerate(ref_break_idx):
    df_portal.loc[idx, "campus_origen_id"] = fake_cids[i]

print(f"fact_portal_uc_activity: {len(df_portal)} rows")
print(f"  DQ issues: 100 lowercase segmentos, 40 negative creditos, 25 orphan XX, 80 ref breaks")

sdf_portal = spark.createDataFrame(df_portal)
sdf_portal.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.fact_portal_uc_activity")
print(f"✅ {CATALOG}.{SCHEMA}.fact_portal_uc_activity written")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table 4: fact_campanas_admision

# COMMAND ----------

campana_rows = []
campana_names = [
    "Admisión 2026 Pregrado", "Beca Excelencia Académica", "Magísteres Online UC",
    "Nodo IA para la Comunidad", "Semana UC Abierta", "Feria Vocacional UC",
    "Programa Interculturalidad", "Educación Continua Verano", "Open Day San Joaquín",
    "Aniversario UC", "Combo UC Online + Certificación", "Investigación Jóvenes",
    "Matrícula cero Educación Continua", "Doble puntos Mi Portal UC", "Alianza Empresas UC",
]

for year in [2024, 2025, 2026]:
    n_campanas = 60 if year < 2026 else 30
    for i in range(n_campanas):
        start = date(year, 1, 1) + timedelta(days=int(np.random.uniform(0, 330 if year < 2026 else 100)))
        duration = int(np.random.uniform(7, 45))
        end = start + timedelta(days=duration)
        region = np.random.choice(list(REGIONS.keys()) + ["ALL"], p=[0.10]*7 + [0.30])
        dtype = np.random.choice(DISCOUNT_TYPES, p=[0.45, 0.25, 0.20, 0.10])
        dval = {"percentage": np.random.choice([5, 10, 15, 20, 30, 50]),
                "fixed_amount": np.random.choice([50000, 150000, 500000, 1000000, 2500000]),
                "beca_parcial": np.random.choice([25, 35, 45, 55]),
                "matricula_cero": 0}[dtype]
        target_segment = np.random.choice([None, "Magíster", "Doctorado", "Educación Continua", "UC Online"], p=[0.40, 0.15, 0.10, 0.20, 0.15])
        target_program = np.random.choice([None, "Pregrado", "Magíster", "Doctorado", "Educación Continua"], p=[0.50, 0.20, 0.15, 0.10, 0.05])
        conversiones = int(np.random.uniform(50, 6000))
        presupuesto = round(np.random.uniform(5000000, 80000000), 2) if np.random.random() < 0.8 else None

        campana_rows.append({
            "campana_id": f"CAMP-{year}-{i+1:03d}",
            "campana_nombre": np.random.choice(campana_names),
            "fecha_inicio": start,
            "fecha_fin": end,
            "region": region,
            "tipo_descuento": dtype,
            "valor_descuento": float(dval),
            "segmento_objetivo": target_segment,
            "programa_objetivo": target_program,
            "postulaciones": conversiones,
            "presupuesto_clp": presupuesto,
        })

df_campanas = pd.DataFrame(campana_rows)

bad_date_idx = np.random.choice(len(df_campanas), 3, replace=False)
for idx in bad_date_idx:
    df_campanas.loc[idx, "fecha_fin"] = df_campanas.loc[idx, "fecha_inicio"] - timedelta(days=10)

pct_idx = df_campanas[df_campanas["tipo_descuento"] == "percentage"].index
if len(pct_idx) >= 5:
    bad_pct_idx = np.random.choice(pct_idx, 5, replace=False)
    df_campanas.loc[bad_pct_idx, "valor_descuento"] = 150.0

null_name_idx = np.random.choice(len(df_campanas), 10, replace=False)
df_campanas.loc[null_name_idx, "campana_nombre"] = None

print(f"fact_campanas_admision: {len(df_campanas)} rows")
print(f"  DQ issues: 3 inverted dates, 5 impossible discounts, 10 null names")

sdf_campanas = spark.createDataFrame(df_campanas)
sdf_campanas.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.fact_campanas_admision")
print(f"✅ {CATALOG}.{SCHEMA}.fact_campanas_admision written")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table 5: fact_daily_kpis

# COMMAND ----------

kpi_rows = []
regions_list = list(REGIONS.keys())

for region_code in regions_list:
    region_cids = df_campus[df_campus["region"] == region_code]["campus_id"].tolist()
    n_campus = len(region_cids)

    for d in date_range:
        d_date = d.date()
        region_data = df_ops[(df_ops["campus_id"].isin(region_cids)) & (df_ops["fecha_matricula"] == d_date)]

        if len(region_data) == 0:
            total_ops = int(np.random.uniform(400, 2500))
            total_tx = int(total_ops * np.random.uniform(0.90, 0.98))
            total_vol = round(total_tx * np.random.uniform(300000, 900000), 2)
        else:
            total_ops = int(region_data["solicitudes_totales"].sum())
            total_tx = int(region_data["matriculas_exitosas"].sum())
            total_vol = round(region_data["ingreso_matricula_clp"].sum(), 2)

        arancel_prom = round(total_vol / max(total_tx, 1), 2)
        tasa_exito = round(np.clip(np.random.normal(0.95, 0.03), 0.85, 1.0), 3)
        sla_pct = round(np.clip(np.random.normal(0.94, 0.04), 0.80, 1.0), 3)
        estudiantes_activos = int(np.random.uniform(3000, 45000))
        nuevos_estudiantes = int(np.random.uniform(15, 600))

        yoy_growth = None
        if d.year >= 2025:
            yoy_growth = round(np.random.normal(0.06, 0.06), 4)

        kpi_rows.append({
            "kpi_date": d_date,
            "region": region_code,
            "total_campus": n_campus,
            "total_solicitudes": total_ops,
            "total_matriculas": total_tx,
            "ingreso_total_clp": total_vol,
            "arancel_promedio_clp": arancel_prom,
            "tasa_exito_promedio": tasa_exito,
            "sla_cumplimiento_pct": sla_pct,
            "estudiantes_portal_activos": estudiantes_activos,
            "nuevos_estudiantes_portal": nuevos_estudiantes,
            "yoy_ingreso_growth": yoy_growth,
        })

df_kpis = pd.DataFrame(kpi_rows)

zero_tx_idx = np.random.choice(len(df_kpis), 20, replace=False)
df_kpis.loc[zero_tx_idx, "total_matriculas"] = 0

unknown_idx = np.random.choice(len(df_kpis), 5, replace=False)
df_kpis.loc[unknown_idx, "region"] = "UNKNOWN"

sentinel_idx = np.random.choice(df_kpis[df_kpis["yoy_ingreso_growth"].notna()].index, 3, replace=False)
df_kpis.loc[sentinel_idx, "yoy_ingreso_growth"] = 999.99

print(f"fact_daily_kpis: {len(df_kpis)} rows")
print(f"  DQ issues: 20 zero-tx with ingreso, 5 UNKNOWN region, 3 sentinel outliers")

sdf_kpis = spark.createDataFrame(df_kpis)
sdf_kpis.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.{SCHEMA}.fact_daily_kpis")
print(f"✅ {CATALOG}.{SCHEMA}.fact_daily_kpis written")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation Summary

# COMMAND ----------

print("=" * 60)
print("PUC GENIE CODE WORKSHOP — DATA GENERATION SUMMARY")
print("=" * 60)
print(f"  Volume: /Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}/new_campus.csv")
print()
tables = ["dim_campus", "fact_matriculas_diarias", "fact_portal_uc_activity",
          "fact_campanas_admision", "fact_daily_kpis"]
for t in tables:
    count = spark.sql(f"SELECT COUNT(*) as cnt FROM {CATALOG}.{SCHEMA}.{t}").collect()[0]["cnt"]
    print(f"  {CATALOG}.{SCHEMA}.{t}: {count:,} rows")

print()
print("DQ Issues Summary:")
print("  dim_campus: 15 null regions, 8 future dates, 12 zero coords, 5 dup IDs, 20 bad casing, 8 aulas outliers")
print("  fact_matriculas_diarias: 200 zero ingreso, 50 negative aranceles, 30 null dates, 40 bad sla_pct")
print("  fact_portal_uc_activity: 100 lowercase segmentos, 40 negative creditos, 25 orphan XX, 80 ref breaks")
print("  fact_campanas_admision: 3 inverted dates, 5 impossible discounts, 10 null names")
print("  fact_daily_kpis: 20 zero-tx with ingreso, 5 UNKNOWN region, 3 sentinel outliers")
print()
print(f"Total DQ defects: ~360")
print("=" * 60)
print("✅ Data generation complete. Ready for workshop.")