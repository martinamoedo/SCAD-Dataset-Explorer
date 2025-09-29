import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="SCAD Dataset Explorer",
    page_icon="🌍",
    layout="wide"
)

# Título principal
st.title("🌍 SCAD Dataset Explorer")
st.markdown("### Análisis de conflictos sociales en África y América Latina (1990-2018)")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("exploratory_data\scad_final_dataset.csv")
    
    # Intentar encontrar la columna del año
    year_col_candidates = [col for col in df.columns if 'year' in col.lower() or 'año' in col.lower()]
    if len(year_col_candidates) > 0:
        year_col = year_col_candidates[0]
    else:
        st.error("❌ No se encontró ninguna columna que parezca contener el año.")
        st.stop()
    
    # Renombrar la columna encontrada a 'year'
    df = df.rename(columns={year_col: 'year'})
    
    # Limpiar y convertir
    df.columns = df.columns.str.strip()
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['ndeath'] = pd.to_numeric(df['ndeath'], errors='coerce')
    
    return df

# Cargar el DataFrame
df = load_data()

# Crear pestañas
tab_inicio, tab_eventos, tab_muertes, tab_estadisticas, tab_religion, tab_conclusiones = st.tabs([
    "🏠 Inicio", 
    "🗺️ Explorador de Eventos", 
    "💀 Explorador de Muertes",
    "📊 Estadísticas Generales", 
    "🕌 Análisis por Religión", 
    "✅ Conclusiones"
])

# -------------------------------
# PESTAÑA 1: INICIO
# -------------------------------
with tab_inicio:
    st.header("Bienvenido al Explorador SCAD")
    st.write("Esta herramienta permite analizar eventos de conflicto social en África y América Latina entre 1990 y 2018.")
    st.markdown("""
    - 🗺️ **Pestaña 2**: Filtra y visualiza eventos en mapas interactivos.
    - 💀 **Pestaña 3**: Filtra y visualiza **muertes** en mapas interactivos.
    - 📊 **Pestaña 4**: Explora estadísticas generales con gráficos dinámicos.
    - 🕌 **Pestaña 5**: Analiza eventos relacionados con religión e identidad.
    - ✅ **Pestaña 6**: Próximamente: conclusiones y hallazgos clave.
    """)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Flag-map_of_the_world.png/1280px-Flag-map_of_the_world.png", 
             caption="Cobertura geográfica: África y América Latina", use_column_width=True)

