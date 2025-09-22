# portada.py  (o incluir al inicio de app.py)
import streamlit as st
import pandas as pd
# Links a las fuentes
LINK_DELITOS = "https://data.buenosaires.gob.ar/dataset/delitos"
LINK_COMUNAS = "https://data.buenosaires.gob.ar/dataset/comunas"

st.set_page_config(
    page_title="Dashboard Delitos CABA 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header principal
st.title("📊 Dashboard de Análisis de Delitos — Ciudad de Buenos Aires (2024)")
st.markdown("---")

# Introducción ampliada
st.markdown(
    """
Este **dashboard interactivo** presenta el análisis de los delitos registrados en la Ciudad Autónoma de Buenos Aires durante 2024.
Su objetivo es transformar datos abiertos en información **acciónable** para la toma de decisiones públicas, políticas y de seguridad.

Los datos provienen de fuentes oficiales de la Ciudad de Buenos Aires (enlaces abajo). Esta herramienta permite explorar patrones
temporales y espaciales, comparar periodos, identificar focos críticos y descargar los subconjuntos de datos filtrados para análisis posteriores.
"""
)

# Fuentes y metadatos (visibles y con links)
with st.expander("ℹ️ - Fuentes, cobertura y metadatos", expanded=True):
    st.markdown(f"""
- **Dataset Delitos (oficial)**: [Repositorio de delitos — GCBA]({LINK_DELITOS})  
- **Dataset Comunas / Geometría**: [Comunas (geojson / shapefile)]({LINK_COMUNAS})

**Cobertura temporal:** Enero - Diciembre 2024 (según el dataset original).  
**Campos clave:** tipo de delito, fecha y hora, barrio, comuna, franja horaria, latitud, longitud.  

""")

# Qué muestra el dashboard (valor agregado)
st.header("¿Qué muestra este dashboard y por qué es útil?")
st.markdown(
    """
Este dashboard está organizado para facilitar la **toma de decisiones** en áreas como prevención, despliegue policial,
políticas públicas de seguridad, asignación presupuestaria y evaluación de impacto. Entre las funcionalidades principales se incluyen:

- **KPIs rápidos**
- **Análisis espacial**:
  - Mapa de calor para detectar micro-hotspots.
  - Mapa coroplético.
  - clusterización para identificar focos de concentración.
- **Filtros dinámicos**: por tipo de delito, comuna, rango de fechas.
- **Exportación**: descargar el subconjunto filtrado en CSV para análisis offline o presentaciones.


"""
)





# Sección de 'Qué se puede hacer' para equipos técnicos y políticos
with st.expander("🔎 - Qué se puede hacer (sugerencias para tomadores de decisión)", expanded=False):
    st.markdown(
        """
- **Policía / Operaciones**: focalizar patrullaje y presencia en micro-hotspots detectados en horarios críticos.
- **Gobierno local**: priorizar mejoras de iluminación, limpieza y visibilidad urbana en áreas con alta incidencia.
- **Planificación social**: coordinar intervenciones sociales y de prevención (programas comunitarios) en barrios con picos sostenidos.

"""
    )

# Pie con enlaces y contacto
st.markdown("---")
st.markdown(
    f"**Fuentes:** [Delitos — GCBA]({LINK_DELITOS}) | [Comunas — GCBA]({LINK_COMUNAS})  \n"
    "Autor: Alan Aramayo"
)

# Nota: en otras secciones del app.py se debe implementar:
# - la carga desde la DB (load_data)
# - los filtros (tipo, comuna, barrio, fechas)
# - las visualizaciones (KPIs, series, mapas)
# - el botón de descarga: st.download_button para df_filtered.to_csv(index=False)
#
# Este bloque sólo crea la portada, descripción y la guía de uso del dashboard.
