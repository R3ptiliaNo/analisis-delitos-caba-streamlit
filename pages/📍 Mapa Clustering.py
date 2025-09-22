import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime
from utils.data_loader import load_data, filter_data
from utils.geo_utils import load_geojson
from folium.plugins import MarkerCluster
import random

# Configuración de la página
st.set_page_config(page_title="Mapa de Clusters", page_icon="📍", layout="wide")
st.title("📍 Mapa de Clusters de Delitos")

# Cargar datos
df = load_data()
geojson = load_geojson('data/caba.json')

if df is not None and geojson is not None:
    # Sidebar con filtros
    st.sidebar.header("Filtros")
    
    # Selector de tipo de delito - sin "Todos" por defecto
    tipos_delito = sorted(df['tipo'].unique().tolist())
    selected_tipo = st.sidebar.selectbox("Tipo de delito", tipos_delito, index=0)
    
    # Selector de comuna
    comunas = ["Todas"] + sorted(df['comuna'].unique().tolist())
    selected_comuna = st.sidebar.selectbox("Comuna", comunas, index=0)
    
    # Selector de rango de fechas
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    fecha_rango = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Aplicar filtros
    if len(fecha_rango) == 2:
        fecha_inicio, fecha_fin = fecha_rango
        df_filtered = filter_data(df, selected_tipo, selected_comuna, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    else:
        df_filtered = filter_data(df, selected_tipo, selected_comuna)
    
    # Mostrar resumen
    st.header("Resumen")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de delitos", df_filtered['cantidad'].sum())
    
    with col2:
        st.metric("Tipos de delitos", df_filtered['tipo'].nunique())
    
    with col3:
        st.metric("Barrios afectados", df_filtered['barrio'].nunique())
    
    with col4:
        st.metric("Comunas afectadas", df_filtered['comuna'].nunique())
    
    st.markdown("---")
    
    # Crear mapa con Folium y clustering
    st.header("Mapa de Clusters")
    
    # Verificar que tenemos coordenadas válidas
    if df_filtered[['latitud', 'longitud']].isnull().values.any():
        st.warning("Algunos registros no tienen coordenadas válidas y no se mostrarán en el mapa.")
        df_map = df_filtered.dropna(subset=['latitud', 'longitud'])
    else:
        df_map = df_filtered.copy()
    
    # Muestrear datos si hay demasiados puntos para mejorar el rendimiento
    #max_points = 2000  # Límite de puntos para mantener buen rendimiento
    #if len(df_map) > max_points:
        #st.info(f"Se muestrearon {max_points} de {len(df_map)} registros para mejorar el rendimiento del mapa.")
        #df_map = df_map.sample(n=max_points, random_state=42)
    
    # Crear mapa centrado en CABA
    m = folium.Map(location=[-34.6037, -58.3816], zoom_start=11)
    
    # Agregar capa GeoJSON con los límites de las comunas (transparente con borde azul)
    folium.GeoJson(
        geojson,
        style_function=lambda feature: {
            'fillColor': 'blue',
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.1,  # Muy transparente
            'opacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['nombre'],
            aliases=['Comuna:'],
            localize=True
        ),
        name="Límites de Comunas"
    ).add_to(m)
    
    # Agregar clustering
    marker_cluster = MarkerCluster(
        options={
            'maxClusterRadius': 50,  # Radio máximo para clustering
            'disableClusteringAtZoom': 18  # Desactivar clustering a alto zoom
        }
    ).add_to(m)
    
    # Colores por tipo de delito
    colores = {
        'Hurto': 'red',
        'Robo': 'blue',
        'Lesiones': 'green',
        'Homicidio': 'black',
        'Violencia': 'orange',
        'Otros': 'gray'
    }
    
    # Función para obtener color según tipo de delito
    def obtener_color(tipo):
        for key, color in colores.items():
            if key in tipo:
                return color
        return 'purple'  # Color por defecto
    
    # Agregar marcadores al cluster
    for idx, row in df_map.iterrows():
        # Crear popup con información
        popup_text = f"""
        <b>Tipo:</b> {row['tipo']}<br>
        <b>Barrio:</b> {row['barrio']}<br>
        <b>Comuna:</b> {row['comuna']}<br>
        <b>Fecha:</b> {row['fecha'].strftime('%Y-%m-%d')}<br>
        <b>Franja:</b> {row['franja']}<br>
        <b>Cantidad:</b> {row['cantidad']}
        """
        
        # Agregar marcador al cluster
        folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row['tipo'],
            icon=folium.Icon(color=obtener_color(row['tipo']), icon='info-sign')
        ).add_to(marker_cluster)
    
    # Agregar control de capas
    folium.LayerControl().add_to(m)
    
    # Mostrar el mapa usando st_folium
    map_data = st_folium(m, width=1000, height=600, returned_objects=[])
    
    # Gráficos (igual que en el panel descriptivo)
    st.header("Análisis Temporal")
    
    # Frecuencia por mes
    st.subheader("Frecuencia por Mes")
    df_mes = df_filtered.groupby('mes').agg({'cantidad': 'sum'}).reset_index()
    
    # Ordenar meses cronológicamente
    meses_orden = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
                  'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
    df_mes['mes'] = pd.Categorical(df_mes['mes'], categories=meses_orden, ordered=True)
    df_mes = df_mes.sort_values('mes')
    
    fig_mes = px.bar(df_mes, x='mes', y='cantidad', 
                     title=f'Delitos por Mes - {selected_tipo}')
    st.plotly_chart(fig_mes, use_container_width=True)
    
    # Frecuencia por franja horaria
    st.subheader("Frecuencia por Franja Horaria")
    df_hora = df_filtered.groupby('franja').agg({'cantidad': 'sum'}).reset_index()
    df_hora = df_hora.sort_values('franja')
    
    fig_hora = px.bar(df_hora, x='franja', y='cantidad', 
                      title=f'Delitos por Franja Horaria - {selected_tipo}')
    st.plotly_chart(fig_hora, use_container_width=True)
    
    # Frecuencia por día de la semana
    st.subheader("Frecuencia por Día de la Semana")
    dias_orden = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
    df_dia = df_filtered.groupby('dia').agg({'cantidad': 'sum'}).reset_index()
    df_dia['dia'] = pd.Categorical(df_dia['dia'], categories=dias_orden, ordered=True)
    df_dia = df_dia.sort_values('dia')
    
    fig_dia = px.bar(df_dia, x='dia', y='cantidad', 
                     title=f'Delitos por Día de la Semana - {selected_tipo}')
    st.plotly_chart(fig_dia, use_container_width=True)
    
    # Serie temporal mensual
    st.subheader("Evolución Mensual")
    df_evolucion = df_filtered.groupby(['mes']).agg({'cantidad': 'sum'}).reset_index()
    
    # Ordenar meses cronológicamente
    df_evolucion['mes'] = pd.Categorical(df_evolucion['mes'], categories=meses_orden, ordered=True)
    df_evolucion = df_evolucion.sort_values('mes')
    
    fig_evolucion = px.line(df_evolucion, x='mes', y='cantidad', 
                            title=f'Evolución Mensual de Delitos - {selected_tipo}')
    st.plotly_chart(fig_evolucion, use_container_width=True)
    
    # Análisis Geográfico
    st.header("Análisis Geográfico")
    
    # Frecuencia por comuna
    st.subheader("Frecuencia por Comuna")
    df_comuna = df_filtered.groupby('comuna').agg({'cantidad': 'sum'}).reset_index()
    df_comuna = df_comuna.sort_values('cantidad', ascending=False)
    
    fig_comuna = px.bar(df_comuna, x='comuna', y='cantidad', 
                        title=f'Delitos por Comuna - {selected_tipo}',
                        labels={'comuna': 'Comuna', 'cantidad': 'Cantidad de Delitos'})
    st.plotly_chart(fig_comuna, use_container_width=True)
    
    # Frecuencia por barrio (top 15 para mejor visualización)
    st.subheader("Frecuencia por Barrio (Top 15)")
    df_barrio = df_filtered.groupby('barrio').agg({'cantidad': 'sum'}).reset_index()
    df_barrio = df_barrio.sort_values('cantidad', ascending=False).head(15)
    
    fig_barrio = px.bar(df_barrio, x='barrio', y='cantidad', 
                        title=f'Delitos por Barrio (Top 15) - {selected_tipo}',
                        labels={'barrio': 'Barrio', 'cantidad': 'Cantidad de Delitos'})
    fig_barrio.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_barrio, use_container_width=True)
    
    # Mostrar datos crudos
    if st.checkbox("Mostrar datos crudos"):
        st.subheader("Datos Crudos")
        st.dataframe(df_filtered)
else:
    if df is None:
        st.error("No se pudieron cargar los datos de delitos. Verifica que el archivo esté en la ubicación correcta.")
    if geojson is None:
        st.error("No se pudo cargar el GeoJSON de CABA. Verifica que el archivo esté en la carpeta data/.")