# -------------------------------
# PESTAÑA 2: EXPLORADOR DE EVENTOS (SOLO NÚMERO DE EVENTOS)
# -------------------------------
with tab_eventos:
    st.header("🗺️ Explorador Geográfico de Eventos")
    
    # Filtros dentro de la pestaña (sin sidebar)
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        region_options = df['region'].dropna().unique()
        selected_regions = st.multiselect(
            "Selecciona Continentes",
            options=region_options,
            default=region_options,
            key="event_regions"
        )
    
    with col_filtro2:
        country_options = df[df['region'].isin(selected_regions)]['countryname'].dropna().unique() if selected_regions else df['countryname'].dropna().unique()
        selected_countries = st.multiselect(
            "Selecciona Países",
            options=sorted(country_options),
            default=[],
            key="event_countries"
        )
    
    with col_filtro3:
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        selected_years = st.slider(
            "Rango de Años",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="event_years"
        )
    
    # Filtros adicionales en otra fila
    col_filtro4, col_filtro5 = st.columns(2)
    
    with col_filtro4:
        event_type_options = df['event_type_label'].dropna().unique()
        selected_event_types = st.multiselect(
            "Tipo de Evento",
            options=sorted(event_type_options),
            default=[],
            key="event_event_types"
        )
    
    with col_filtro5:
        min_deaths = st.slider(
            "Muertes Mínimas",
            min_value=0,
            max_value=int(df['ndeath'].max()) if not df['ndeath'].isna().all() else 0,
            value=0,
            key="event_min_deaths"
        )
    
    # Aplicar filtros
    filtered_df = df.copy()
    if selected_regions:
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df['countryname'].isin(selected_countries)]
    filtered_df = filtered_df[
        (filtered_df['year'] >= selected_years[0]) &
        (filtered_df['year'] <= selected_years[1])
    ]
    if selected_event_types:
        filtered_df = filtered_df[filtered_df['event_type_label'].isin(selected_event_types)]
    filtered_df = filtered_df[filtered_df['ndeath'] >= min_deaths]
    
    # Mostrar métricas rápidas
    st.markdown("### 📈 Resumen de Filtros Aplicados")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Eventos Totales", len(filtered_df))
    with col_m2:
        st.metric("Muertes Totales", int(filtered_df['ndeath'].sum()) if not filtered_df['ndeath'].isna().all() else 0)
    with col_m3:
        st.metric("Países Incluidos", filtered_df['countryname'].nunique())
    
    # Dividir datos por continente
    africa_df = filtered_df[filtered_df['region'] == 'africa'].copy()
    americas_df = filtered_df[filtered_df['region'] == 'latinamerica'].copy()
    
    # Determinar qué mapas mostrar
    show_africa = not selected_countries or (df[(df['countryname'].isin(selected_countries)) & (df['region'] == 'africa')].shape[0] > 0)
    show_americas = not selected_countries or (df[(df['countryname'].isin(selected_countries)) & (df['region'] == 'latinamerica')].shape[0] > 0)
    show_africa = show_africa and not africa_df.empty
    show_americas = show_americas and not americas_df.empty

    # Preparar datos para África (NÚMERO DE EVENTOS)
    africa_data = africa_df.groupby('countryname').size().reset_index(name='value')
    americas_data = americas_df.groupby('countryname').size().reset_index(name='value')
    color_label = "Número de Eventos"

    # Crear mapas
    if show_africa and show_americas:
        col_africa, col_americas = st.columns(2)
        
        with col_africa:
            st.markdown("### 🌍 África")
            fig_africa = px.choropleth(
                africa_data,
                locations='countryname',
                locationmode='country names',
                color='value',
                color_continuous_scale='Blues',
                labels={'value': color_label},
                title=f'África: {color_label}',
                scope='africa',
                hover_name='countryname'
            )
            fig_africa.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=500)
            st.plotly_chart(fig_africa, use_container_width=True)
        
        with col_americas:
            st.markdown("### 🌎 América")
            fig_americas = px.choropleth(
                americas_data,
                locations='countryname',
                locationmode='country names',
                color='value',
                color_continuous_scale='Blues',
                labels={'value': color_label},
                title=f'América: {color_label}',
                scope='world',
                hover_name='countryname'
            )
            fig_americas.update_layout(
                margin={"r":0,"t":40,"l":0,"b":0},
                height=500,
                geo=dict(
                    projection_scale=1,
                    center=dict(lat=10, lon=-80),
                    lataxis_range=[-55, 60],
                    lonaxis_range=[-130, -30]
                )
            )
            st.plotly_chart(fig_americas, use_container_width=True)
            
    elif show_africa:
        st.markdown("### 🌍 Mapa de África")
        fig_africa = px.choropleth(
            africa_data,
            locations='countryname',
            locationmode='country names',
            color='value',
            color_continuous_scale='Blues',
            labels={'value': color_label},
            title=f'África: {color_label}',
            scope='africa',
            hover_name='countryname'
        )
        fig_africa.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
        st.plotly_chart(fig_africa, use_container_width=True)
        
    elif show_americas:
        st.markdown("### 🌎 Mapa de América")
        fig_americas = px.choropleth(
            americas_data,
            locations='countryname',
            locationmode='country names',
            color='value',
            color_continuous_scale='Blues',
            labels={'value': color_label},
            title=f'América: {color_label}',
            scope='world',
            hover_name='countryname'
        )
        fig_americas.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            height=600,
            geo=dict(
                projection_scale=1,
                center=dict(lat=10, lon=-80),
                lataxis_range=[-55, 60],
                lonaxis_range=[-130, -30]
            )
        )
        st.plotly_chart(fig_americas, use_container_width=True)
        
    else:
        st.info("🔍 No hay datos disponibles para los filtros seleccionados.")

