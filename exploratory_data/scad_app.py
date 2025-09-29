import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# =====================================================================================
# CSS PERSONALIZADO
# =====================================================================================
st.markdown("""
<style>

/* ====== Fondos principales ====== */

/* Fondo del área principal (contenido) */
div[data-testid="stAppViewContainer"]{
  background-color: #f9f9f9;   /* gris muy suave para resaltar gráficos */
}

/* Fondo del sidebar */
aside[data-testid="stSidebar"]{
  background-color: #b1c7df;   /* azul grisáceo de la paleta */
}

/* Panel interno de tarjetas en el sidebar (donde está el option_menu) */
aside[data-testid="stSidebar"] .block-container{
  padding-top: 1rem;
  padding-bottom: 1rem;
}

/* ====== Navegación (streamlit-option-menu) ======
   La librería usa clases bootstrap-like: .nav, .nav-pills, .nav-link, .active
   Estas reglas se aplican de forma robusta dentro del sidebar.
================================================== */

/* Botón activo */
aside[data-testid="stSidebar"] .nav-pills .nav-link.active{
  background-color: #f0635e !important;  /* rojo coral de la paleta */
  color: #ffffff !important;
  font-weight: 700;
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.05) inset;
}

/* Botón normal */
aside[data-testid="stSidebar"] .nav-pills .nav-link{
  color: #122b39;                 /* texto oscuro legible */
  background-color: #ffffff;      /* pastilla blanca */
  border-radius: 10px;
  margin-bottom: 8px;
  border: 1px solid rgba(0,0,0,0.06);
  transition: all 0.2s ease-in-out;
}

/* Hover */
aside[data-testid="stSidebar"] .nav-pills .nav-link:hover{
  background-color: #23b7d9 !important;  /* cyan */
  color: #ffffff !important;
  border-color: transparent;
}

/* Iconos dentro del option menu */
aside[data-testid="stSidebar"] .nav-pills .nav-link svg{
  margin-right: .35rem;
}

/* ====== Métricas (KPI) ====== */
div[data-testid="stMetricValue"]{
  color: #1d7084;  /* teal para valores */
  font-weight: 600;
}
div[data-testid="stMetricLabel"]{
  color: #4a5b6b;  /* gris oscuro */
  font-size: 0.9rem;
}

/* ====== Pequeños detalles ====== */
header[data-testid="stHeader"]{
  background: transparent;   /* elimina barra superior gris */
  box-shadow: none;
}
</style>
""", unsafe_allow_html=True)


# =====================================================================================
# Configuración de la página
# =====================================================================================
st.set_page_config(page_title="SCAD Dataset Explorer", page_icon="🌍", layout="wide")

# Estado global
if "df" not in st.session_state:
    st.session_state.df = None

# =====================================================================================
# CARGA DE DATOS (cacheada)
# =====================================================================================
@st.cache_data(show_spinner=True)
def load_data(path: Path) -> pd.DataFrame:
    # Lee CSV
    df = pd.read_csv(path)

    # Normaliza columnas
    df.columns = df.columns.str.strip()

    # Detecta columna de año
    year_col_candidates = [c for c in df.columns if "year" in c.lower() or "año" in c.lower()]
    if not year_col_candidates:
        st.error("❌ No se encontró ninguna columna que parezca contener el año.")
        st.stop()
    year_col = year_col_candidates[0]
    if year_col != "year":
        df = df.rename(columns={year_col: "year"})

    # Conversión a numérico
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # ndeath puede no existir en algunos SCAD
    if "ndeath" not in df.columns:
        if "fatalities" in df.columns:
            df["ndeath"] = pd.to_numeric(df["fatalities"], errors="coerce")
        else:
            df["ndeath"] = pd.NA

    df["ndeath"] = pd.to_numeric(df["ndeath"], errors="coerce")

    return df

# Ruta del dataset
DATA_PATH = Path("exploratory_data") / "scad_final_dataset.csv"

# Intenta cargar al inicio (si existe)
if DATA_PATH.exists():
    st.session_state.df = load_data(DATA_PATH)

# =====================================================================================
# Encabezado principal
# =====================================================================================
st.title("🌍 SCAD Dataset Explorer")
st.markdown("### Análisis de conflictos sociales en África y América Latina (1990–2018)")

# =====================================================================================
# Sidebar navegación
# =====================================================================================
with st.sidebar:
    st.markdown("## Navegación")
    selected = option_menu(
        menu_title=None,
        options=[
            "Inicio",
            "Explorador de Eventos",
            "Explorador de Muertes",
            "Estadísticas Generales",
            "Análisis por Religión",
            "Conclusiones"
        ],
        icons=["house", "map", "x-circle", "bar-chart", "building", "check2-circle"],
        default_index=0
    )

