# app.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="PAES 2023–2026 | Puntajes de corte", layout="wide")


# -----------------------------
# Data loaders
# -----------------------------
@st.cache_data(show_spinner=False)
def load_xlsx(path: str, sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

    expected = {
        "PROCESO",
        "CODIGO_CARRERA",
        "VIA",
        "PUNTAJE_CORTE",
        "N_SELECCIONADOS",
        "NOMBRE_CARRERA",
        "NOMBRE_UNIVERSIDAD",
        "REG_CODIGO",
        "DELTA_26_23",
        "SD_23_26",
        "SLOPE_PTS_ANIO",
        "N_MIN_23_26",
        "N_PROM_23_26",
        "TIPO_TENDENCIA",
        "ESTABILIDAD",
        "CUADRANTE",
        "CLUSTER",
        "CLUSTER_LABEL",
        "DELTA_YOY",
    }
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas esperadas en la hoja '{sheet_name}': {sorted(missing)}")

    # Tipos
    df["PROCESO"] = pd.to_numeric(df["PROCESO"], errors="coerce").astype("Int64")
    df["CODIGO_CARRERA"] = pd.to_numeric(df["CODIGO_CARRERA"], errors="coerce").astype("Int64")
    df["REG_CODIGO"] = pd.to_numeric(df["REG_CODIGO"], errors="coerce").astype("Int64")
    df["PUNTAJE_CORTE"] = pd.to_numeric(df["PUNTAJE_CORTE"], errors="coerce")
    df["N_SELECCIONADOS"] = pd.to_numeric(df["N_SELECCIONADOS"], errors="coerce")
    df["DELTA_26_23"] = pd.to_numeric(df["DELTA_26_23"], errors="coerce")
    df["SD_23_26"] = pd.to_numeric(df["SD_23_26"], errors="coerce")
    df["SLOPE_PTS_ANIO"] = pd.to_numeric(df["SLOPE_PTS_ANIO"], errors="coerce")
    df["N_MIN_23_26"] = pd.to_numeric(df["N_MIN_23_26"], errors="coerce")
    df["N_PROM_23_26"] = pd.to_numeric(df["N_PROM_23_26"], errors="coerce")
    df["CLUSTER"] = pd.to_numeric(df["CLUSTER"], errors="coerce").astype("Int64")

    df = df.dropna(subset=["PROCESO", "CODIGO_CARRERA", "PUNTAJE_CORTE"])
    return df


def plot_hist(series: pd.Series, title: str, xlabel: str):
    fig = plt.figure()
    series.dropna().plot(kind="hist", bins=50)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("N° de carreras")
    st.pyplot(fig, clear_figure=True)


def plot_scatter(x: pd.Series, y: pd.Series, title: str, xlabel: str, ylabel: str):
    fig = plt.figure()
    plt.scatter(x, y, s=10, alpha=0.5)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    st.pyplot(fig, clear_figure=True)


# -----------------------------
# Sidebar: Data source
# -----------------------------
st.sidebar.header("Datos")

DEFAULT_XLSX = "analisis_puntajes_corte_PAES_2023_2026.xlsx"
DEFAULT_SHEET = "serie_larga_enriquecida"

data_mode = st.sidebar.radio(
    "Fuente de datos",
    ["Excel en el repo", "Subir Excel"],
    index=0
)

df = None

try:
    if data_mode == "Excel en el repo":
        path = st.sidebar.text_input("Archivo Excel (.xlsx)", value=DEFAULT_XLSX)
        sheet = st.sidebar.text_input("Hoja", value=DEFAULT_SHEET)

        if not os.path.exists(path):
            st.sidebar.error(
                f"No encuentro el archivo '{path}'.\n\n"
                "Súbelo al repo en la misma carpeta que app.py o usa 'Subir Excel'."
            )
        else:
            df = load_xlsx(path, sheet)

    else:
        up = st.sidebar.file_uploader("Sube el Excel", type=["xlsx"])
        sheet = st.sidebar.text_input("Hoja", value=DEFAULT_SHEET)

        if up is not None:
            df = pd.read_excel(up, sheet_name=sheet, engine="openpyxl")

            # Validación rápida (mismas columnas esperadas)
            expected = {
                "PROCESO","CODIGO_CARRERA","VIA","PUNTAJE_CORTE","N_SELECCIONADOS",
                "NOMBRE_CARRERA","NOMBRE_UNIVERSIDAD","REG_CODIGO",
                "DELTA_26_23","SD_23_26","SLOPE_PTS_ANIO","N_MIN_23_26","N_PROM_23_26",
                "TIPO_TENDENCIA","ESTABILIDAD","CUADRANTE","CLUSTER","CLUSTER_LABEL","DELTA_YOY"
            }
            missing = expected - set(df.columns)
            if missing:
                st.error(f"Faltan columnas esperadas en la hoja '{sheet}': {sorted(missing)}")
                st.stop()

            # Tipos básicos
            df["PROCESO"] = pd.to_numeric(df["PROCESO"], errors="coerce").astype("Int64")
            df["CODIGO_CARRERA"] = pd.to_numeric(df["CODIGO_CARRERA"], errors="coerce").astype("Int64")
            df["REG_CODIGO"] = pd.to_numeric(df["REG_CODIGO"], errors="coerce").astype("Int64")
            df["PUNTAJE_CORTE"] = pd.to_numeric(df["PUNTAJE_CORTE"], errors="coerce")
            df["N_SELECCIONADOS"] = pd.to_numeric(df["N_SELECCIONADOS"], errors="coerce")
            df["DELTA_26_23"] = pd.to_numeric(df["DELTA_26_23"], errors="coerce")
            df["SD_23_26"] = pd.to_numeric(df["SD_23_26"], errors="coerce")
            df["SLOPE_PTS_ANIO"] = pd.to_numeric(df["SLOPE_PTS_ANIO"], errors="coerce")
            df["N_MIN_23_26"] = pd.to_numeric(df["N_MIN_23_26"], errors="coerce")
            df["N_PROM_23_26"] = pd.to_numeric(df["N_PROM_23_26"], errors="coerce")
            df["CLUSTER"] = pd.to_numeric(df["CLUSTER"], errors="coerce").astype("Int64")
            df = df.dropna(subset=["PROCESO","CODIGO_CARRERA","PUNTAJE_CORTE"])

except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

if df is None:
    st.title("PAES 2023–2026 | Puntajes de corte")
    st.info("Selecciona una fuente de datos válida en la barra lateral para continuar.")
    st.stop()


# -----------------------------
# Sidebar: Filters
# -----------------------------
st.sidebar.header("Filtros")

years = sorted(df["PROCESO"].dropna().unique().tolist())
year_sel = st.sidebar.multiselect("Años", options=years, default=years)

vias = sorted(df["VIA"].dropna().unique().tolist())
via_sel = st.sidebar.multiselect("Vía", options=vias, default=vias)

unis = sorted(df["NOMBRE_UNIVERSIDAD"].dropna().unique().tolist())
uni_sel = st.sidebar.multiselect("Universidad", options=unis, default=unis)

regs = sorted(df["REG_CODIGO"].dropna().unique().tolist())
reg_sel = st.sidebar.multiselect("Región (REG_CODIGO)", options=regs, default=regs)

tendencias = sorted(df["TIPO_TENDENCIA"].dropna().unique().tolist())
tend_sel = st.sidebar.multiselect("Tipo tendencia", options=tendencias, default=tendencias)

estabs = sorted(df["ESTABILIDAD"].dropna().unique().tolist())
estab_sel = st.sidebar.multiselect("Estabilidad", options=estabs, default=estabs)

clusters = sorted(df["CLUSTER"].dropna().unique().tolist())
cluster_sel = st.sidebar.multiselect("Cluster", options=clusters, default=clusters)

min_n = st.sidebar.slider("N mínimo seleccionados (2023–2026)", min_value=0, max_value=300, value=30, step=5)

search = st.sidebar.text_input("Buscar carrera (contiene)", value="").strip().upper()

df_f = df[
    df["PROCESO"].isin(year_sel)
    & df["VIA"].isin(via_sel)
    & df["NOMBRE_UNIVERSIDAD"].isin(uni_sel)
    & df["REG_CODIGO"].isin(reg_sel)
    & df["TIPO_TENDENCIA"].isin(tend_sel)
    & df["ESTABILIDAD"].isin(estab_sel)
    & df["CLUSTER"].isin(cluster_sel)
    & (df["N_MIN_23_26"] >= min_n)
].copy()

if search:
    df_f = df_f[df_f["NOMBRE_CARRERA"].fillna("").str.upper().str.contains(search)]


# -----------------------------
# Header + KPIs
# -----------------------------
st.title("PAES 2023–2026 | Puntajes de corte (carreras con continuidad)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Carreras únicas (filtro)", f"{df_f['CODIGO_CARRERA'].nunique():,}".replace(",", "."))
c2.metric("Observaciones (filtro)", f"{len(df_f):,}".replace(",", "."))
c3.metric("Corte mediano (filtro)", f"{df_f['PUNTAJE_CORTE'].median():.2f}")
c4.metric("Volatilidad mediana (SD 23–26)", f"{df_f['SD_23_26'].median():.2f}")

st.caption(
    "Definición: puntaje de corte = mínimo PUNTAJE_CORTE (derivado de PTJE_PREF) "
    "entre seleccionados/as REGULAR (ESTADO_PREF=24). Dataset enriquecido 2023–2026."
)


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Exploración", "Rankings", "Universidades", "Carrera (detalle)"]
)