# -------------------------------
# PESTAÑA 3: EXPLORADOR DE MUERTES (SOLO MUERTES TOTALES)
# -------------------------------
with tab_muertes:
    st.header("💀 Explorador Geográfico de Muertes")
    
    # Filtros dentro de la pestaña (sin sidebar) — MISMO FORMATO QUE EVENTOS
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        region_options = df['region'].dropna().unique()
        selected_regions = st.multiselect(
            "Selecciona Continentes",
            options=region_options,
            default=region_options,
            key="death_regions"
        )
    
    with col_filtro2:
        country_options = df[df['region'].isin(selected_regions)]['countryname'].dropna().unique() if selected_regions else df['countryname'].dropna().unique()
        selected_countries = st.multiselect(
            "Selecciona Países",
            options=sorted(country_options),
            default=[],
            key="death_countries"
        )
    
    with col_filtro3:
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        selected_years = st.slider(
            "Rango de Años",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="death_years"
        )
    
    # Filtros adicionales en otra fila
    col_filtro4, col_filtro5 = st.columns(2)
    
    with col_filtro4:
        event_type_options = df['event_type_label'].dropna().unique()
        selected_event_types = st.multiselect(
            "Tipo de Evento",
            options=sorted(event_type_options),
            default=[],
            key="death_event_types"
        )
    
    with col_filtro5:
        min_deaths = st.slider(
            "Muertes Mínimas",
            min_value=0,
            max_value=int(df['ndeath'].max()) if not df['ndeath'].isna().all() else 0,
            value=0,
            key="death_min_deaths"
        )
    
    # Aplicar filtros
    filtered_df = df.copy()
    if selected_regions:
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df['countryname'].isin(selected_countries)]
    filtered_df = filtered_df[
        (filtered_df['year'] >= selected_years[0]) &
        (filtered_df['year'] <= selected_years[1])
    ]
    if selected_event_types:
        filtered_df = filtered_df[filtered_df['event_type_label'].isin(selected_event_types)]
    filtered_df = filtered_df[filtered_df['ndeath'] >= min_deaths]
    
    # Mostrar métricas rápidas
    st.markdown("### 📈 Resumen de Filtros Aplicados")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Eventos Totales", len(filtered_df))
    with col_m2:
        st.metric("Muertes Totales", int(filtered_df['ndeath'].sum()) if not filtered_df['ndeath'].isna().all() else 0)
    with col_m3:
        st.metric("Países Incluidos", filtered_df['countryname'].nunique())
    
    # Dividir datos por continente
    africa_df = filtered_df[filtered_df['region'] == 'africa'].copy()
    americas_df = filtered_df[filtered_df['region'] == 'latinamerica'].copy()
    
    # Determinar qué mapas mostrar
    show_africa = not selected_countries or (df[(df['countryname'].isin(selected_countries)) & (df['region'] == 'africa')].shape[0] > 0)
    show_americas = not selected_countries or (df[(df['countryname'].isin(selected_countries)) & (df['region'] == 'latinamerica')].shape[0] > 0)
    show_africa = show_africa and not africa_df.empty
    show_americas = show_americas and not americas_df.empty

    # Preparar datos para África (MUERTES TOTALES)
    africa_data = africa_df.groupby('countryname')['ndeath'].sum().reset_index(name='value')
    americas_data = americas_df.groupby('countryname')['ndeath'].sum().reset_index(name='value')
    color_label = "Muertes Totales"

    # Crear mapas
    if show_africa and show_americas:
        col_africa, col_americas = st.columns(2)
        
        with col_africa:
            st.markdown("### 🌍 África")
            fig_africa = px.choropleth(
                africa_data,
                locations='countryname',
                locationmode='country names',
                color='value',
                color_continuous_scale='Reds',
                labels={'value': color_label},
                title=f'África: {color_label}',
                scope='africa',
                hover_name='countryname'
            )
            fig_africa.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=500)
            st.plotly_chart(fig_africa, use_container_width=True)
        
        with col_americas:
            st.markdown("### 🌎 América")
            fig_americas = px.choropleth(
                americas_data,
                locations='countryname',
                locationmode='country names',
                color='value',
                color_continuous_scale='Reds',
                labels={'value': color_label},
                title=f'América: {color_label}',
                scope='world',
                hover_name='countryname'
            )
            fig_americas.update_layout(
                margin={"r":0,"t":40,"l":0,"b":0},
                height=500,
                geo=dict(
                    projection_scale=1,
                    center=dict(lat=10, lon=-80),
                    lataxis_range=[-55, 60],
                    lonaxis_range=[-130, -30]
                )
            )
            st.plotly_chart(fig_americas, use_container_width=True)
            
    elif show_africa:
        st.markdown("### 🌍 Mapa de África")
        fig_africa = px.choropleth(
            africa_data,
            locations='countryname',
            locationmode='country names',
            color='value',
            color_continuous_scale='Reds',
            labels={'value': color_label},
            title=f'África: {color_label}',
            scope='africa',
            hover_name='countryname'
        )
        fig_africa.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
        st.plotly_chart(fig_africa, use_container_width=True)
        
    elif show_americas:
        st.markdown("### 🌎 Mapa de América")
        fig_americas = px.choropleth(
            americas_data,
            locations='countryname',
            locationmode='country names',
            color='value',
            color_continuous_scale='Reds',
            labels={'value': color_label},
            title=f'América: {color_label}',
            scope='world',
            hover_name='countryname'
        )
        fig_americas.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            height=600,
            geo=dict(
                projection_scale=1,
                center=dict(lat=10, lon=-80),
                lataxis_range=[-55, 60],
                lonaxis_range=[-130, -30]
            )
        )
        st.plotly_chart(fig_americas, use_container_width=True)
        
    else:
        st.info("🔍 No hay datos disponibles para los filtros seleccionados.")

