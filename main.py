import streamlit as st
import streamlit_folium
from data_generator import (
    generate_paris_region_data,
    generate_socioeconomic_data,
    get_department_stats
)
from utils import create_choropleth_map, calculate_statistics, calculate_correlation_analysis

# Page configuration
st.set_page_config(
    page_title="MAUP - Analyse Logistique en Île-de-France",
    page_icon="🗺️",
    layout="wide"
)

# Language selector
language = st.sidebar.selectbox(
    "Langue / Language",
    ["Français", "English"]
)

# Translations
translations = {
    "Français": {
        "title": "Le Problème des Unités Spatiales Modifiables (MAUP) en Île-de-France",
        "intro": """
        Cette application démontre le Problème des Unités Spatiales Modifiables (MAUP) 
        en analysant la distribution des entrepôts logistiques en Île-de-France et 
        leur relation avec les indicateurs socio-économiques.

        Le MAUP montre comment différentes échelles d'agrégation spatiale peuvent 
        influencer l'interprétation des relations entre la présence d'entrepôts et 
        les caractéristiques socio-économiques des départements.
        """,
        "grid_size": "Taille de la Grille d'Analyse",
        "grid_help": "Ajustez le nombre de cellules (plus élevé = analyse plus fine)",
        "map_title": "Carte Interactive : Entrepôts et Analyse Spatiale",
        "stats_title": "Statistiques d'Agrégation",
        "correlation_title": "Analyse des Corrélations",
        "maup_effects": "Effets du MAUP Observés",
        "dept_analysis": "Analyse par Département",
        "grid_analysis": "Analyse par Grille"
    },
    "English": {
        "title": "The Modifiable Areal Unit Problem (MAUP) in Paris Region",
        "intro": """
        This application demonstrates the Modifiable Areal Unit Problem (MAUP) 
        by analyzing the distribution of logistics warehouses in the Paris region 
        and their relationship with socioeconomic indicators.

        MAUP shows how different scales of spatial aggregation can influence the 
        interpretation of relationships between warehouse presence and departmental 
        socioeconomic characteristics.
        """,
        "grid_size": "Analysis Grid Size",
        "grid_help": "Adjust the number of grid cells (higher = finer analysis)",
        "map_title": "Interactive Map: Warehouses and Spatial Analysis",
        "stats_title": "Aggregation Statistics",
        "correlation_title": "Correlation Analysis",
        "maup_effects": "Observed MAUP Effects",
        "dept_analysis": "Department Analysis",
        "grid_analysis": "Grid Analysis"
    }
}

# Get current language translations
t = translations[language]

# Title and introduction
st.title(t["title"])
st.markdown(t["intro"])

# Sidebar controls
st.sidebar.header(t["grid_size"])
grid_size = st.sidebar.slider(
    t["grid_size"],
    min_value=5,
    max_value=20,
    value=10,
    help=t["grid_help"]
)

# Generate data
warehouses_df = generate_paris_region_data()
socio_df = generate_socioeconomic_data()
stats_df = get_department_stats(warehouses_df, socio_df)

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Create and display map
    st.subheader(t["map_title"])
    m = create_choropleth_map(warehouses_df, stats_df, grid_size)
    streamlit_folium.st_folium(m, width=800)

with col2:
    # Display statistics
    st.subheader(t["stats_title"])

    # Calculate statistics
    stats = calculate_statistics(
        *create_grid(warehouses_df, grid_size),
        stats_df
    )

    # Display grid analysis
    st.subheader(t["grid_analysis"])
    for name, value in stats['Grid Analysis'].items():
        st.metric(name, value)

    # Display department analysis
    st.subheader(t["dept_analysis"])
    for name, value in stats['Department Analysis'].items():
        st.metric(name, value)

# Correlation analysis
st.subheader(t["correlation_title"])
correlations = calculate_correlation_analysis(stats_df)

# Create columns for correlation metrics
col1, col2, col3 = st.columns(3)
for col, (metric, value) in zip([col1, col2, col3], correlations.items()):
    col.metric(metric, f"{value:+.3f}")

# MAUP effects explanation
st.subheader(t["maup_effects"])
st.markdown("""
| Scale Level | Analytical Impact | Implications |
|------------|-------------------|--------------|
| Fine Grid | Highlights local clusters, may miss broader patterns | Better for identifying specific hotspots |
| Coarse Grid | Shows general trends, loses local detail | Useful for regional planning |
| Department | Administrative relevance, may hide internal variation | Important for policy decisions |
""")

# Add references
st.markdown("""
---
### Sources
- Openshaw, S. (1984). The modifiable areal unit problem. Geo Books, Norwich.
- INSEE - Institut National de la Statistique et des Études Économiques
- Fotheringham, A.S. & Wong, D.W.S. (1991). The modifiable areal unit problem in multivariate statistical analysis.
""")