with tab1:
    st.subheader("Distribuciones y relaciones")

    a, b = st.columns(2)
    with a:
        plot_hist(df_f["DELTA_26_23"], "Distribución Δ corte (2026 vs 2023)", "Δ puntaje")
    with b:
        plot_hist(df_f["SD_23_26"], "Distribución volatilidad (SD 2023–2026)", "SD")

    a2, b2 = st.columns(2)
    with a2:
        plot_scatter(
            df_f["PUNTAJE_CORTE"],
            df_f["DELTA_26_23"],
            "Relación: corte (según filtro/año) vs Δ 2026–2023",
            "PUNTAJE_CORTE",
            "Δ 2026–2023",
        )
    with b2:
        plot_scatter(
            df_f["PUNTAJE_CORTE"],
            df_f["SD_23_26"],
            "Relación: corte (según filtro/año) vs volatilidad",
            "PUNTAJE_CORTE",
            "SD 2023–2026",
        )

    st.subheader("Muestra de datos")
    st.dataframe(
        df_f.sort_values(["PROCESO", "NOMBRE_UNIVERSIDAD", "NOMBRE_CARRERA"])[
            [
                "PROCESO",
                "CODIGO_CARRERA",
                "NOMBRE_CARRERA",
                "NOMBRE_UNIVERSIDAD",
                "REG_CODIGO",
                "VIA",
                "PUNTAJE_CORTE",
                "N_SELECCIONADOS",
                "DELTA_YOY",
                "DELTA_26_23",
                "SD_23_26",
                "SLOPE_PTS_ANIO",
                "TIPO_TENDENCIA",
                "ESTABILIDAD",
                "CLUSTER_LABEL",
            ]
        ],
        use_container_width=True,
        height=460,
    )


