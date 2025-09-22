import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data
def load_data():
    """
    Carga los datos del archivo CSV con caching para mejor performance
    """
    try:
        df = pd.read_csv('data/delitos_2024_clean.csv', delimiter=',')
        
        # Convertir fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'])
                # Asegurarse de que latitud y longitud sean numéricas
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
                # Eliminar filas con coordenadas inválidas
        df = df.dropna(subset=['latitud', 'longitud'])
        
        # Ordenar por fecha
        df = df.sort_values('fecha')
        
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

def filter_data(df, tipo_delito=None, comuna=None, barrio=None, fecha_inicio=None, fecha_fin=None):
    """
    Filtra el dataframe según los parámetros seleccionados
    """
    df_filtered = df.copy()
    
    if tipo_delito and tipo_delito != "Todos":
        df_filtered = df_filtered[df_filtered['tipo'] == tipo_delito]
    
    if comuna and comuna != "Todas":
        df_filtered = df_filtered[df_filtered['comuna'] == comuna]
    
    if barrio and barrio != "Todos":
        df_filtered = df_filtered[df_filtered['barrio'] == barrio]
    
    # Convertir las fechas a datetime64[ns] para comparación consistente
    if fecha_inicio:
        fecha_inicio = pd.to_datetime(fecha_inicio)
        df_filtered = df_filtered[df_filtered['fecha'] >= fecha_inicio]
    
    if fecha_fin:
        fecha_fin = pd.to_datetime(fecha_fin)
        df_filtered = df_filtered[df_filtered['fecha'] <= fecha_fin]
    
    return df_filtered



