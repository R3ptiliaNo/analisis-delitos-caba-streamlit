import json
import pandas as pd
import streamlit as st

@st.cache_data
def load_geojson(file_path):
    """
    Carga el archivo GeoJSON de CABA
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        return geojson
    except Exception as e:
        st.error(f"Error al cargar el GeoJSON: {e}")
        return None

def prepare_geojson_data(geojson, df_delitos, tipo_delito=None, fecha_inicio=None, fecha_fin=None):
    """
    Prepara los datos para el mapa de coropletas uniendo el GeoJSON con los datos de delitos
    """
    from utils.data_loader import filter_data
    
    # Filtrar datos de delitos
    df_filtered = filter_data(df_delitos, tipo_delito, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    
    # Agrupar delitos por comuna
    delitos_por_comuna = df_filtered.groupby('comuna')['cantidad'].sum().reset_index()
    
    # Crear un diccionario para mapear comuna -> cantidad de delitos
    delitos_dict = dict(zip(delitos_por_comuna['comuna'], delitos_por_comuna['cantidad']))
    
    # Preparar los datos para el GeoJSON
    for feature in geojson['features']:
        # Extraer el número de comuna del nombre (ej: "Comuna 6" -> 6)
        comuna_name = feature['properties']['nombre']
        comuna_num = int(comuna_name.split(' ')[-1])
        
        # Asignar la cantidad de delitos a la propiedad
        feature['properties']['delitos'] = delitos_dict.get(comuna_num, 0)
    
    return geojson

def normalize_comuna_name(comuna_num):
    """
    Convierte el número de comuna al formato del GeoJSON
    Ej: 6 -> "Comuna 6"
    """
    return f"Comuna {comuna_num}"