# =====================================================================================
# 1. PESTAÑA INICIO
# =====================================================================================
if selected == "Inicio":
    st.header("Inicio")
    st.write("Bienvenido. Usa las pestañas de abajo para explorar el contexto del proyecto.")

    tabs = st.tabs([
        "📝 Descripción",
        "🎯 Objetivos",
        "🗂️ Datos",
        "📚 Codebooks",
        "🧪 Metodología",
        "ℹ️ Notas/Créditos"
    ])

    # --- Descripción ---
    with tabs[0]:
        st.subheader("Descripción")
        st.markdown(
            """
            Hemos llevado a cabo un **proyecto de investigación y desarrollo** basado en los datos del 
            **[SCAD Dataset Explorer](https://www.strausscenter.org/ccaps-research-areas/social-conflict/database/)**, 
            recopilando información detallada de **África** y **América Latina**.  
            
            Nuestro propósito ha sido **analizar los conflictos sociales registrados entre 1990 y 2018**, 
            considerando variables como el tipo de evento, los actores implicados, la localización geográfica y el número de víctimas.  
            Este trabajo se enmarca dentro de un interés por comprender mejor la dinámica de los conflictos en diferentes contextos 
            políticos, sociales y culturales.

            A partir de esta recopilación y análisis, hemos desarrollado una **aplicación funcional e interactiva** que facilita:  
            - La exploración de los datos en múltiples dimensiones.  
            - La generación de visualizaciones dinámicas que permiten identificar patrones y tendencias.  
            - La comparación entre países y regiones de forma accesible.  
            
            Con esta herramienta buscamos **poner a disposición de investigadores, estudiantes y público general** 
            un entorno en el cual los resultados puedan ser consultados y comprendidos de manera intuitiva.  
            Creemos que la **interactividad** y la **transparencia de los datos** son aspectos clave para fomentar una reflexión crítica 
            y constructiva en torno a los conflictos sociales en ambas regiones.
            
            En definitiva, el proyecto no solo constituye un ejercicio de análisis de datos, sino también una 
            **iniciativa orientada a la difusión del conocimiento**, al ofrecer una plataforma abierta que permita observar 
            y comprender los resultados de manera directa.
            """
        )

        # --- Objetivos ---
    # --- Objetivos ---
    with tabs[1]:
        st.subheader("Objetivos")
        st.markdown(
            """
            En el marco de este proyecto nos hemos propuesto una serie de **objetivos estratégicos** 
            orientados a garantizar la calidad de los datos, la robustez de los análisis y la utilidad práctica de los resultados.  
            Desde una perspectiva de **Data Engineering**, **Data Analysis** y **Data Visualization**, nuestros objetivos son los siguientes:

            1. **Construir una arquitectura de datos sólida**, asegurando procesos de limpieza, normalización y estandarización, 
            con el fin de minimizar inconsistencias y errores que puedan afectar el análisis posterior.  
            2. **Implementar procedimientos de *Feature Engineering*** que permitan enriquecer los datos originales mediante 
            la creación de nuevas variables, transformaciones relevantes y codificaciones adecuadas para capturar relaciones no triviales.  
            3. **Realizar un *Exploratory Data Analysis (EDA)* exhaustivo**, aplicando técnicas estadísticas y visuales 
            que faciliten la comprensión de patrones, distribuciones y anomalías en los datos antes de los análisis avanzados.  
            4. **Desarrollar visualizaciones comprensibles y estéticamente cuidadas**, orientadas a un público general, 
            empleando una **paleta de colores adecuada** para cada contexto y garantizando la correcta interpretación 
            de los hallazgos sin sobrecargar la información.  
            5. **Diseñar dashboards interactivos y modulares** que permitan explorar dinámicamente las distintas dimensiones 
            de los conflictos (espaciales, temporales y temáticos), ofreciendo flexibilidad para distintos perfiles de usuarios.  
            6. **Crear una aplicación funcional e interactiva**, con una experiencia de usuario fluida y accesible, 
            que permita la exploración de resultados en tiempo real y la consulta de métricas clave desde múltiples perspectivas.  
            7. **Asegurar buenas prácticas de ingeniería de datos**, incluyendo validación de consistencia, documentación, 
            versionado de datasets y trazabilidad de transformaciones, con el fin de garantizar la reproducibilidad.  
            8. **Promover la accesibilidad y la transparencia**, asegurando que los datos y resultados puedan ser utilizados 
            tanto por investigadores especializados como por usuarios sin formación técnica, contribuyendo así a la 
            democratización del conocimiento.  

            Con ello buscamos consolidar una plataforma que integre **rigurosidad metodológica**, **calidad en el tratamiento de datos**, 
            **profundidad analítica** y **excelencia en la comunicación visual**, ofreciendo un equilibrio entre la 
            precisión técnica y la claridad divulgativa.
            """
        )

        # --- Datos ---
    with tabs[2]:
        st.subheader("Datos")
        st.markdown(
            """
            Los datos utilizados en este proyecto provienen del 
            **[Social Conflict Analysis Database (SCAD)](https://www.strausscenter.org/ccaps-research-areas/social-conflict/database/)**, 
            un repositorio de referencia en el estudio de conflictos sociales.  

            **Citación recomendada:**  
            Salehyan, Idean, Cullen S. Hendrix, Jesse Hamner, Christina Case, Christopher Linebarger, Emily Stull, and Jennifer Williams.  
            *“Social conflict in Africa: A new database.”* International Interactions 38, no. 4 (2012): 503–511.  

            ---

            A partir de los datos en bruto disponibles en la fuente original, hemos llevado a cabo un proceso de **transformación y 
            normalización exhaustivo**, orientado a:  
            - Estandarizar formatos de fechas, nombres de países y divisiones administrativas.  
            - Controlar valores faltantes y posibles duplicados.  
            - Integrar los distintos subconjuntos en un **único dataset consolidado**.  
            - Definir una estructura de columnas sólida y coherente para su posterior manipulación y análisis.  

            El resultado de este proceso es un **dataset único y completo** que concentra toda la información necesaria para los análisis 
            posteriores, con un formato estandarizado y de fácil manipulación.  

            Cabe destacar que, aunque se han aplicado transformaciones técnicas para garantizar la calidad y consistencia de los datos, 
            hemos procurado **mantener los registros lo más fieles posible a la fuente original**, evitando alteraciones que pudieran 
            modificar la naturaleza o los resultados de los análisis.

            ---

            A continuación se muestra una vista preliminar del dataset final:
            """
        )

        if st.session_state.df is not None:
            st.dataframe(st.session_state.df.head(20), use_container_width=True)

            # Botón para descargar el dataset directamente desde la app
            st.download_button(
                label="💾 Descargar dataset consolidado (CSV)",
                data=st.session_state.df.to_csv(index=False).encode("utf-8"),
                file_name="scad_final_dataset.csv",
                mime="text/csv"
            )
        else:
            st.warning(
                "⚠️ No se han cargado datos. Utiliza la opción de carga rápida en esta sección o asegúrate de que "
                "el archivo `scad_final_dataset.csv` esté disponible en la carpeta `exploratory_data`."
            )


    # --- Codebooks ---
    with tabs[3]:
        st.subheader("Codebooks")
        st.markdown(
            """
            Los **codebooks** (libros de códigos) son documentos esenciales en cualquier proyecto de análisis de datos, 
            ya que **definen y documentan** con precisión cada variable incluida en el dataset.  
            En ellos se especifica el **nombre de la variable**, su **significado**, el **tipo de dato**, los **valores permitidos**, 
            las **unidades de medida**, las **reglas de codificación** y las **notas metodológicas** que orientan su correcta interpretación.  

            ### ¿Para qué se utilizan?
            - Para **interpretar correctamente** los datos y evitar errores de análisis.  
            - Para **garantizar la reproducibilidad**, facilitando que cualquier analista pueda replicar los resultados.  
            - Para **alinear criterios** entre equipos de trabajo (data engineers, data analysts, científicos sociales), 
            asegurando consistencia en la manipulación y uso de la información.  
            - Para **estandarizar procesos** de limpieza, transformación y análisis en proyectos colaborativos.  

            ### ¿Por qué es importante leerlos y comprenderlos?
            - Ayudan a **detectar y prevenir errores de interpretación**, por ejemplo en variables categóricas o en escalas invertidas.  
            - Permiten diseñar procesos de **feature engineering** más sólidos, al contar con el contexto completo de cada campo.  
            - Son clave para un **EDA (Exploratory Data Analysis)** riguroso, asegurando que las estadísticas y visualizaciones 
            reflejen la realidad de los datos.  
            - Garantizan que las **visualizaciones y modelos analíticos** comuniquen lo que realmente representan las variables, 
            evitando conclusiones erróneas.  

            ### Codebooks oficiales
            Los codebooks oficiales del SCAD están disponibles en la página del  
            **[SCAD Dataset Explorer](https://www.strausscenter.org/ccaps-research-areas/social-conflict/database/)**.  
            No obstante, para facilitar el acceso y la consulta, en esta aplicación hemos incluido la posibilidad de 
            **descargarlos directamente** en formato PDF.
            """
        )

        from pathlib import Path

        CODEBOOK_DIR = Path("codebooks")  # <- carpeta dentro del repo o proyecto
        pdfs = list(CODEBOOK_DIR.glob("*.pdf")) if CODEBOOK_DIR.exists() else []

        if pdfs:
            st.markdown("#### Descarga directa de Codebooks (PDF)")
            for pdf in pdfs:
                with open(pdf, "rb") as fh:
                    st.download_button(
                        label=f"⬇️ Descargar {pdf.name}",
                        data=fh.read(),
                        file_name=pdf.name,
                        mime="application/pdf"
                    )
        else:
            st.info(
                "⚠️ Los codebooks no están disponibles en la carpeta del proyecto. "
                "Puedes consultarlos directamente en la página oficial del SCAD."
            )

        # --- Metodología ---
        # --- Metodología ---
    with tabs[4]:
        st.subheader("Metodología")
        st.markdown(
            """
            La metodología aplicada en este proyecto sigue un enfoque sistemático propio de la **ingeniería y el análisis de datos**, 
            garantizando la calidad, consistencia y utilidad del dataset resultante.  

            El proceso ha sido diseñado en etapas secuenciales, siguiendo las buenas prácticas utilizadas por **Data Engineers** y 
            **Data Analysts** en proyectos de analítica avanzada:

            1. **Ingesta de datos**  
            - Recolección de los ficheros originales publicados por el SCAD.  
            - Verificación de integridad de los registros y formatos de origen.  

            2. **Limpieza y normalización**  
            - Estandarización de nombres de países, divisiones administrativas y fechas.  
            - Control de valores faltantes y duplicados.  
            - Conversión de tipos de datos (numéricos, categóricos, temporales).  

            3. **Feature Engineering**  
            - Creación de variables derivadas (por ejemplo, número total de muertes normalizadas, clasificación de eventos).  
            - Codificación de categorías y generación de atributos adicionales para enriquecer el análisis.  

            4. **Exploratory Data Analysis (EDA)**  
            - Identificación de patrones, outliers y distribuciones de interés.  
            - Validación de supuestos metodológicos antes de aplicar análisis descriptivos y visualizaciones.  

            5. **Consolidación en un dataset único**  
            - Integración de los distintos subconjuntos de datos en un único fichero estructurado.  
            - Validación de consistencia entre columnas clave (`event_type`, `country`, `year`, etc.).  

            6. **Visualización y comunicación**  
            - Diseño de gráficos interactivos y métricas agregadas.  
            - Selección de paletas de colores comprensibles y accesibles para el público general.  

            7. **Despliegue en aplicación interactiva**  
            - Implementación de una aplicación funcional que facilita la exploración de los datos.  
            - Accesibilidad para investigadores, estudiantes y usuarios no técnicos.  

            En conjunto, esta metodología permite asegurar que los datos sean **fiables, reproducibles y útiles** para distintos tipos de análisis.
            """
        )

        with st.expander("📌 Buenas prácticas y recomendaciones"):
            st.markdown(
                """
                Como especialistas en ingeniería y análisis de datos, recomendamos tener en cuenta las siguientes 
                buenas prácticas al trabajar con datasets complejos como SCAD:

                - **Gobernanza de datos**: documentar fuentes, versiones y transformaciones aplicadas.  
                - **Reproducibilidad**: mantener scripts y notebooks versionados (Git) que permitan replicar cada paso.  
                - **Validación continua**: aplicar controles de calidad en cada fase (conteo de registros, consistencia de claves).  
                - **Automatización**: diseñar pipelines de ingesta y transformación escalables, evitando procesos manuales repetitivos.  
                - **EDA riguroso**: realizar un análisis exploratorio antes de generar métricas o visualizaciones definitivas.  
                - **Feature Engineering responsable**: crear variables útiles, pero siempre documentando su significado y supuestos.  
                - **Visualizaciones accesibles**: emplear gráficos claros, con etiquetas y colores comprensibles incluso para usuarios no expertos.  
                - **Seguridad y privacidad**: manejar los datos con criterios éticos, respetando licencias y citando adecuadamente la fuente.  
                - **Transparencia**: publicar codebooks, definiciones y criterios metodológicos para facilitar el entendimiento a toda la comunidad.  

                Estas prácticas aseguran que los resultados no solo sean correctos desde el punto de vista técnico, 
                sino también **comprensibles, reproducibles y de valor para la toma de decisiones**.
                """
            )

    # --- Notas/Créditos ---
    with tabs[5]:
        st.subheader("Notas / Créditos")
        st.markdown(
            """
            ### Autores
            - **Diego Rubianes Sousa**  
            - **Martín Amoedo Carbajal**

            ### Agradecimientos
            Queremos agradecer al equipo del **[Strauss Center for International Security and Law](https://www.strausscenter.org/)** 
            por la recopilación, mantenimiento y publicación del **SCAD Dataset**, sin el cual este proyecto no habría sido posible.  

            Asimismo, reconocemos el trabajo de la comunidad académica y profesional en el ámbito de la **ingeniería de datos** 
            y el **análisis de conflictos**, cuyos enfoques y metodologías han inspirado el diseño de esta aplicación.

            ### Referencias
            - Salehyan, Idean, Cullen S. Hendrix, Jesse Hamner, Christina Case, Christopher Linebarger, Emily Stull, and Jennifer Williams.  
            *“Social conflict in Africa: A new database.”* International Interactions 38, no. 4 (2012): 503–511.  
            - SCAD Dataset Explorer: [https://www.strausscenter.org/ccaps-research-areas/social-conflict/database/](https://www.strausscenter.org/ccaps-research-areas/social-conflict/database/)  

            ### Licencia y uso
            Este proyecto se ha desarrollado con fines **académicos y de investigación**.  
            Los datos pertenecen a sus respectivos autores y deben ser citados según la referencia oficial.  

            El código y la aplicación están orientados a promover la **transparencia**, la **reproducibilidad** y la 
            **democratización del conocimiento**, facilitando el acceso abierto a herramientas de análisis de conflictos sociales.  

            ---
            **Contacto:**  
            Para comentarios, sugerencias o colaboraciones, no dudes en ponerte en contacto con los autores.  
            """
        )
    # =====================================================================================
    # 2. PESTAÑA EXPLORADOR DE EVENTOS
    # =====================================================================================
