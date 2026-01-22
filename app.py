# app.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="PAES 2023–2026 | Puntajes de corte", layout="wide")


# -----------------------------
# Utils
# -----------------------------
@st.cache_data(show_spinner=False)
def get_sheet_names(xlsx_path: str) -> list[str]:
    xls = pd.ExcelFile(xlsx_path, engine="openpyxl")
    return xls.sheet_names


@st.cache_data(show_spinner=False)
def load_sheet(xlsx_path: str, sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, engine="openpyxl")

    # Tipos (tolerante)
    for c in ["PROCESO", "CODIGO_CARRERA", "REG_CODIGO", "CLUSTER"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    for c in [
        "PUNTAJE_CORTE",
        "N_SELECCIONADOS",
        "DELTA_26_23",
        "SD_23_26",
        "SLOPE_PTS_ANIO",
        "N_MIN_23_26",
        "N_PROM_23_26",
        "DELTA_YOY",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Validación mínima para que la app funcione
    required = {"PROCESO", "CODIGO_CARRERA", "PUNTAJE_CORTE", "NOMBRE_CARRERA", "NOMBRE_UNIVERSIDAD"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"La hoja '{sheet_name}' no tiene las columnas mínimas requeridas: {sorted(missing)}. "
            "Selecciona otra hoja."
        )

    df = df.dropna(subset=["PROCESO", "CODIGO_CARRERA", "PUNTAJE_CORTE"])
    return df


def plot_hist(series: pd.Series, title: str, xlabel: str):
    fig = plt.figure()
    series.dropna().plot(kind="hist", bins=50)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("N° observaciones")
    st.pyplot(fig, clear_figure=True)


def plot_scatter(x: pd.Series, y: pd.Series, title: str, xlabel: str, ylabel: str):
    fig = plt.figure()
    plt.scatter(x, y, s=10, alpha=0.5)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    st.pyplot(fig, clear_figure=True)


# -----------------------------
# Sidebar: data
# -----------------------------
st.sidebar.header("Datos")

DEFAULT_XLSX = "serie_larga_enriquecida.xlsx"  # <- tu archivo en repo

xlsx_path = st.sidebar.text_input("Archivo Excel (.xlsx) en el repo", value=DEFAULT_XLSX)

if not os.path.exists(xlsx_path):
    st.error(
        f"No encuentro el archivo '{xlsx_path}'.\n\n"
        "Verifica que esté en la misma carpeta que app.py (raíz del repo) "
        "o escribe la ruta relativa correcta."
    )
    st.stop()

sheets = get_sheet_names(xlsx_path)
st.sidebar.caption("Hojas detectadas:")
st.sidebar.write(sheets)

# Selección de hoja: por defecto intenta una hoja “probable”, si no existe usa la primera
preferred_order = ["serie_larga_enriquecida", "serie_larga", "data", "Sheet1"]
default_sheet = next((s for s in preferred_order if s in sheets), sheets[0])

sheet = st.sidebar.selectbox("Hoja a cargar", options=sheets, index=sheets.index(default_sheet))
df = load_sheet(xlsx_path, sheet)


# -----------------------------
# Sidebar: filtros (con fallback)
# -----------------------------
st.sidebar.header("Filtros")

years = sorted(df["PROCESO"].dropna().unique().tolist())
year_sel = st.sidebar.multiselect("Años", options=years, default=years)

unis = sorted(df["NOMBRE_UNIVERSIDAD"].dropna().unique().tolist())
uni_sel = st.sidebar.multiselect("Universidad", options=unis, default=unis)

df_f = df[df["PROCESO"].isin(year_sel) & df["NOMBRE_UNIVERSIDAD"].isin(uni_sel)].copy()

if "VIA" in df_f.columns:
    vias = sorted(df_f["VIA"].dropna().unique().tolist())
    via_sel = st.sidebar.multiselect("Vía", options=vias, default=vias)
    df_f = df_f[df_f["VIA"].isin(via_sel)]

if "REG_CODIGO" in df_f.columns:
    regs = sorted(df_f["REG_CODIGO"].dropna().unique().tolist())
    reg_sel = st.sidebar.multiselect("Región (REG_CODIGO)", options=regs, default=regs)
    df_f = df_f[df_f["REG_CODIGO"].isin(reg_sel)]

if "TIPO_TENDENCIA" in df_f.columns:
    tendencias = sorted(df_f["TIPO_TENDENCIA"].dropna().unique().tolist())
    tend_sel = st.sidebar.multiselect("Tipo tendencia", options=tendencias, default=tendencias)
    df_f = df_f[df_f["TIPO_TENDENCIA"].isin(tend_sel)]

if "ESTABILIDAD" in df_f.columns:
    estabs = sorted(df_f["ESTABILIDAD"].dropna().unique().tolist())
    estab_sel = st.sidebar.multiselect("Estabilidad", options=estabs, default=estabs)
    df_f = df_f[df_f["ESTABILIDAD"].isin(estab_sel)]

if "CLUSTER" in df_f.columns:
    clusters = sorted(df_f["CLUSTER"].dropna().unique().tolist())
    cluster_sel = st.sidebar.multiselect("Cluster", options=clusters, default=clusters)
    df_f = df_f[df_f["CLUSTER"].isin(cluster_sel)]

min_n = 0
if "N_MIN_23_26" in df_f.columns:
    min_n = st.sidebar.slider("N mínimo seleccionados (2023–2026)", 0, 300, 30, 5)
    df_f = df_f[df_f["N_MIN_23_26"] >= min_n]

search = st.sidebar.text_input("Buscar carrera (contiene)", value="").strip().upper()
if search:
    df_f = df_f[df_f["NOMBRE_CARRERA"].fillna("").str.upper().str.contains(search)]


# -----------------------------
# Main UI
# -----------------------------
st.title("PAES 2023–2026 | Puntajes de corte (explorador)")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Carreras únicas (filtro)", f"{df_f['CODIGO_CARRERA'].nunique():,}".replace(",", "."))
k2.metric("Observaciones (filtro)", f"{len(df_f):,}".replace(",", "."))
k3.metric("Corte mediano (filtro)", f"{df_f['PUNTAJE_CORTE'].median():.2f}")
if "SD_23_26" in df_f.columns:
    k4.metric("Volatilidad mediana (SD)", f"{df_f['SD_23_26'].median():.2f}")
else:
    k4.metric("Volatilidad mediana (SD)", "N/D")

tab1, tab2 = st.tabs(["Exploración", "Detalle carrera"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        plot_hist(df_f["PUNTAJE_CORTE"], "Distribución de puntaje de corte", "PUNTAJE_CORTE")
    with c2:
        if "DELTA_26_23" in df_f.columns:
            plot_hist(df_f["DELTA_26_23"], "Distribución Δ (2026 vs 2023)", "Δ 2026–2023")
        else:
            st.info("La columna DELTA_26_23 no existe en esta hoja.")

    if "DELTA_26_23" in df_f.columns:
        plot_scatter(
            df_f["PUNTAJE_CORTE"],
            df_f["DELTA_26_23"],
            "Relación: corte vs Δ 2026–2023",
            "PUNTAJE_CORTE",
            "Δ 2026–2023",
        )

    st.subheader("Tabla")
    st.dataframe(df_f, use_container_width=True, height=560)

with tab2:
    st.subheader("Detalle por carrera (serie)")
    carr = (
        df_f[["CODIGO_CARRERA", "NOMBRE_CARRERA", "NOMBRE_UNIVERSIDAD"]]
        .drop_duplicates()
        .sort_values(["NOMBRE_UNIVERSIDAD", "NOMBRE_CARRERA"])
    )

    options = [
        f"{int(r.CODIGO_CARRERA)} | {r.NOMBRE_CARRERA} | {r.NOMBRE_UNIVERSIDAD}"
        for r in carr.itertuples(index=False)
        if pd.notna(r.CODIGO_CARRERA)
    ]

    if not options:
        st.info("No hay carreras disponibles con los filtros actuales.")
    else:
        choice = st.selectbox("Selecciona una carrera", options, index=0)
        code = int(choice.split("|")[0].strip())
        d = df_f[df_f["CODIGO_CARRERA"] == code].sort_values("PROCESO")

        fig = plt.figure()
        plt.plot(d["PROCESO"].astype(int), d["PUNTAJE_CORTE"], marker="o")
        plt.title("Puntaje de corte por año")
        plt.xlabel("Año (PROCESO)")
        plt.ylabel("PUNTAJE_CORTE")
        st.pyplot(fig, clear_figure=True)

        cols = ["PROCESO", "PUNTAJE_CORTE"]
        for extra in ["N_SELECCIONADOS", "DELTA_YOY", "VIA", "REG_CODIGO"]:
            if extra in d.columns:
                cols.append(extra)
        st.dataframe(d[cols], use_container_width=True)

st.divider()
st.subheader("Exportar datos filtrados")
csv_bytes = df_f.to_csv(index=False).encode("utf-8")
st.download_button(
    "Descargar CSV (filtros aplicados)",
    data=csv_bytes,
    file_name="paes_filtrado.csv",
    mime="text/csv",
)