with tab2:
    st.subheader("Rankings (Δ 2026–2023)")

    careers = (
        df_f[df_f["PROCESO"] == 2026]
        .drop_duplicates(subset=["CODIGO_CARRERA"])
        .copy()
    )

    if careers.empty:
        st.warning("No hay carreras 2026 bajo estos filtros (revisa filtros).")
    else:
        n_show = st.slider("Cantidad a mostrar", 10, 200, 50, 10)

        l, r = st.columns(2)

        with l:
            st.markdown("**Top suben**")
            st.dataframe(
                careers.sort_values("DELTA_26_23", ascending=False)[
                    [
                        "CODIGO_CARRERA",
                        "NOMBRE_CARRERA",
                        "NOMBRE_UNIVERSIDAD",
                        "REG_CODIGO",
                        "PUNTAJE_CORTE",
                        "DELTA_26_23",
                        "SD_23_26",
                        "N_MIN_23_26",
                        "TIPO_TENDENCIA",
                        "CLUSTER_LABEL",
                    ]
                ].head(n_show),
                use_container_width=True,
                height=520,
            )

        with r:
            st.markdown("**Top bajan**")
            st.dataframe(
                careers.sort_values("DELTA_26_23", ascending=True)[
                    [
                        "CODIGO_CARRERA",
                        "NOMBRE_CARRERA",
                        "NOMBRE_UNIVERSIDAD",
                        "REG_CODIGO",
                        "PUNTAJE_CORTE",
                        "DELTA_26_23",
                        "SD_23_26",
                        "N_MIN_23_26",
                        "TIPO_TENDENCIA",
                        "CLUSTER_LABEL",
                    ]
                ].head(n_show),
                use_container_width=True,
                height=520,
            )