elif selected == "Explorador de Eventos":
    st.header("Explorador Geográfico de Eventos")
    st.caption("Distribución total de eventos por país con filtros esenciales y mapas coropléticos profesionales.")

    # -------------------------
    # Validación de datos
    # -------------------------
    if "df" not in st.session_state or st.session_state.df is None or st.session_state.df.empty:
        st.warning("⚠️ Primero carga datos en Inicio → Datos.")
        st.stop()

    df = st.session_state.df.copy()

    # -------------------------
    # Columnas (robusto a nombres distintos)
    # -------------------------
    country_col = next((c for c in ["countryname", "country", "country_name"] if c in df.columns), None)
    if country_col is None:
        st.error("No se encontró columna de país (se esperaba 'countryname' o 'country').")
        st.stop()

    region_col = "region" if "region" in df.columns else None
    event_type_col = next((c for c in ["event_type_label", "event_type", "type"] if c in df.columns), None)

    if "year" not in df.columns:
        st.error("No se encontró la columna 'year'.")
        st.stop()

    # Estandarización para visualizaciones
    rename_map = {country_col: "country_display"}
    if event_type_col:
        rename_map[event_type_col] = "event_type_display"
    df = df.rename(columns=rename_map)

    # -------------------------
    # Paleta (derivada de tu imagen) — EVENTOS (total)
    # -------------------------
    CHORO_EVENTS = ["#b1c7df", "#23b7d9", "#1d7084"]  # claro → cyan → teal

    # -------------------------
    # 4 FILTROS ESENCIALES
    # -------------------------
    col_f1, col_f2, col_f3 = st.columns([1, 1.4, 1])

    # 1) Región
    with col_f1:
        if region_col:
            region_opts = sorted(df[region_col].dropna().unique().tolist())
            selected_regions = st.multiselect(
                "Región",
                options=region_opts,
                default=region_opts,
                key="event_regions"
            )
        else:
            selected_regions = []
            st.caption("ℹ️ El dataset no incluye columna de región; se omite este filtro.")

    # 2) País
    with col_f2:
        if selected_regions and region_col:
            country_opts = df[df[region_col].isin(selected_regions)]["country_display"].dropna().unique()
        else:
            country_opts = df["country_display"].dropna().unique()
        selected_countries = st.multiselect(
            "País",
            options=sorted(country_opts),
            default=[],
            key="event_countries"
        )

    # 3) Años
    with col_f3:
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        selected_years = st.slider(
            "Años",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="event_years"
        )

    # 4) Tipo de evento
    if "event_type_display" in df.columns:
        selected_event_types = st.multiselect(
            "Tipo de evento",
            options=sorted(df["event_type_display"].dropna().unique()),
            default=[],
            key="event_event_types"
        )
    else:
        selected_event_types = []

    # -------------------------
    # Aplicar filtros (EVENTOS TOTALES)
    # -------------------------
    fdf = df.copy()
    if selected_regions and region_col:
        fdf = fdf[fdf[region_col].isin(selected_regions)]
    if selected_countries:
        fdf = fdf[fdf["country_display"].isin(selected_countries)]
    fdf = fdf[(fdf["year"] >= selected_years[0]) & (fdf["year"] <= selected_years[1])]
    if selected_event_types and "event_type_display" in fdf.columns:
        fdf = fdf[fdf["event_type_display"].isin(selected_event_types)]

    # -------------------------
    # KPIs GLOBALES (totales)
    # -------------------------
    total_events = len(fdf)
    years_text = f"{selected_years[0]}–{selected_years[1]}"
    countries_count = fdf["country_display"].nunique()
    types_count = fdf["event_type_display"].nunique() if "event_type_display" in fdf.columns else "—"

    st.markdown("### Indicadores globales")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Eventos (total)", f"{total_events:,}")
    with k2:
        st.metric("Países incluidos", countries_count)
    with k3:
        st.metric("Periodo", years_text)
    with k4:
        st.metric("Tipos de evento", types_count)

    st.divider()

    # -------------------------
    # Agregación por país (EVENTOS TOTALES)
    # -------------------------
    import plotly.express as px

    grp_total = fdf.groupby("country_display").size().reset_index(name="value")

    if grp_total["value"].fillna(0).sum() == 0:
        st.info("No hay eventos para los filtros actuales.")
        st.stop()

    # -------------------------
    # Helper de mapa (coroplético profesional)
    # -------------------------
    def plot_map(data, title, scope, geo_kwargs=None):
        fig = px.choropleth(
            data_frame=data,
            locations="country_display",
            locationmode="country names",
            color="value",
            color_continuous_scale=CHORO_EVENTS,
            labels={"value": "Eventos (total)"},
            title=title,
            scope=scope,
            hover_name="country_display",
            hover_data={"value": ":,.0f"},
        )
        layout = dict(
            margin={"r":0, "t":46, "l":0, "b":0},
            height=540,
            coloraxis_colorbar=dict(
                title="Eventos",
                thickness=14,
                outlinewidth=0,
                tickformat=","
            ),
            font=dict(size=13),
        )
        if geo_kwargs:
            layout["geo"] = geo_kwargs
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # Mapas (África / América) o mundial si no hay región
    # -------------------------
    if region_col:
        africa_df = fdf[fdf[region_col].str.lower() == "africa"].copy()
        americas_df = fdf[fdf[region_col].str.lower().isin(["latinamerica", "latin america", "americas"])].copy()

        if not africa_df.empty and not americas_df.empty:
            colA, colB = st.columns(2)
            with colA:
                dfa = africa_df.groupby("country_display").size().reset_index(name="value")
                plot_map(dfa, "África · Eventos (total)", scope="africa")
            with colB:
                dfam = americas_df.groupby("country_display").size().reset_index(name="value")
                plot_map(
                    dfam, "América · Eventos (total)", scope="world",
                    geo_kwargs=dict(
                        projection_scale=1,
                        center=dict(lat=10, lon=-80),
                        lataxis_range=[-55, 60],
                        lonaxis_range=[-130, -30],
                    )
                )
        elif not africa_df.empty:
            dfa = africa_df.groupby("country_display").size().reset_index(name="value")
            plot_map(dfa, "África · Eventos (total)", scope="africa")
        elif not americas_df.empty:
            dfam = americas_df.groupby("country_display").size().reset_index(name="value")
            plot_map(
                dfam, "América · Eventos (total)", scope="world",
                geo_kwargs=dict(
                    projection_scale=1,
                    center=dict(lat=10, lon=-80),
                    lataxis_range=[-55, 60],
                    lonaxis_range=[-130, -30],
                )
            )
        else:
            st.info("🔍 No hay eventos disponibles para los filtros seleccionados.")
    else:
        # Sin columna de región: mapa mundial
        plot_map(grp_total, "Mapa por país · Eventos (total)", scope="world")

    # -------------------------
    # Descarga de datos filtrados
    # -------------------------
    st.download_button(
        "⬇️ Descargar datos filtrados (CSV)",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="scad_eventos_filtrado.csv",
        mime="text/csv"
    )
    
    # =====================================================================================
    # 3. PESTAÑA EXPLORADOR DE MUERTES
    # =====================================================================================
