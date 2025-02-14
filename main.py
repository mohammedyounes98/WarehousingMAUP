import streamlit as st
import streamlit_folium
from data_generator import generate_warehouse_data
from utils import create_map, calculate_statistics, create_grid

# Page configuration
st.set_page_config(
    page_title="MAUP - Analyse Logistique en France",
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
        "title": "Comprendre le Problème des Unités Spatiales Modifiables (MAUP)",
        "intro": """
        Cet outil interactif démontre le Problème des Unités Spatiales Modifiables (MAUP) 
        en utilisant la distribution des entrepôts en France comme exemple.
        Le MAUP montre comment différentes agrégations spatiales peuvent conduire à 
        des interprétations différentes des mêmes données sous-jacentes.
        """,
        "grid_size": "Taille de la Grille",
        "grid_help": "Ajustez le nombre de cellules (nombre plus élevé = cellules plus petites)",
        "map_title": "Carte Interactive",
        "stats_title": "Statistiques de la Grille",
        "how_to": "Comment Utiliser cet Outil",
        "observations": "Observations Clés",
        "why_matters": "Pourquoi c'est Important"
    },
    "English": {
        "title": "Understanding the Modifiable Areal Unit Problem (MAUP)",
        "intro": """
        This interactive tool demonstrates the Modifiable Areal Unit Problem (MAUP) 
        using warehouse distribution in France as an example.
        MAUP shows how different spatial aggregations can lead to different 
        interpretations of the same underlying data.
        """,
        "grid_size": "Grid Size",
        "grid_help": "Adjust the number of grid cells (higher number = smaller cells)",
        "map_title": "Interactive Map",
        "stats_title": "Grid Statistics",
        "how_to": "How to Use This Tool",
        "observations": "Key Observations",
        "why_matters": "Why This Matters"
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
data = generate_warehouse_data()

# Display city-wise distribution
city_counts = data['city'].value_counts()
st.sidebar.subheader("Distribution par Ville" if language == "Français" else "Distribution by City")
st.sidebar.dataframe(city_counts)

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Create and display map
    st.subheader(t["map_title"])
    m = create_map(data, grid_size)
    streamlit_folium.st_folium(m, width=800)

with col2:
    # Display statistics and explanation
    st.subheader(t["stats_title"])
    grid_counts, _, _ = create_grid(data, grid_size)
    stats = calculate_statistics(grid_counts)

    for stat_name, value in stats.items():
        st.metric(stat_name, value)

# Educational content
st.markdown(f"""
### {t['how_to']}
1. {t['grid_size']} ↔️
2. 🔍 {t['observations']}
3. 📊 {t['why_matters']}
""")

# Add references
st.markdown("""
---
### Sources
- Openshaw, S. (1984). The modifiable areal unit problem. Geo Books, Norwich.
- Fotheringham, A.S. & Wong, D.W.S. (1991). The modifiable areal unit problem in multivariate statistical analysis.
- INSEE - Institut National de la Statistique et des Études Économiques
""")