# -------------------------------
# PESTAÑA 4: ESTADÍSTICAS GENERALES
# -------------------------------
# -------------------------------
# PESTAÑA 4: ESTADÍSTICAS GENERALES
# -------------------------------
with tab_estadisticas:
    st.header("📊 Estadísticas Generales")
    
    # Filtros generales
    st.subheader("🔍 Filtros")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        region_filter = st.multiselect(
            "Región",
            options=df['region'].unique(),
            default=df['region'].unique(),
            key="stats_region"
        )
    
    with col_e2:
        year_range = st.slider(
            "Años",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=(int(df['year'].min()), int(df['year'].max())),
            key="stats_years"
        )
    
    with col_e3:
        event_filter = st.multiselect(
            "Tipo de Evento",
            options=df['event_type_label'].dropna().unique(),
            default=[],
            key="stats_event"
        )
    
    # Aplicar filtros
    stats_df = df[df['region'].isin(region_filter)]
    stats_df = stats_df[(stats_df['year'] >= year_range[0]) & (stats_df['year'] <= year_range[1])]
    if event_filter:
        stats_df = stats_df[stats_df['event_type_label'].isin(event_filter)]
    
    # Si no hay datos, mostrar advertencia y salir
    if stats_df.empty:
        st.warning("⚠️ No hay datos disponibles con los filtros seleccionados.")
        st.stop()
    
    # Métricas principales
    st.subheader("📈 Resumen Estadístico")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Eventos", len(stats_df))
    with col_s2:
        total_deaths = int(stats_df['ndeath'].sum()) if not stats_df['ndeath'].isna().all() else 0
        st.metric("Muertes Totales", total_deaths)
    with col_s3:
        st.metric("Países", stats_df['countryname'].nunique())
    with col_s4:
        st.metric("Años Cubiertos", stats_df['year'].nunique())
    
    # Gráfico 1: Eventos por año
    st.subheader("📅 Eventos por Año")
    events_by_year = stats_df.groupby('year').size().reset_index(name='count')
    fig_year = px.line(
        events_by_year, 
        x='year', 
        y='count', 
        title='Evolución de Eventos por Año',
        markers=True,
        line_shape='spline'
    )
    fig_year.update_traces(line=dict(width=3))
    st.plotly_chart(fig_year, use_container_width=True)
    
    # Gráfico 2: Muertes por año
    st.subheader("💀 Muertes Totales por Año")
    deaths_by_year = stats_df.groupby('year')['ndeath'].sum().reset_index()
    fig_deaths = px.area(
        deaths_by_year,
        x='year',
        y='ndeath',
        title='Evolución de Muertes por Año',
        labels={'ndeath': 'Muertes Totales', 'year': 'Año'},
        color_discrete_sequence=['#ff4b4b']
    )
    st.plotly_chart(fig_deaths, use_container_width=True)
    
    # Gráfico 3: Eventos por tipo
    st.subheader("📌 Eventos por Tipo de Conflicto")
    events_by_type = stats_df['event_type_label'].value_counts().reset_index()
    events_by_type.columns = ['Tipo de Evento', 'Cantidad']
    fig_type = px.bar(
        events_by_type, 
        x='Tipo de Evento', 
        y='Cantidad',
        title='Distribución por Tipo de Evento',
        color='Cantidad', 
        color_continuous_scale='Blues',
        text='Cantidad'
    )
    fig_type.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_type, use_container_width=True)
    
    # Gráfico 4: Top 10 Países por Tipo de Evento (SELECCIONABLE)
    st.subheader("🔝 Top 10 Países por Tipo de Evento")
    unique_event_types = stats_df['event_type_label'].dropna().unique()
    selected_event_type_for_top = st.selectbox(
        "Selecciona un tipo de evento para ver el Top 10 de países:",
        options=["Todos"] + sorted(unique_event_types),
        key="top_event_type"
    )

    if selected_event_type_for_top != "Todos":
        filtered_by_event = stats_df[stats_df['event_type_label'] == selected_event_type_for_top]
    else:
        filtered_by_event = stats_df

    top_countries_by_event = filtered_by_event['countryname'].value_counts().head(10).reset_index()
    top_countries_by_event.columns = ['País', 'Eventos']

    fig_top_event = px.bar(
        top_countries_by_event,
        x='País',
        y='Eventos',
        title=f'Top 10 Países por "{selected_event_type_for_top}"',
        color='Eventos',
        color_continuous_scale='Viridis',
        text='Eventos'
    )
    fig_top_event.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_top_event, use_container_width=True)
    
    # Gráfico 5: Top 10 países por eventos
    st.subheader("🌍 Top 10 Países por Número de Eventos")
    top_countries = stats_df['countryname'].value_counts().head(10).reset_index()
    top_countries.columns = ['País', 'Eventos']
    fig_top = px.bar(
        top_countries, 
        x='País', 
        y='Eventos',
        title='Top 10 Países con Más Eventos',
        color='Eventos', 
        color_continuous_scale='Reds',
        text='Eventos'
    )
    fig_top.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Gráfico 6: Top 10 países por muertes totales
    st.subheader("☠️ Top 10 Países por Muertes Totales")
    top_deaths_countries = stats_df.groupby('countryname')['ndeath'].sum().nlargest(10).reset_index()
    top_deaths_countries.columns = ['País', 'Muertes Totales']
    fig_top_deaths = px.bar(
        top_deaths_countries,
        x='País',
        y='Muertes Totales',
        title='Top 10 Países con Más Muertes',
        color='Muertes Totales',
        color_continuous_scale='Reds',
        text='Muertes Totales'
    )
    fig_top_deaths.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_top_deaths, use_container_width=True)
    
    # Gráfico 7: Mapa de calor de muertes por país
    st.subheader("🗺️ Mapa de Calor: Muertes Totales por País")
    deaths_by_country = stats_df.groupby('countryname')['ndeath'].sum().reset_index()
    fig_heatmap = px.choropleth(
        deaths_by_country,
        locations='countryname',
        locationmode='country names',
        color='ndeath',
        color_continuous_scale='Reds',
        labels={'ndeath': 'Muertes Totales'},
        title='Muertes Totales por País'
    )
    fig_heatmap.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Gráfico 8: Eventos por actor principal
    st.subheader("🎭 Eventos por Actor Principal")
    if 'actor1' in stats_df.columns:
        actor_counts = stats_df['actor1'].value_counts().head(10).reset_index()
        actor_counts.columns = ['Actor Principal', 'Eventos']
        fig_actor = px.pie(
            actor_counts,
            values='Eventos',
            names='Actor Principal',
            title='Distribución de Eventos por Actor Principal (Top 10)',
            hole=0.4
        )
        st.plotly_chart(fig_actor, use_container_width=True)
    else:
        st.info("La columna 'actor1' no está disponible en este dataset.")
    
    # Gráfico 9: Eventos por objetivo
    st.subheader("🎯 Eventos por Objetivo del Conflicto")
    if 'target1' in stats_df.columns:
        target_counts = stats_df['target1'].value_counts().head(10).reset_index()
        target_counts.columns = ['Objetivo', 'Eventos']
        fig_target = px.bar(
            target_counts,
            x='Objetivo',
            y='Eventos',
            title='Top 10 Objetivos de los Eventos',
            color='Eventos',
            color_continuous_scale='Purples',
            text='Eventos'
        )
        fig_target.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_target, use_container_width=True)
    else:
        st.info("La columna 'target1' no está disponible en este dataset.")
    
    # Gráfico 10: Comparativa: Eventos vs Muertes por país
    st.subheader("⚖️ Comparativa: Eventos vs Muertes por País")
    events_vs_deaths = stats_df.groupby('countryname').agg(
        total_events=('eventid', 'count'),
        total_deaths=('ndeath', 'sum')
    ).reset_index()

    fig_scatter = px.scatter(
        events_vs_deaths,
        x='total_events',
        y='total_deaths',
        text='countryname',
        title='Eventos vs Muertes por País',
        labels={'total_events': 'Número de Eventos', 'total_deaths': 'Muertes Totales'},
        size='total_events',
        color='total_deaths',
        color_continuous_scale='Reds',
        hover_name='countryname'
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(height=600)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Gráfico 11: Tendencia de eventos por tipo a lo largo del tiempo
    st.subheader("📈 Tendencia de Eventos por Tipo a lo Largo del Tiempo")
    trend_data = stats_df.groupby(['year', 'event_type_label']).size().reset_index(name='count')
    fig_trend = px.line(
        trend_data,
        x='year',
        y='count',
        color='event_type_label',
        title='Evolución de Tipos de Evento por Año',
        labels={'count': 'Número de Eventos', 'year': 'Año', 'event_type_label': 'Tipo de Evento'},
        markers=True
    )
    fig_trend.update_layout(height=600, legend_title_text='Tipo de Evento')
    st.plotly_chart(fig_trend, use_container_width=True)

# -------------------------------
# PESTAÑA 5: ANÁLISIS POR RELIGIÓN
# -------------------------------
with tab_religion:
    st.header("🕌 Análisis de Conflictos Religiosos y Étnicos")
    
    # Filtrar por temas relacionados con religión/identidad
    religion_keywords = ['religio', 'ethnic', 'étnico', 'identidad', 'discriminación', 'discrimination', 'muslim', 'cristian', 'christian', 'islam', 'hindu', 'jew', 'judío']
    religion_df = df[df['issue1_label'].str.contains('|'.join(religion_keywords), case=False, na=False) |
                     df['issue_main'].str.contains('|'.join(religion_keywords), case=False, na=False)]
    
    st.info(f"Se encontraron {len(religion_df)} eventos relacionados con religión o identidad étnica.")
    
    if len(religion_df) == 0:
        st.warning("No se encontraron eventos con temas religiosos en el dataset actual.")
    else:
        # Filtros específicos
        st.subheader("Filtros Religiosos")
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            religion_regions = st.multiselect(
                "Región",
                options=religion_df['region'].unique(),
                default=religion_df['region'].unique(),
                key="religion_region"
            )
        
        with col_r2:
            religion_years = st.slider(
                "Años",
                min_value=int(religion_df['year'].min()),
                max_value=int(religion_df['year'].max()),
                value=(int(religion_df['year'].min()), int(religion_df['year'].max())),
                key="religion_years"
            )
        
        # Aplicar filtros
        filtered_religion = religion_df[religion_df['region'].isin(religion_regions)]
        filtered_religion = filtered_religion[(filtered_religion['year'] >= religion_years[0]) & 
                                            (filtered_religion['year'] <= religion_years[1])]
        
        # Métricas
        st.subheader("Resumen")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Eventos Religiosos", len(filtered_religion))
        with col_r2:
            st.metric("Muertes Totales", int(filtered_religion['ndeath'].sum()))
        with col_r3:
            st.metric("Países Involucrados", filtered_religion['countryname'].nunique())
        
        # Gráfico 1: Eventos religiosos por año
        st.subheader("📅 Eventos Religiosos/Etnicos por Año")
        religion_by_year = filtered_religion.groupby('year').size().reset_index(name='count')
        fig_religion_year = px.bar(religion_by_year, x='year', y='count',
                                   title='Eventos Religiosos/Etnicos por Año',
                                   color='count', color_continuous_scale='Purples')
        st.plotly_chart(fig_religion_year, use_container_width=True)
        
        # Gráfico 2: Distribución por tema
        st.subheader("📌 Temas Religiosos/Etnicos")
        if 'issue1_label' in filtered_religion.columns:
            religion_topics = filtered_religion['issue1_label'].value_counts().reset_index()
            religion_topics.columns = ['Tema', 'Cantidad']
            fig_topics = px.pie(religion_topics, values='Cantidad', names='Tema',
                                title='Distribución por Tema Religioso/Étnico')
            st.plotly_chart(fig_topics, use_container_width=True)
        
        # Gráfico 3: Top países por conflictos religiosos
        st.subheader("🌍 Top Países por Conflictos Religiosos")
        top_religion_countries = filtered_religion['countryname'].value_counts().head(10).reset_index()
        top_religion_countries.columns = ['País', 'Eventos']
        fig_religion_countries = px.bar(top_religion_countries, x='País', y='Eventos',
                                        title='Top 10 Países con Más Conflictos Religiosos',
                                        color='Eventos', color_continuous_scale='Purples')
        fig_religion_countries.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_religion_countries, use_container_width=True)
        
        # Mostrar datos
        st.subheader("📋 Datos Detallados")
        st.dataframe(filtered_religion[['year', 'countryname', 'event_type_label', 'issue1_label', 'ndeath', 'actor1', 'target1']], 
                     use_container_width=True)
        
        

# -------------------------------
# PESTAÑA 6: CONCLUSIONES
# -------------------------------
with tab_conclusiones:
    st.header("✅ Conclusiones y Hallazgos")
    st.write("Esta sección será desarrollada próximamente con análisis profundos y conclusiones basadas en los datos explorados.")
    st.markdown("""
    - 📈 Tendencias generales por región y período.
    - 🎯 Actores principales y objetivos más frecuentes.
    - 🌍 Patrones geográficos de conflictos.
    - ⚖️ Relación entre tipo de evento y número de víctimas.
    """)
    st.info("¡Vuelve pronto para ver las conclusiones finales!")

# Información adicional (pie de página)
st.markdown("---")
st.caption("Dataset: Social Conflict Analysis Database (SCAD) | Periodo: 1990-2018 | Cobertura: África y América Latina")