elif selected == "Explorador de Muertes":
    st.header("Explorador Geográfico de Muertes")
    st.caption("Distribución total de muertes por país con filtros esenciales y mapas coropléticos profesionales.")

    # -------------------------
    # Validación de datos
    # -------------------------
    if "df" not in st.session_state or st.session_state.df is None or st.session_state.df.empty:
        st.warning("⚠️ Primero carga datos en Inicio → Datos.")
        st.stop()
    df = st.session_state.df.copy()

    # -------------------------
    # Columnas (robusto a nombres distintos)
    # -------------------------
    # País
    country_col = next((c for c in ["countryname", "country", "country_name"] if c in df.columns), None)
    if country_col is None:
        st.error("No se encontró columna de país (se esperaba 'countryname' o 'country').")
        st.stop()

    # Región / Continente
    region_col = "region" if "region" in df.columns else None

    # Tipo de evento
    event_type_col = next((c for c in ["event_type_label", "event_type", "type"] if c in df.columns), None)

    # Año y muertes
    if "year" not in df.columns:
        st.error("No se encontró la columna 'year'.")
        st.stop()
    death_col = "ndeath" if "ndeath" in df.columns else None
    if not death_col:
        st.error("No se encontró la columna de muertes ('ndeath').")
        st.stop()

    # Estandarización para visualizaciones
    rename_map = {country_col: "country_display"}
    if event_type_col:
        rename_map[event_type_col] = "event_type_display"
    df = df.rename(columns=rename_map)

    # -------------------------
    # Paleta (rojos de tu paleta) — MUERTES
    # -------------------------
    CHORO_DEATHS = ["#e78c88", "#f0493e", "#7e130f"]  # claro → coral → rojo suave

    # -------------------------
    # 4 FILTROS ESENCIALES (en formatos variados)
    # -------------------------
    col_f1, col_f2, col_f3 = st.columns([1, 1.4, 1])

    # 1) Región (multiselect)
    with col_f1:
        if region_col:
            region_opts = sorted(df[region_col].dropna().unique().tolist())
            selected_regions = st.multiselect(
                "Región",
                options=region_opts,
                default=region_opts,
                key="death_regions"
            )
        else:
            selected_regions = []
            st.caption("ℹ️ El dataset no incluye columna de región; se omite este filtro.")

    # 2) País (multiselect condicionado por región)
    with col_f2:
        if selected_regions and region_col:
            country_opts = df[df[region_col].isin(selected_regions)]["country_display"].dropna().unique()
        else:
            country_opts = df["country_display"].dropna().unique()
        selected_countries = st.multiselect(
            "País",
            options=sorted(country_opts),
            default=[],
            key="death_countries"
        )

    # 3) Años (range slider)
    with col_f3:
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        selected_years = st.slider(
            "Años",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="death_years"
        )

    # 4) Tipo de evento (multiselect)
    if "event_type_display" in df.columns:
        selected_event_types = st.multiselect(
            "Tipo de evento",
            options=sorted(df["event_type_display"].dropna().unique()),
            default=[],
            key="death_event_types"
        )
    else:
        selected_event_types = []

    # -------------------------
    # Aplicar filtros (MUERTES TOTALES)
    # -------------------------
    fdf = df.copy()
    if selected_regions and region_col:
        fdf = fdf[fdf[region_col].isin(selected_regions)]
    if selected_countries:
        fdf = fdf[fdf["country_display"].isin(selected_countries)]
    fdf = fdf[(fdf["year"] >= selected_years[0]) & (fdf["year"] <= selected_years[1])]
    if selected_event_types and "event_type_display" in fdf.columns:
        fdf = fdf[fdf["event_type_display"].isin(selected_event_types)]

    # -------------------------
    # KPIs GLOBALES (totales, sin medias)
    # -------------------------
    total_deaths = int(fdf[death_col].fillna(0).sum())
    events_with_death = int((fdf[death_col].fillna(0) > 0).sum())
    countries_count = fdf["country_display"].nunique()
    years_text = f"{selected_years[0]}–{selected_years[1]}"
    # Top país por muertes
    top_country = (
        fdf.groupby("country_display")[death_col].sum().sort_values(ascending=False).head(1)
    )
    top_country_name = top_country.index[0] if not top_country.empty else "—"
    top_country_val = int(top_country.iloc[0]) if not top_country.empty else 0
    # Máx muertes en un solo evento
    max_deaths_event = int(fdf[death_col].fillna(0).max()) if not fdf.empty else 0

    st.markdown("### Indicadores globales")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Muertes (total)", f"{total_deaths:,}")
    with k2:
        st.metric("Eventos con muertes", f"{events_with_death:,}")
    with k3:
        st.metric("Países incluidos", countries_count)
    with k4:
        st.metric("Máx. en un evento", f"{max_deaths_event:,}")

    st.caption(f"🏅 País con más muertes: **{top_country_name}** ({top_country_val:,})")
    st.divider()

    # -------------------------
    # Agregación por país (MUERTES TOTALES)
    # -------------------------

    grp_deaths = fdf.groupby("country_display")[death_col].sum().reset_index(name="value")
    if grp_deaths["value"].fillna(0).sum() == 0:
        st.info("No hay muertes registradas para los filtros actuales.")
        st.stop()

    # -------------------------
    # Helper de mapa (coroplético profesional)
    # -------------------------
    def plot_map(data, title, scope, geo_kwargs=None):
        fig = px.choropleth(
            data_frame=data,
            locations="country_display",
            locationmode="country names",
            color="value",
            color_continuous_scale=CHORO_DEATHS,
            labels={"value": "Muertes (total)"},
            title=title,
            scope=scope,
            hover_name="country_display",
            hover_data={"value": ":,.0f"},
        )
        layout = dict(
            margin={"r":0, "t":46, "l":0, "b":0},
            height=540,
            coloraxis_colorbar=dict(
                title="Muertes",
                thickness=14,
                outlinewidth=0,
                tickformat=","
            ),
            font=dict(size=13),
        )
        if geo_kwargs:
            layout["geo"] = geo_kwargs
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # Mapas (África / América) o mundial si no hay región
    # -------------------------
    if region_col:
        africa_df = fdf[fdf[region_col].str.lower() == "africa"].copy()
        americas_df = fdf[fdf[region_col].str.lower().isin(["latinamerica", "latin america", "americas"])].copy()

        if not africa_df.empty and not americas_df.empty:
            colA, colB = st.columns(2)
            with colA:
                dfa = africa_df.groupby("country_display")[death_col].sum().reset_index(name="value")
                plot_map(dfa, "África · Muertes (total)", scope="africa")
            with colB:
                dfam = americas_df.groupby("country_display")[death_col].sum().reset_index(name="value")
                plot_map(
                    dfam, "América · Muertes (total)", scope="world",
                    geo_kwargs=dict(
                        projection_scale=1,
                        center=dict(lat=10, lon=-80),
                        lataxis_range=[-55, 60],
                        lonaxis_range=[-130, -30],
                    )
                )
        elif not africa_df.empty:
            dfa = africa_df.groupby("country_display")[death_col].sum().reset_index(name="value")
            plot_map(dfa, "África · Muertes (total)", scope="africa")
        elif not americas_df.empty:
            dfam = americas_df.groupby("country_display")[death_col].sum().reset_index(name="value")
            plot_map(
                dfam, "América · Muertes (total)", scope="world",
                geo_kwargs=dict(
                    projection_scale=1,
                    center=dict(lat=10, lon=-80),
                    lataxis_range=[-55, 60],
                    lonaxis_range=[-130, -30],
                )
            )
        else:
            st.info("🔍 No hay muertes disponibles para los filtros seleccionados.")
    else:
        # Sin columna de región: mapa mundial
        plot_map(grp_deaths, "Mapa por país · Muertes (total)", scope="world")

    # -------------------------
    # Descarga de datos filtrados y agregados
    # -------------------------
    cdl, cdr = st.columns(2)
    with cdl:
        st.download_button(
            "⬇️ Descargar filas filtradas (CSV)",
            data=fdf.to_csv(index=False).encode("utf-8"),
            file_name="scad_muertes_filtrado_rows.csv",
            mime="text/csv",
            use_container_width=True
        )
    with cdr:
        st.download_button(
            "⬇️ Descargar muertes por país (CSV)",
            data=grp_deaths.to_csv(index=False).encode("utf-8"),
            file_name="scad_muertes_por_pais.csv",
            mime="text/csv",
            use_container_width=True
        )