with tab3:
    st.subheader("Universidades: mediana anual + % de carreras que suben")

    uni_year = (
        df_f.groupby(["NOMBRE_UNIVERSIDAD", "PROCESO"])
        .agg(
            MEDIANA_CORTE=("PUNTAJE_CORTE", "median"),
            PROM_CORTE=("PUNTAJE_CORTE", "mean"),
            N_CARRERAS=("CODIGO_CARRERA", "nunique"),
            N_SELECCIONADOS=("N_SELECCIONADOS", "sum"),
        )
        .reset_index()
    )

    uni_piv = (
        uni_year.pivot(index="NOMBRE_UNIVERSIDAD", columns="PROCESO", values="MEDIANA_CORTE")
        .reset_index()
    )

    if 2023 in uni_piv.columns and 2026 in uni_piv.columns:
        uni_piv["DELTA_MEDIANA_26_23"] = uni_piv[2026] - uni_piv[2023]
    else:
        uni_piv["DELTA_MEDIANA_26_23"] = np.nan

    careers_2026 = df_f[df_f["PROCESO"] == 2026].drop_duplicates(subset=["CODIGO_CARRERA"])
    if not careers_2026.empty:
        careers_2026["SUBE_26_23"] = careers_2026["DELTA_26_23"] > 0

        uni_up = (
            careers_2026.groupby("NOMBRE_UNIVERSIDAD")
            .agg(
                N_CARRERAS=("CODIGO_CARRERA", "nunique"),
                PCT_CARRERAS_SUBEN=("SUBE_26_23", "mean"),
                MEDIANA_SD=("SD_23_26", "median"),
            )
            .reset_index()
        )
        uni_up["PCT_CARRERAS_SUBEN"] = (uni_up["PCT_CARRERAS_SUBEN"] * 100).round(1)

        uni_piv = uni_piv.merge(uni_up, on="NOMBRE_UNIVERSIDAD", how="left")

    st.dataframe(
        uni_piv.sort_values("DELTA_MEDIANA_26_23", ascending=True),
        use_container_width=True,
        height=620,
    )


with tab4:
    st.subheader("Detalle por carrera (2023–2026)")

    careers_list = (
        df_f[["CODIGO_CARRERA", "NOMBRE_CARRERA", "NOMBRE_UNIVERSIDAD"]]
        .drop_duplicates()
        .sort_values(["NOMBRE_UNIVERSIDAD", "NOMBRE_CARRERA"])
    )

    options = [
        f"{int(r.CODIGO_CARRERA)} | {r.NOMBRE_CARRERA} | {r.NOMBRE_UNIVERSIDAD}"
        for r in careers_list.itertuples(index=False)
        if pd.notna(r.CODIGO_CARRERA)
    ]

    if not options:
        st.warning("No hay carreras disponibles bajo estos filtros.")
    else:
        choice = st.selectbox("Selecciona una carrera", options, index=0)
        code = int(choice.split("|")[0].strip())

        d = df_f[df_f["CODIGO_CARRERA"] == code].sort_values("PROCESO")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Δ 2026–2023", f"{d['DELTA_26_23'].iloc[0]:.2f}")
        k2.metric("SD 2023–2026", f"{d['SD_23_26'].iloc[0]:.2f}")
        k3.metric("Slope (pts/año)", f"{d['SLOPE_PTS_ANIO'].iloc[0]:.2f}")
        k4.metric("N mínimo 23–26", f"{int(d['N_MIN_23_26'].iloc[0])}")

        st.write(
            f"**Tendencia:** {d['TIPO_TENDENCIA'].iloc[0]}  |  "
            f"**Estabilidad:** {d['ESTABILIDAD'].iloc[0]}  |  "
            f"**Cluster:** {d['CLUSTER_LABEL'].iloc[0]}"
        )

        fig = plt.figure()
        plt.plot(d["PROCESO"].astype(int), d["PUNTAJE_CORTE"], marker="o")
        plt.title("Puntaje de corte por año")
        plt.xlabel("Año (PROCESO)")
        plt.ylabel("PUNTAJE_CORTE")
        st.pyplot(fig, clear_figure=True)

        st.dataframe(
            d[["PROCESO", "PUNTAJE_CORTE", "N_SELECCIONADOS", "DELTA_YOY", "REG_CODIGO", "VIA"]],
            use_container_width=True,
        )


# -----------------------------
# Download filtered data
# -----------------------------
st.divider()
st.subheader("Exportar datos filtrados")

csv_bytes = df_f.to_csv(index=False).encode("utf-8")
st.download_button(
    "Descargar CSV (filtros aplicados)",
    data=csv_bytes,
    file_name="paes_2023_2026_filtrado.csv",
    mime="text/csv",
)
