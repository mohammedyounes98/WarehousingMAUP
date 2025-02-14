import streamlit as st
import streamlit_folium
from data_generator import (
    generate_paris_region_data,
    generate_socioeconomic_data,
    get_department_stats
)
from utils import (
    create_choropleth_map,
    calculate_statistics,
    calculate_correlation_analysis,
    create_grid
)

# Page configuration
st.set_page_config(
    page_title="MAUP - Logistics Analysis in Paris Region",
    page_icon="🗺️",
    layout="wide"
)

# Translations
translations = {
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
        "indicator": "Select Indicator",
        "map_title": "Interactive Map: Spatial Analysis",
        "stats_title": "Aggregation Statistics",
        "correlation_title": "Correlation Analysis",
        "maup_effects": "Understanding MAUP Effects",
        "dept_analysis": "Department Analysis",
        "grid_analysis": "Grid Analysis",
        "theoretical_insights": "Theoretical Insights",
        "indicators": {
            "warehouse_density": "Warehouse Density",
            "employment_rate": "Employment Rate",
            "median_income": "Median Income",
            "logistics_accessibility": "Logistics Accessibility"
        },
        "indicator_descriptions": {
            "warehouse_density": "Number of warehouses per unit area",
            "employment_rate": "Percentage of employed working-age population",
            "median_income": "Median annual household income in euros",
            "logistics_accessibility": "Index of transportation and logistics infrastructure access"
        }
    },
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
        "indicator": "Sélectionner l'Indicateur",
        "map_title": "Carte Interactive : Analyse Spatiale",
        "stats_title": "Statistiques d'Agrégation",
        "correlation_title": "Analyse des Corrélations",
        "maup_effects": "Comprendre les Effets du MAUP",
        "dept_analysis": "Analyse par Département",
        "grid_analysis": "Analyse par Grille",
        "theoretical_insights": "Perspectives Théoriques",
        "indicators": {
            "warehouse_density": "Densité d'Entrepôts",
            "employment_rate": "Taux d'Emploi",
            "median_income": "Revenu Médian",
            "logistics_accessibility": "Accessibilité Logistique"
        },
        "indicator_descriptions": {
            "warehouse_density": "Nombre d'entrepôts par unité de surface",
            "employment_rate": "Pourcentage de la population active ayant un emploi",
            "median_income": "Revenu médian annuel des ménages en euros",
            "logistics_accessibility": "Indice d'accès aux infrastructures de transport et logistique"
        }
    }
}

# Language selector (default to English)
language = st.sidebar.selectbox(
    "Language / Langue",
    ["English", "Français"]
)

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

# Indicator selector
selected_indicator = st.sidebar.selectbox(
    t["indicator"],
    options=list(t["indicators"].keys()),
    format_func=lambda x: t["indicators"][x]
)

# Show indicator description
st.sidebar.info(t["indicator_descriptions"][selected_indicator])

# Generate data
warehouses_df = generate_paris_region_data()
socio_df = generate_socioeconomic_data()
stats_df = get_department_stats(warehouses_df, socio_df)

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Create and display map
    st.subheader(t["map_title"])
    m = create_choropleth_map(warehouses_df, stats_df, grid_size, selected_indicator)
    streamlit_folium.st_folium(m, width=800)

with col2:
    # Display statistics
    st.subheader(t["stats_title"])

    # Calculate statistics
    grid_data = create_grid(warehouses_df, grid_size)
    stats = calculate_statistics(grid_data[0], grid_data[1], stats_df, selected_indicator)

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

# Enhanced MAUP effects explanation
st.subheader(t["maup_effects"])
st.markdown("""
| Scale Level | Analytical Impact | Statistical Implications | Policy Relevance |
|------------|-------------------|------------------------|------------------|
| Fine Grid (5x5) | - High local detail<br>- Captures micro-patterns<br>- More empty cells | - Higher variance<br>- Lower spatial autocorrelation<br>- Risk of data sparsity | Best for:<br>- Local planning<br>- Site selection<br>- Micro-market analysis |
| Medium Grid (10x10) | - Balanced detail<br>- Moderate aggregation<br>- Stable patterns | - Moderate smoothing<br>- Better statistical stability<br>- Good pattern detection | Best for:<br>- Regional analysis<br>- Market optimization<br>- Transport planning |
| Coarse Grid (20x20) | - Strong smoothing<br>- Regional trends<br>- Loss of detail | - Lower variance<br>- Strong spatial autocorrelation<br>- Risk of ecological fallacy | Best for:<br>- Strategic planning<br>- Policy making<br>- Trend analysis |
| Administrative Boundaries | - Political relevance<br>- Varying sizes<br>- Historical context | - Size bias<br>- Border effects<br>- Administrative relevance | Best for:<br>- Governance<br>- Policy implementation<br>- Resource allocation |
""")

# Theoretical insights
st.subheader(t["theoretical_insights"])
st.markdown("""
### Key MAUP Components:
1. **Scale Effect**
   - Changes in results when data is aggregated into larger/smaller units
   - Affects statistical measures (mean, variance, correlation)
   - Important for policy decisions and resource allocation

2. **Zoning Effect**
   - Impact of different boundary definitions at same scale
   - Critical for administrative vs. analytical boundaries
   - Influences spatial relationship analysis

3. **Statistical Implications**
   - Correlation coefficients can change dramatically
   - Spatial autocorrelation varies with scale
   - Distribution patterns may appear/disappear

4. **Methodological Considerations**
   - Multi-scale analysis recommended
   - Sensitivity testing important
   - Need for scale-appropriate interpretations
""")

# Add references
st.markdown("""
---
### Sources & Further Reading
- Openshaw, S. (1984). The modifiable areal unit problem. Geo Books, Norwich.
- INSEE - Institut National de la Statistique et des Études Économiques
- Fotheringham, A.S. & Wong, D.W.S. (1991). The modifiable areal unit problem in multivariate statistical analysis.
- Gehlke, C.E. & Biehl, K. (1934). Certain effects of grouping upon the size of the correlation coefficient in census tract material.
- Wong, D. (2009). The modifiable areal unit problem (MAUP). The SAGE handbook of spatial analysis, 105-123.
""")