# =====================================================================================
# 4. PESTAÑA ESTADÍSTICAS GENERALES
# =====================================================================================
elif selected == "Estadísticas Generales":
    st.header("Estadísticas Generales")
    st.caption("Indicadores globales, tendencias y distribuciones por país y tipo de evento (totales).")

    # -------------------------
    # Validación de datos
    # -------------------------
    if "df" not in st.session_state or st.session_state.df is None or st.session_state.df.empty:
        st.warning("⚠️ Primero carga datos en Inicio → Datos.")
        st.stop()
    df = st.session_state.df.copy()

    # -------------------------
    # Columnas robustas
    # -------------------------
    country_col = next((c for c in ["countryname", "country", "country_name"] if c in df.columns), None)
    if country_col is None:
        st.error("No se encontró columna de país (se esperaba 'countryname' o 'country').")
        st.stop()

    region_col = "region" if "region" in df.columns else None
    event_type_col = next((c for c in ["event_type_label", "event_type", "type"] if c in df.columns), None)

    if "year" not in df.columns:
        st.error("No se encontró la columna 'year'.")
        st.stop()

    death_col = "ndeath" if "ndeath" in df.columns else None

    # Estandarización visual
    rename_map = {country_col: "country_display"}
    if event_type_col:
        rename_map[event_type_col] = "event_type_display"
    df = df.rename(columns=rename_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # -------------------------
    # Paleta corporativa
    # -------------------------
    PALETTE = {
        "teal_dark": "#1d7084",   # eventos
        "cyan": "#23b7d9",        # eventos
        "red": "#f0635e",         # muertes
        "blue_gray": "#b1c7df",   # apoyo
        "slate": "#8094a8",
        "gray_light": "#d9dad5",
    }
    CHORO_EVENTS = ["#b1c7df", "#23b7d9", "#1d7084"]
    CHORO_DEATHS = ["#ffd9d7", "#f28b84", "#f0635e"]

    # =========================
    # BLOQUE 1 · Filtros (esenciales + avanzados)
    # =========================
    with st.container():
        st.subheader("Filtros")

        # --- Detección de columnas opcionales ---
        sub_event_col = next((c for c in ["sub_event_type", "sub_event_type_label", "subtype"] if c in df.columns), None)
        admin1_col     = next((c for c in ["admin1", "adm1", "admin_1"] if c in df.columns), None)
        source_col     = next((c for c in ["source", "sources"] if c in df.columns), None)
        actors_col     = next((c for c in ["actors", "actor1", "actor", "parties"] if c in df.columns), None)
        pop_col        = next((c for c in ["population", "pop", "pop_est"] if c in df.columns), None)

        # --------- Filtros ESENCIALES ----------
        col_f1, col_f2, col_f3 = st.columns([1, 1.4, 1])

        # 1) Región
        with col_f1:
            if region_col:
                region_opts = sorted(df[region_col].dropna().unique().tolist())
                selected_regions = st.multiselect(
                    "Región",
                    options=region_opts,
                    default=region_opts,
                    key="stats_regions"
                )
            else:
                selected_regions = []
                st.caption("ℹ️ El dataset no incluye columna de región; se omite este filtro.")

        # 2) País
        with col_f2:
            if selected_regions and region_col:
                country_opts = df[df[region_col].isin(selected_regions)]["country_display"].dropna().unique()
            else:
                country_opts = df["country_display"].dropna().unique()
            selected_countries = st.multiselect(
                "País",
                options=sorted(country_opts),
                default=[],
                key="stats_countries"
            )

        # 3) Años
        with col_f3:
            min_year = int(df["year"].min())
            max_year = int(df["year"].max())
            selected_years = st.slider(
                "Años",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                key="stats_years"
            )

        # Tipo de evento
        if "event_type_display" in df.columns:
            selected_event_types = st.multiselect(
                "Tipo de evento",
                options=sorted(df["event_type_display"].dropna().unique()),
                default=[],
                key="stats_event_types"
            )
        else:
            selected_event_types = []

       # --------- Filtros AVANZADOS (layout dinámico sin huecos) ----------
        _active_adv = 0
        def _inc(flag): 
            return 1 if flag else 0

        # Preparar "fichas" de controles disponibles (cada item es una función que pinta y devuelve su valor)
        adv_controls = []

        # Subtipo
        if sub_event_col:
            def _ctl_subtype():
                vals = st.multiselect(
                    "Subtipo de evento",
                    options=sorted(df[sub_event_col].dropna().unique()),
                    default=[],
                    key="stats_subtypes"
                )
                return ("selected_subtypes", vals, _inc(len(vals) > 0))
            adv_controls.append(_ctl_subtype)

        # Actor (contiene)
        def _ctl_actor():
            val = st.text_input(
                "Actor (contiene)",
                value=st.session_state.get("stats_actor_query", ""),
                key="stats_actor_query",
                help="Búsqueda textual (no distingue mayúsculas)."
            )
            return ("actor_query", val, _inc(bool(val.strip())))
        adv_controls.append(_ctl_actor)

        # Fuente
        if source_col:
            def _ctl_source():
                ser = df[source_col].dropna().astype(str).str.split(r"[;,]").explode().str.strip()
                opts = sorted([s for s in ser.unique().tolist() if s])
                vals = st.multiselect("Fuente", options=opts, default=[], key="stats_sources")
                return ("selected_sources", vals, _inc(len(vals) > 0))
            adv_controls.append(_ctl_source)

        # Admin1
        if admin1_col:
            def _ctl_admin1():
                if selected_countries:
                    pool = df[df["country_display"].isin(selected_countries)][admin1_col]
                elif (region_col and selected_regions):
                    pool = df[df[region_col].isin(selected_regions)][admin1_col]
                else:
                    pool = df[admin1_col]
                opts = sorted(pool.dropna().astype(str).unique().tolist())
                vals = st.multiselect("División administrativa (Admin1)", options=opts, default=[], key="stats_admin1")
                return ("selected_admin1", vals, _inc(len(vals) > 0))
            adv_controls.append(_ctl_admin1)

        # Umbral mínimo de muertes
        if death_col:
            def _ctl_min_deaths():
                val = st.number_input(
                    "Umbral mínimo de muertes",
                    min_value=0, value=0, step=1, key="stats_min_deaths",
                    help="Filtra filas con muertes < umbral."
                )
                return ("min_deaths", val, _inc(val > 0))
            adv_controls.append(_ctl_min_deaths)

        # Top-N
        def _ctl_topn():
            val = st.number_input("Top-N países en rankings", min_value=5, max_value=30, value=10, step=1, key="stats_topn")
            return ("top_n", val, 0)
        adv_controls.append(_ctl_topn)

        # Suavizado temporal
        def _ctl_smooth():
            val = st.number_input(
                "Suavizado temporal (ventana rolling)",
                min_value=1, max_value=7, value=1, step=1, key="stats_smooth",
                help="Aplica media móvil a series si > 1."
            )
            return ("smooth_win", val, _inc(val > 1))
        adv_controls.append(_ctl_smooth)

        # Normalización por población
        if pop_col:
            def _ctl_normpop():
                val = st.checkbox("Normalizar por población (por 100k hab.)", value=False, key="stats_norm_pop")
                if val:
                    st.caption(f"Usando columna de población: **{pop_col}**")
                return ("normalize_by_pop", val, _inc(val))
            adv_controls.append(_ctl_normpop)

        # Render dinámico en filas de 2, sin columnas vacías
        values = {}
        with st.expander("➕ Filtros avanzados (opcionales)", expanded=False):
            for i in range(0, len(adv_controls), 2):
                row_ctls = adv_controls[i:i+2]
                cols = st.columns(len(row_ctls))
                for fn, col in zip(row_ctls, cols):
                    with col:
                        key, val, inc = fn()
                        values[key] = val
                        _active_adv += inc

        # Asignar variables para el bloque de filtros
        selected_subtypes  = values.get("selected_subtypes", [])
        actor_query        = values.get("actor_query", "")
        selected_sources   = values.get("selected_sources", [])
        selected_admin1    = values.get("selected_admin1", [])
        min_deaths         = values.get("min_deaths", 0)
        top_n              = int(values.get("top_n", 10))
        smooth_win         = int(values.get("smooth_win", 1))
        normalize_by_pop   = bool(values.get("normalize_by_pop", False))

        # Badge de estado (opcional)
        if _active_adv > 0:
            st.caption(f"🔧 Filtros avanzados activos: **{_active_adv}**")

    # =========================
    # Aplicar filtros
    # =========================
    fdf = df.copy()

    # Esenciales
    if selected_regions and region_col:
        fdf = fdf[fdf[region_col].isin(selected_regions)]
    if selected_countries:
        fdf = fdf[fdf["country_display"].isin(selected_countries)]
    fdf = fdf[(fdf["year"] >= selected_years[0]) & (fdf["year"] <= selected_years[1])]
    if selected_event_types and "event_type_display" in fdf.columns:
        fdf = fdf[fdf["event_type_display"].isin(selected_event_types)]

    # Avanzados
    if sub_event_col and 'selected_subtypes' in locals() and selected_subtypes:
        fdf = fdf[fdf[sub_event_col].isin(selected_subtypes)]

    if actors_col and actor_query:
        fdf = fdf[fdf[actors_col].astype(str).str.contains(actor_query, case=False, na=False)]

    if source_col and selected_sources:
        exploded = fdf.assign(_src=fdf[source_col].astype(str).str.split(r"[;,]")).explode("_src")
        exploded["_src"] = exploded["_src"].str.strip()
        fdf = exploded[exploded["_src"].isin(selected_sources)].drop(columns=["_src"])

    if admin1_col and selected_admin1:
        fdf = fdf[fdf[admin1_col].astype(str).isin(selected_admin1)]

    if death_col and min_deaths > 0:
        fdf = fdf[fdf[death_col].fillna(0) >= min_deaths]

    # =========================
    # Helpers de visualización
    # =========================
    import plotly.express as px

    def _layout_pro(fig, legend=True, h=420):
        fig.update_layout(
            margin=dict(l=0, r=0, t=48, b=0),
            height=h,
            font=dict(size=13),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0) if legend else None,
        )
        return fig

    # =========================
    # BLOQUE 2 · KPIs globales
    # =========================
    with st.container():
        st.subheader("Indicadores globales")

        # Eventos totales
        total_events = len(fdf)

        # Muertes totales
        total_deaths = int(fdf[death_col].fillna(0).sum()) if death_col else None

        # Población total (si hay normalización)
        total_pop = None
        if normalize_by_pop and pop_col:
            # Tomamos población única por país (si la columna es por país)
            pop_map = df[["country_display", pop_col]].drop_duplicates().dropna()
            total_pop = pop_map[pop_col].sum() if not pop_map.empty else None

        countries_count = fdf["country_display"].nunique()
        types_count = fdf["event_type_display"].nunique() if "event_type_display" in fdf.columns else "—"
        years_text = f"{selected_years[0]}–{selected_years[1]}"

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Eventos (total)", f"{total_events:,}")
        with k2:
            st.metric("Muertes (total)", f"{total_deaths:,}" if total_deaths is not None else "—")
        with k3:
            st.metric("Países incluidos", countries_count)
        with k4:
            st.metric("Periodo", years_text)

        if normalize_by_pop and total_pop:
            st.caption(f"Normalización activa: métricas ‘por 100k hab.’ calculadas con población total ≈ {int(total_pop):,}")

    st.divider()

    # =========================
    # BLOQUE 3 · Tendencias temporales (con suavizado y normalización opcional)
    # =========================
    with st.container():
        st.subheader("📉 Tendencias temporales")
        col1, col2 = st.columns(2)

        # Eventos por año
        with col1:
            ts_e = fdf.groupby("year").size().reset_index(name="Eventos")
            if normalize_by_pop and pop_col:
                # población total aprox: suma por países filtrados
                pop_map = df[df["country_display"].isin(fdf["country_display"].unique())][["country_display", pop_col]].drop_duplicates().dropna()
                tot_pop = pop_map[pop_col].sum() if not pop_map.empty else None
                if tot_pop:
                    ts_e["Eventos"] = (ts_e["Eventos"] / tot_pop) * 100000
                    y_title = "Eventos por 100k hab."
                else:
                    y_title = "Eventos"
            else:
                y_title = "Eventos"

            if ts_e.empty:
                st.info("Sin datos para la tendencia de eventos.")
            else:
                if smooth_win > 1:
                    ts_e["Eventos"] = ts_e["Eventos"].rolling(smooth_win, min_periods=1).mean()
                fig = px.line(ts_e, x="year", y="Eventos", markers=True, title=f"Eventos por año ({y_title})")
                fig.update_traces(line=dict(color=PALETTE["teal_dark"], width=3),
                                  marker=dict(color=PALETTE["cyan"], size=7))
                st.plotly_chart(_layout_pro(fig), use_container_width=True)

        # Muertes por año
        with col2:
            if death_col:
                ts_d = fdf.groupby("year")[death_col].sum().reset_index(name="Muertes")
                if normalize_by_pop and pop_col:
                    pop_map = df[df["country_display"].isin(fdf["country_display"].unique())][["country_display", pop_col]].drop_duplicates().dropna()
                    tot_pop = pop_map[pop_col].sum() if not pop_map.empty else None
                    if tot_pop:
                        ts_d["Muertes"] = (ts_d["Muertes"] / tot_pop) * 100000
                        y_title = "Muertes por 100k hab."
                    else:
                        y_title = "Muertes"
                else:
                    y_title = "Muertes"

                if ts_d.empty or (ts_d["Muertes"].fillna(0).sum() == 0 and not normalize_by_pop):
                    st.info("Sin datos suficientes para la tendencia de muertes.")
                else:
                    if smooth_win > 1:
                        ts_d["Muertes"] = ts_d["Muertes"].rolling(smooth_win, min_periods=1).mean()
                    fig = px.line(ts_d, x="year", y="Muertes", markers=True, title=f"Muertes por año ({y_title})")
                    fig.update_traces(line=dict(color=PALETTE["red"], width=3),
                                      marker=dict(color=PALETTE["red"], size=7))
                    st.plotly_chart(_layout_pro(fig), use_container_width=True)
            else:
                st.info("No hay columna de muertes en el dataset.")

    st.divider()

    # =========================
    # BLOQUE 4 · Rankings (Top-N países)
    # =========================
    with st.container():
        st.subheader("🏆 Rankings por país")
        col3, col4 = st.columns(2)

        # Eventos
        with col3:
            rank_e = fdf.groupby("country_display").size().reset_index(name="Eventos")
            if normalize_by_pop and pop_col:
                pop_map = df[["country_display", pop_col]].drop_duplicates()
                rank_e = rank_e.merge(pop_map, on="country_display", how="left")
                rank_e["Eventos_norm"] = (rank_e["Eventos"] / rank_e[pop_col]) * 100000
                rank_e = rank_e.dropna(subset=["Eventos_norm"]).sort_values("Eventos_norm", ascending=False).head(int(top_n))
                x_col, title = "Eventos_norm", f"Top {int(top_n)} países · Eventos por 100k hab."
            else:
                rank_e = rank_e.sort_values("Eventos", ascending=False).head(int(top_n))
                x_col, title = "Eventos", f"Top {int(top_n)} países · Eventos (total)"

            if rank_e.empty:
                st.info("Sin datos para el ranking de eventos.")
            else:
                fig = px.bar(rank_e, x=x_col, y="country_display", orientation="h", title=title)
                fig.update_traces(marker_color=PALETTE["teal_dark"])
                fig.update_yaxes(categoryorder="total ascending", title=None)
                st.plotly_chart(_layout_pro(fig, legend=False), use_container_width=True)

        # Muertes
        with col4:
            if death_col:
                rank_d = fdf.groupby("country_display")[death_col].sum().reset_index(name="Muertes")
                if normalize_by_pop and pop_col:
                    pop_map = df[["country_display", pop_col]].drop_duplicates()
                    rank_d = rank_d.merge(pop_map, on="country_display", how="left")
                    rank_d["Muertes_norm"] = (rank_d["Muertes"] / rank_d[pop_col]) * 100000
                    rank_d = rank_d.dropna(subset=["Muertes_norm"]).sort_values("Muertes_norm", ascending=False).head(int(top_n))
                    x_col, title = "Muertes_norm", f"Top {int(top_n)} países · Muertes por 100k hab."
                else:
                    rank_d = rank_d.sort_values("Muertes", ascending=False).head(int(top_n))
                    x_col, title = "Muertes", f"Top {int(top_n)} países · Muertes (total)"

                if rank_d.empty or (rank_d[x_col].fillna(0).sum() == 0 and not normalize_by_pop):
                    st.info("Sin datos para el ranking de muertes.")
                else:
                    fig = px.bar(rank_d, x=x_col, y="country_display", orientation="h", title=title)
                    fig.update_traces(marker_color=PALETTE["red"])
                    fig.update_yaxes(categoryorder="total ascending", title=None)
                    st.plotly_chart(_layout_pro(fig, legend=False), use_container_width=True)
            else:
                st.info("No hay columna de muertes en el dataset.")

    st.divider()

    # =========================
    # BLOQUE 5 · Distribución por tipo de evento
    # =========================
    with st.container():
        st.subheader("📦 Distribución por tipo de evento")
        if "event_type_display" in fdf.columns:
            dist_types = (fdf.groupby("event_type_display").size()
                          .reset_index(name="Eventos")
                          .sort_values("Eventos", ascending=False))
            if not dist_types.empty:
                fig = px.bar(dist_types, x="event_type_display", y="Eventos", title="Eventos por tipo")
                fig.update_traces(marker_color=PALETTE["cyan"])
                fig.update_xaxes(title=None)
                st.plotly_chart(_layout_pro(fig, legend=False), use_container_width=True)
            else:
                st.info("Sin datos para la distribución por tipo.")
        else:
            st.caption("ℹ️ No hay columna de tipo de evento en el dataset.")

    st.divider()

    # =========================
    # BLOQUE 6 · Heatmap (Año × Región / País)
    # =========================
    with st.container():
        st.subheader("🔥 Heatmap")
        if region_col:
            heat = fdf.groupby(["year", region_col]).size().reset_index(name="Eventos")
            if not heat.empty:
                fig = px.density_heatmap(
                    heat, x="year", y=region_col, z="Eventos",
                    color_continuous_scale=[PALETTE["blue_gray"], PALETTE["cyan"], PALETTE["teal_dark"]],
                    title="Eventos por año y región"
                )
                st.plotly_chart(_layout_pro(fig), use_container_width=True)
            else:
                st.info("Sin datos para el heatmap por región.")
        else:
            # Sin región: top-8 países para no saturar
            top8 = (fdf.groupby("country_display").size()
                    .sort_values(ascending=False).head(8).index.tolist())
            heat = (fdf[fdf["country_display"].isin(top8)]
                    .groupby(["year", "country_display"]).size().reset_index(name="Eventos"))
            if not heat.empty:
                fig = px.density_heatmap(
                    heat, x="year", y="country_display", z="Eventos",
                    color_continuous_scale=[PALETTE["blue_gray"], PALETTE["cyan"], PALETTE["teal_dark"]],
                    title="Eventos por año y país (top 8)"
                )
                st.plotly_chart(_layout_pro(fig), use_container_width=True)
            else:
                st.info("Sin datos para el heatmap por país.")

    st.divider()

    # =========================
    # BLOQUE 7 · Tabla resumen y descargas
    # =========================
    with st.container():
        st.subheader("📄 Resumen por país")
        country_events = fdf.groupby("country_display").size().reset_index(name="Eventos")
        if death_col:
            country_deaths = fdf.groupby("country_display")[death_col].sum().reset_index(name="Muertes")
            summary = pd.merge(country_events, country_deaths, on="country_display", how="left")
        else:
            summary = country_events.copy()

        # Normalización por 100k (si procede)
        if normalize_by_pop and pop_col:
            pop_map = df[["country_display", pop_col]].drop_duplicates()
            summary = summary.merge(pop_map, on="country_display", how="left")
            summary["Eventos_100k"] = (summary["Eventos"] / summary[pop_col]) * 100000
            if "Muertes" in summary.columns:
                summary["Muertes_100k"] = (summary["Muertes"] / summary[pop_col]) * 100000

        st.dataframe(summary.sort_values(by="Eventos", ascending=False), use_container_width=True)

        cdl, cdr = st.columns(2)
        with cdl:
            st.download_button(
                "⬇️ Descargar filas filtradas (CSV)",
                data=fdf.to_csv(index=False).encode("utf-8"),
                file_name="scad_estadisticas_filtrado.csv",
                mime="text/csv",
                use_container_width=True
            )
        with cdr:
            st.download_button(
                "⬇️ Descargar resumen por país (CSV)",
                data=summary.to_csv(index=False).encode("utf-8"),
                file_name="scad_estadisticas_resumen_pais.csv",
                mime="text/csv",
                use_container_width=True
            )

