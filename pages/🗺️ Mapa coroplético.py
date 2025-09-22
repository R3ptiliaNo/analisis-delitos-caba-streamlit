import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_data, filter_data
from utils.geo_utils import load_geojson, prepare_geojson_data

# Configuración de la página
st.set_page_config(page_title="Análisis Espacial", page_icon="🗺️")
st.title("🗺️ Análisis coroplético de Delitos")

# Cargar datos
df = load_data()
geojson = load_geojson('data/caba.json')

if df is not None and geojson is not None:
    # Sidebar con filtros
    st.sidebar.header("Filtros")
    
    # Selector de tipo de delito
    tipos_delito = ["Todos"] + sorted(df['tipo'].unique().tolist())
    selected_tipo = st.sidebar.selectbox("Tipo de delito", tipos_delito)
    
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
        # Convertir a datetime para la comparación
        fecha_inicio = pd.to_datetime(fecha_inicio)
        fecha_fin = pd.to_datetime(fecha_fin)
        geojson_data = prepare_geojson_data(geojson, df, selected_tipo, fecha_inicio, fecha_fin)
        df_filtered = filter_data(df, selected_tipo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    else:
        geojson_data = prepare_geojson_data(geojson, df, selected_tipo)
        df_filtered = filter_data(df, selected_tipo)
    
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
    
    # Crear mapa de coropletas
    st.header("Mapa coroplético por Comunas")
    
    # Preparar datos para el gráfico
    delitos_por_comuna = []
    for feature in geojson_data['features']:
        comuna_name = feature['properties']['nombre']
        delitos_count = feature['properties']['delitos']
        delitos_por_comuna.append({
            'Comuna': comuna_name,
            'Delitos': delitos_count
        })
    
    df_delitos_comuna = pd.DataFrame(delitos_por_comuna)
    
    # Crear el mapa de coropletas
    fig = px.choropleth_mapbox(
        df_delitos_comuna,
        geojson=geojson_data,
        locations='Comuna',
        featureidkey="properties.nombre",
        color='Delitos',
        color_continuous_scale="reds",
        range_color=(0, max(1, df_delitos_comuna['Delitos'].max())),  # Evitar rango 0-0
        mapbox_style="carto-positron",
        zoom=10,
        center={"lat": -34.6037, "lon": -58.3816},
        opacity=0.7,
        labels={'Delitos': 'Cantidad de Delitos'},
        title=f'Distribución de {selected_tipo if selected_tipo != "Todos" else "todos los delitos"} por Comuna'
    )
    
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla con datos por comuna
    st.subheader("Datos por Comuna")
    df_delitos_comuna = df_delitos_comuna.sort_values('Delitos', ascending=False)
    st.dataframe(df_delitos_comuna)
    
    # Gráfico de barras por comuna
    st.subheader("Distribución por Comuna")
    fig_barras = px.bar(
        df_delitos_comuna, 
        x='Comuna', 
        y='Delitos',
        title=f'Delitos por Comuna - {selected_tipo if selected_tipo != "Todos" else "Todos los tipos"}'
    )
    fig_barras.update_xaxes(tickangle=45)
    st.plotly_chart(fig_barras, use_container_width=True)
    
    # Nueva sección: Análisis Temporal (igual que en el panel descriptivo)
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
    
    # Nueva sección: Análisis Geográfico Detallado
    st.header("Análisis Geográfico Detallado")
    
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