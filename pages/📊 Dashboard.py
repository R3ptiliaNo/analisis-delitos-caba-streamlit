import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_data, filter_data
from utils.geo_utils import load_geojson

# Configuración de la página
st.set_page_config(page_title="Dashboard de Delitos CABA", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Análisis de Delitos - CABA 2024")

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .chart-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    .kpi-highlight {
        font-size: 1.2rem;
        font-weight: bold;
        color: #e74c3c;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos
df = load_data()

if df is not None:
    # Sidebar con filtros
    with st.sidebar:
        st.markdown("### 🔍 Filtros")
        
        # Selector de tipo de delito
        tipos_delito = sorted(df['tipo'].unique().tolist())
        selected_tipos = st.multiselect(
            "Tipos de delito", 
            tipos_delito, 
            default=tipos_delito,
            help="Selecciona uno o más tipos de delito para analizar"
        )
        
        # Selector de comuna
        comunas = sorted(df['comuna'].unique().tolist())
        selected_comunas = st.multiselect(
            "Comunas", 
            comunas, 
            default=comunas,
            help="Selecciona una o más comunas para analizar"
        )
        
        # Selector de rango de fechas
        min_date = df['fecha'].min().date()
        max_date = df['fecha'].max().date()
        
        fecha_rango = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Selecciona el rango de fechas para analizar"
        )
        
        # Botón para aplicar filtros
        aplicar_filtros = st.button("Aplicar Filtros", type="primary")
    
    # Aplicar filtros
    if len(fecha_rango) == 2:
        fecha_inicio, fecha_fin = fecha_rango
        # Filtrar datos
        df_filtered = df[
            (df['tipo'].isin(selected_tipos)) & 
            (df['comuna'].isin(selected_comunas)) &
            (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
            (df['fecha'] <= pd.to_datetime(fecha_fin))
        ]
    else:
        df_filtered = df[
            (df['tipo'].isin(selected_tipos)) & 
            (df['comuna'].isin(selected_comunas))
        ]
    
    # Cálculos para los nuevos KPIs
    # Día con más delitos
    dia_mas_delitos = df_filtered.groupby('dia')['cantidad'].sum().reset_index()
    dia_mas_delitos = dia_mas_delitos.sort_values('cantidad', ascending=False).iloc[0]
    
    # Franja horaria con más delitos
    franja_mas_delitos = df_filtered.groupby('franja')['cantidad'].sum().reset_index()
    franja_mas_delitos = franja_mas_delitos.sort_values('cantidad', ascending=False).iloc[0]
    
    # Barrio con más delitos
    barrio_mas_delitos = df_filtered.groupby('barrio')['cantidad'].sum().reset_index()
    barrio_mas_delitos = barrio_mas_delitos.sort_values('cantidad', ascending=False).iloc[0]
    
    # KPIs principales
    st.markdown("### 📈 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_delitos = df_filtered['cantidad'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total de Delitos</h3>
            <h2 style="color: #e74c3c;">{total_delitos:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Día con Más Delitos</h3>
            <h2 style="color: #3498db;">{dia_mas_delitos['dia']}</h2>
            <div class="kpi-highlight">{dia_mas_delitos['cantidad']:,} delitos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Franja Más Activa</h3>
            <h2 style="color: #2ecc71;">{franja_mas_delitos['franja']} hs</h2>
            <div class="kpi-highlight">{franja_mas_delitos['cantidad']:,} delitos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Barrio Más Afectado</h3>
            <h2 style="color: #f39c12;">{barrio_mas_delitos['barrio']}</h2>
            <div class="kpi-highlight">{barrio_mas_delitos['cantidad']:,} delitos</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Primera fila: Gráficos de distribución
    st.markdown("---")
    st.markdown("### 📊 Distribución de Delitos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por tipo de delito (reemplaza el de torta)
        st.markdown("#### Por Tipo de Delito")
        delitos_por_tipo = df_filtered.groupby('tipo')['cantidad'].sum().reset_index()
        delitos_por_tipo = delitos_por_tipo.sort_values('cantidad', ascending=False)
        
        fig_barras_tipo = px.bar(
            delitos_por_tipo, 
            x='tipo', 
            y='cantidad', 
            title='Distribución por Tipo de Delito',
            labels={'tipo': 'Tipo de Delito', 'cantidad': 'Cantidad de Delitos'},
            color='cantidad',
            color_continuous_scale='Viridis'
        )
        fig_barras_tipo.update_xaxes(tickangle=45)
        st.plotly_chart(fig_barras_tipo, use_container_width=True)
    
    with col2:
        # Gráfico de barras por comuna
        st.markdown("#### Por Comuna")
        df_comuna = df_filtered.groupby('comuna')['cantidad'].sum().reset_index()
        df_comuna = df_comuna.sort_values('cantidad', ascending=False)
        
        fig_comuna = px.bar(
            df_comuna, 
            x='comuna', 
            y='cantidad', 
            title='Delitos por Comuna',
            labels={'comuna': 'Comuna', 'cantidad': 'Cantidad de Delitos'},
            color='cantidad',
            color_continuous_scale='Plasma'
        )
        fig_comuna.update_xaxes(tickangle=45)
        st.plotly_chart(fig_comuna, use_container_width=True)
    
    # Segunda fila: Análisis temporal
    st.markdown("---")
    st.markdown("### 📅 Análisis Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de línea temporal
        st.markdown("#### Evolución Diaria")
        df_temporal = df_filtered.groupby('fecha')['cantidad'].sum().reset_index()
        df_temporal = df_temporal.sort_values('fecha')
        
        # Agregar media móvil de 7 días
        df_temporal['media_movil'] = df_temporal['cantidad'].rolling(window=7).mean()
        
        fig_temporal = px.line(
            df_temporal, 
            x='fecha', 
            y='cantidad', 
            title='Evolución Diaria de Delitos',
            labels={'fecha': 'Fecha', 'cantidad': 'Cantidad de Delitos'},
            color_discrete_sequence=['#3498db']
        )
        
        fig_temporal.add_trace(
            go.Scatter(
                x=df_temporal['fecha'], 
                y=df_temporal['media_movil'],
                mode='lines',
                name='Media Móvil (7 días)',
                line=dict(color='#e74c3c', dash='dash')
            )
        )
        
        st.plotly_chart(fig_temporal, use_container_width=True)
    
    with col2:
        # Gráfico de calor por día y hora
        st.markdown("#### Por Día y Franja Horaria")
        
        # Crear matriz de datos para el heatmap
        dias_orden = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
        df_heatmap = df_filtered.groupby(['dia', 'franja'])['cantidad'].sum().reset_index()
        
        # Convertir a formato de matriz
        heatmap_data = pd.pivot_table(
            df_heatmap, 
            values='cantidad', 
            index='dia', 
            columns='franja', 
            fill_value=0
        )
        
        # Reordenar los días
        heatmap_data = heatmap_data.reindex(dias_orden)
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Franja Horaria", y="Día de la Semana", color="Cantidad de Delitos"),
            title="Distribución por Día y Franja Horaria",
            aspect="auto",
            color_continuous_scale="YlOrRd"
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Tercera fila: Análisis detallado
    st.markdown("---")
    st.markdown("### 🔍 Análisis Detallado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 barrios
        st.markdown("#### Top 10 Barrios")
        df_barrio = df_filtered.groupby('barrio')['cantidad'].sum().reset_index()
        df_barrio = df_barrio.sort_values('cantidad', ascending=False).head(10)
        
        fig_barrio = px.bar(
            df_barrio, 
            x='barrio', 
            y='cantidad', 
            title='Top 10 Barrios con Más Delitos',
            labels={'barrio': 'Barrio', 'cantidad': 'Cantidad de Delitos'},
            color='cantidad',
            color_continuous_scale='Plasma'
        )
        fig_barrio.update_xaxes(tickangle=45)
        st.plotly_chart(fig_barrio, use_container_width=True)
    
    with col2:
        # Distribución por mes
        st.markdown("#### Por Mes")
        df_mes = df_filtered.groupby('mes')['cantidad'].sum().reset_index()
        
        # Ordenar meses cronológicamente
        meses_orden = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
                      'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
        df_mes['mes'] = pd.Categorical(df_mes['mes'], categories=meses_orden, ordered=True)
        df_mes = df_mes.sort_values('mes')
        
        fig_mes = px.bar(
            df_mes, 
            x='mes', 
            y='cantidad', 
            title='Distribución Mensual de Delitos',
            labels={'mes': 'Mes', 'cantidad': 'Cantidad de Delitos'},
            color='cantidad',
            color_continuous_scale='Rainbow'
        )
        st.plotly_chart(fig_mes, use_container_width=True)
    
    # Cuarta fila: Datos tabulares
    st.markdown("---")
    st.markdown("### 📋 Datos Detallados")
    
    # Resumen por tipo y comuna
    st.markdown("#### Resumen por Tipo y Comuna")
    resumen = df_filtered.groupby(['tipo', 'comuna'])['cantidad'].sum().reset_index()
    resumen = resumen.sort_values('cantidad', ascending=False)
    
    # Formatear la tabla
    resumen_formateado = resumen.copy()
    resumen_formateado['cantidad'] = resumen_formateado['cantidad'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        resumen_formateado.head(15),
        use_container_width=True,
        height=400
    )
    
    # Opción para descargar datos
    csv = resumen.to_csv(index=False)
    st.download_button(
        label="📥 Descargar Datos Resumidos",
        data=csv,
        file_name="resumen_delitos.csv",
        mime="text/csv"
    )
    
    # Información del dataset
    with st.expander("ℹ️ Información del Dataset"):
        st.markdown(f"""
        - **Total de registros:** {len(df_filtered):,}
        - **Período:** {df_filtered['fecha'].min().strftime('%d/%m/%Y')} - {df_filtered['fecha'].max().strftime('%d/%m/%Y')}
        - **Tipos de delito incluidos:** {', '.join(selected_tipos)}
        - **Comunas incluidas:** {', '.join(map(str, selected_comunas))}
        """)
    
else:
    st.error("No se pudieron cargar los datos de delitos. Verifica que el archivo esté en la ubicación correcta.")