# =====================================================================================
# 5. ANALISIS POR RELIGION
# =====================================================================================
elif selected == "Análisis por Religión":
    st.header("Análisis de Conflictos Religiosos y Étnicos")
    st.caption("Eventos identificados por palabras clave en columnas de tema (issue1_label / issue_main). Filtros: Región y Años.")

    # -------------------------
    # Validación y preparación de columnas
    # -------------------------
    if "df" not in st.session_state or st.session_state.df is None or st.session_state.df.empty:
        st.warning("⚠️ Primero carga datos en Inicio → Datos.")
        st.stop()
    df = st.session_state.df.copy()

    country_col = next((c for c in ["countryname", "country", "country_name"] if c in df.columns), None)
    if not country_col:
        st.error("No se encontró la columna de país (p. ej., 'countryname').")
        st.stop()

    region_col = "region" if "region" in df.columns else None
    if "year" not in df.columns:
        st.error("No se encontró la columna 'year'.")
        st.stop()
    death_col = "ndeath" if "ndeath" in df.columns else None
    event_type_col = next((c for c in ["event_type_label", "event_type", "type"] if c in df.columns), None)

    # Estandarización mínima
    rename_map = {country_col: "country_display"}
    if event_type_col:
        rename_map[event_type_col] = "event_type_display"
    df = df.rename(columns=rename_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # -------------------------
    # Paleta divergente (azules ↔ neutro ↔ rojos)
    # -------------------------
    RELIGION_SCALE = [
        "#1f77b4",  # azul fuerte
        "#1fa2e0",  # azul medio
        "#5bc0eb",  # azul claro
        "#9dd6f5",  # azul muy claro
        "#e0e0e0",  # gris neutro
        "#f4a896",  # rojo claro
        "#e76f51",  # rojo medio
        "#e63946",  # rojo intenso
        "#b81d13",  # rojo oscuro
    ]
    COLOR_EVENTS = "#1f77b4"  # barras eventos (azul fuerte)
    COLOR_RANK   = "#e63946"  # ranking países (rojo intenso)

    # -------------------------
    # Detección por palabras clave (igual al original)
    # -------------------------
    if not {"issue1_label", "issue_main"}.intersection(df.columns):
        st.error("No se encontraron columnas 'issue1_label' o 'issue_main' en el dataset.")
        st.stop()

    religion_keywords = [
        "religio", "ethnic", "étnico", "identidad", "discriminación", "discrimination",
        "muslim", "cristian", "christian", "islam", "hindu", "jew", "judío"
    ]
    regex = "|".join(religion_keywords)

    mask = pd.Series(False, index=df.index)
    if "issue1_label" in df.columns:
        mask = mask | df["issue1_label"].astype(str).str.contains(regex, case=False, na=False)
    if "issue_main" in df.columns:
        mask = mask | df["issue_main"].astype(str).str.contains(regex, case=False, na=False)

    religion_df = df[mask].copy()
    st.info(f"Se encontraron **{len(religion_df):,}** eventos relacionados con religión o identidad étnica.")

    if religion_df.empty:
        st.warning("No se encontraron eventos con temas religiosos en el dataset actual.")
        st.stop()

    # -------------------------
    # Filtros ESENCIALES (solo Región y Años)
    # -------------------------
    st.subheader("Filtros")
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        if region_col:
            region_opts = sorted(religion_df[region_col].dropna().unique().tolist())
            religion_regions = st.multiselect(
                "Región",
                options=region_opts,
                default=region_opts,
                key="religion_region"
            )
        else:
            religion_regions = []
            st.caption("ℹ️ El dataset no incluye columna de región; se omite este filtro.")

    with col_r2:
        min_year = int(religion_df["year"].min())
        max_year = int(religion_df["year"].max())
        religion_years = st.slider(
            "Años",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="religion_years"
        )

    # Aplicar filtros
    fdf = religion_df.copy()
    if religion_regions and region_col:
        fdf = fdf[fdf[region_col].isin(religion_regions)]
    fdf = fdf[(fdf["year"] >= religion_years[0]) & (fdf["year"] <= religion_years[1])]

    # -------------------------
    # KPIs globales (totales)
    # -------------------------
    st.subheader("Resumen")
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Eventos religiosos/étnicos", f"{len(fdf):,}")
    with k2:
        if death_col:
            st.metric("Muertes totales", f"{int(fdf[death_col].fillna(0).sum()):,}")
        else:
            st.metric("Muertes totales", "—")
    with k3:
        st.metric("Países involucrados", fdf["country_display"].nunique())

    st.divider()

    # -------------------------
    # GRÁFICO 1 · Eventos por año (barras azules)
    # -------------------------
    import plotly.express as px

    st.subheader("🕌 Eventos religiosos/étnicos por año")
    by_year = fdf.groupby("year").size().reset_index(name="Eventos")
    if by_year.empty:
        st.info("Sin datos para la serie temporal.")
    else:
        fig_year = px.bar(by_year, x="year", y="Eventos", title="Eventos por año")
        fig_year.update_traces(marker_color=COLOR_EVENTS)
        fig_year.update_layout(margin=dict(l=0, r=0, t=48, b=0), height=420, font=dict(size=13))
        st.plotly_chart(fig_year, use_container_width=True)

    # -------------------------
    # GRÁFICO 2 · Distribución por tema (pie con escala diverging)
    # -------------------------
    st.subheader("📌 Temas religiosos/étnicos")
    if "issue1_label" in fdf.columns:
        topics = fdf["issue1_label"].dropna().value_counts().reset_index()
        topics.columns = ["Tema", "Eventos"]
        if topics.empty:
            st.info("Sin datos para la distribución por tema.")
        else:
            fig_topics = px.pie(
                topics.head(12),
                values="Eventos",
                names="Tema",
                title="Distribución por tema (Top 12)",
                color_discrete_sequence=RELIGION_SCALE
            )
            fig_topics.update_layout(margin=dict(l=0, r=0, t=48, b=0), height=420, font=dict(size=13), legend_title_text="")
            st.plotly_chart(fig_topics, use_container_width=True)
    else:
        st.caption("ℹ️ No hay columna 'issue1_label' para la distribución por tema.")

    # -------------------------
    # GRÁFICO 3 · Top países (barra horizontal roja)
    # -------------------------
    st.subheader("🧭 Top países por conflictos religiosos/étnicos")
    top_countries = (
        fdf.groupby("country_display").size()
          .reset_index(name="Eventos")
          .sort_values("Eventos", ascending=False)
          .head(10)
    )
    if top_countries.empty:
        st.info("Sin datos para el ranking por país.")
    else:
        fig_countries = px.bar(
            top_countries, x="Eventos", y="country_display",
            orientation="h", title="Top 10 países por eventos"
        )
        fig_countries.update_traces(marker_color=COLOR_RANK)
        fig_countries.update_yaxes(categoryorder="total ascending", title=None)
        fig_countries.update_layout(margin=dict(l=0, r=0, t=48, b=0), height=460, font=dict(size=13))
        st.plotly_chart(fig_countries, use_container_width=True)

    st.divider()

    # -------------------------
    # Tabla de detalle
    # -------------------------
    st.subheader("📋 Datos detallados")
    cols_show = [c for c in ["year", "country_display", "event_type_display", "issue1_label", "ndeath", "actor1", "target1"] if c in fdf.columns]
    if not cols_show:
        cols_show = fdf.columns.tolist()[:8]
    st.dataframe(fdf[cols_show].reset_index(drop=True), use_container_width=True)

# =====================================================================================
# 6. PESTAÑA
# =====================================================================================
elif selected == "Conclusiones":
    st.header("Conclusiones")
    st.caption("Análisis del Social Conflict Analysis Database (SCAD), 1990–2018. Cobertura: África subsahariana y América Latina.")

    st.markdown("""
    El análisis del dataset SCAD permite identificar patrones estructurales, tendencias temporales y dinámicas geográficas en los conflictos sociales y políticos registrados entre 1990 y 2018. A continuación se presentan hallazgos organizados en ejes temáticos fundamentales, basados en la codificación sistemática de actores, causas, tipos de violencia y localización de los eventos.
    """)

    st.subheader("1. Tendencias temporales: picos de conflicto y sus contextos históricos")
    st.markdown("""
    El dataset revela varios picos significativos de actividad conflictiva, estrechamente vinculados a procesos políticos, económicos o de seguridad:

    - **1994–1996**: Aumento notable de eventos en Haití, República Dominicana y Sudáfrica. En Haití, la transición post-dictadura y la intervención internacional generaron represión estatal y violencia comunitaria. En Sudáfrica, persistieron tensiones étnicas (xhosas vs. sothos) en el periodo posterior al fin del apartheid.
    
    - **2000–2003**: Pico en Sierra Leona, Liberia y Costa de Marfil, coincidente con el colapso de acuerdos de paz y el resurgimiento de conflictos post-guerra civil. En Costa de Marfil, las protestas de jueces por salarios (2002) reflejan la fragilidad institucional previa al estallido de la guerra civil.

    - **2010–2012**: Máximo histórico de eventos en el conjunto del dataset. Este periodo incluye:
        - La **crisis post-electoral en Costa de Marfil** (2010–2011), con cientos de muertos.
        - La **insurgencia en el norte de Malí** (2012), tras el golpe de Estado y la expansión de grupos yihadistas.
        - El **auge de la violencia criminal en México**, especialmente en Ciudad Juárez, con masacres como la del Casino Royale (52 muertos en 2011) o los ataques a fiestas privadas (2010–2011).

    - **2015–2017**: Persistencia de violencia en México y surgimiento de nuevos focos en el Sahel (Níger, Chad) y el Cuerno de África (Somalia, Etiopía), vinculados a la expansión de Al-Shabaab y tensiones por recursos hídricos y ganaderos.

    Estos picos no son aleatorios: reflejan **transiciones políticas frágiles, vacíos de poder estatal y choques entre identidades colectivas** en contextos de debilidad institucional.
    """)

    st.subheader("2. Distribución geográfica: países y regiones con mayor incidencia")
    st.markdown("""
    El dataset está fuertemente concentrado en unos pocos países, lo que refleja tanto la intensidad del conflicto como la cobertura mediática:

    - **México** es, con diferencia, el país con más eventos en América Latina (más del 95% de los casos regionales). La violencia se concentra en estados como **Chihuahua (Ciudad Juárez), Sinaloa, Tamaulipas y Guerrero**, y está dominada por actores no estatales (cárteles, autodefensas, pandillas).

    - En **África**, los países con mayor número de eventos son:
        - **Nigeria**: por disputas étnico-religiosas (norte vs. sur), violencia del MEND en el Delta del Níger y ataques de Boko Haram (aunque este último rara vez se nombra explícitamente).
        - **Sudán y Sudán del Sur**: por conflictos étnicos (dinka vs. nuer), disputas por ganado y recursos petroleros.
        - **Costa de Marfil**: por tensiones post-coloniales entre "nativos" y migrantes, exacerbadas en periodos electorales.
        - **Somalia y Etiopía**: por inestabilidad estatal, presencia de Al-Shabaab y conflictos transfronterizos.

    La ausencia de países como Brasil, Colombia o Argentina no indica ausencia de conflicto, sino que el SCAD está diseñado para monitorear contextos de **alta fragilidad estatal**, no protestas en democracias consolidadas.
    """)

    st.subheader("3. Tipología de eventos: formas y motivaciones predominantes")
    st.markdown("""
    El SCAD clasifica los eventos en categorías que permiten distinguir entre protesta política, violencia criminal y conflicto comunitario:

    - **Manifestaciones y huelgas (no letales)**: Constituyen la mayoría de los eventos en África. Incluyen protestas de jueces (Costa de Marfil, 2002), estudiantes (República Dominicana, 1995), vendedores ambulantes (Santo Domingo, 1999) o comunidades por apagones eléctricos (2002–2003). Estos eventos suelen tener demandas concretas y actores identificables.

    - **Violencia letal no estatal**: Predomina en México y partes del Sahel. Incluye:
        - Ejecuciones masivas en fiestas privadas (Ciudad Juárez, 2010–2011).
        - Ataques a periodistas (Juchitán, 2016).
        - Masacres en cárceles (Matamoros, 2010).
        - Descuartizamientos y mensajes con cuerpos (San Quintín, 2015).
        Estos eventos rara vez tienen una causa política explícita y se clasifican como "unknown/not specified".

    - **Violencia comunitaria**: Muy presente en África. Incluye:
        - Linchamientos por rumores (Senegal, 1997: "encogimiento de genitales").
        - Enfrentamientos étnicos (Sudáfrica, 1996: xhosas vs. sothos).
        - Disputas por recursos (Sudán, 2007: 1,800 muertos en choques por ganado).
        Estos eventos reflejan la debilidad del Estado y la persistencia de mecanismos de justicia comunitaria.

    - **Represión estatal**: Documentada en Haití (1994–1996), Egipto (2013) y Cuba. Incluye redadas policiales, quemas de casas y detenciones arbitrarias, generalmente en respuesta a protestas o movimientos opositores.
    """)

    st.subheader("4. Causas subyacentes: motores estructurales del conflicto")
    st.markdown("""
    A pesar de la diversidad de eventos, es posible agrupar las causas en cuatro categorías fundamentales:

    - **Recursos y subsistencia**: Disputas por tierras, ganado, agua, electricidad o empleo. Son la causa más recurrente en zonas rurales de África y en barrios marginados de América Latina.

    - **Identidad colectiva**: Conflictos étnicos, religiosos o nacionales. Aparecen de forma persistente en Nigeria, Sudán, Costa de Marfil y Sudáfrica, y suelen escalar en periodos de transición política.

    - **Gobernanza y legitimidad**: Elecciones, corrupción, impunidad y represión. Los periodos electorales actúan como catalizadores en contextos de desconfianza institucional (Costa de Marfil 2010, Togo 2012).

    - **Crimen organizado**: En México, la violencia se articula en torno al tráfico de drogas, el control territorial y la imposición de normas paralelas al Estado. La opacidad de estos actores lleva a una alta proporción de eventos clasificados como "desconocidos".
    """)

    st.subheader("5. Implicaciones metodológicas y limitaciones")
    st.markdown("""
    El SCAD es una herramienta valiosa, pero está sujeto a sesgos inherentes a su metodología:

    - **Sesgo de visibilidad**: Los eventos dependen de la cobertura de agencias internacionales (AP, AFP, Reuters), lo que puede subrepresentar zonas remotas o conflictos de baja intensidad.
    
    - **Subregistro de violencia estructural**: Formas de violencia como la doméstica, la de género o la económica sistémica no aparecen, ya que el SCAD se centra en eventos colectivos y públicos.

    - **Dificultad de atribución**: En contextos de criminalidad organizada o insurgencia difusa, la identificación precisa de actores y motivaciones es frecuentemente imposible, lo que lleva a categorías genéricas como "desconocido" o "no especificado".

    Estas limitaciones no invalidan el dataset, pero sí exigen cautela al generalizar sus hallazgos.
    """)

    st.subheader("6. Reflexión final")
    st.markdown("""
    Los conflictos sociales no son meros brotes de caos, sino expresiones de demandas, frustraciones y disputas por el poder, la identidad y los recursos. El SCAD, al registrar desde huelgas judiciales hasta masacres en fiestas privadas, captura la complejidad de estas dinámicas en contextos de fragilidad estatal. Comprenderlas en su diversidad —temporal, geográfica y temática— es esencial para diseñar políticas de prevención y resolución de conflictos contextualizadas, efectivas y sostenibles.
    """)