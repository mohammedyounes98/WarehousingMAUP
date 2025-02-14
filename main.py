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
        by analyzing the distribution of virtual logistics warehouses in the Paris region 
        and their relationship with socioeconomic indicators.

        MAUP shows how different scales of spatial aggregation can influence the 
        interpretation of relationships between warehouse presence and departmental 
        socioeconomic characteristics.
        """,
        "grid_size": "Analysis Grid Size",
        "grid_help": "Adjust the number of grid cells (higher = finer analysis)",
        "indicator": "Select Indicator",
        "map_title": "Interactive Map: Spatial Analysis",
        "stats_title": "Comparative Statistics",
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
    }
}

# Set English as default language
language = "English"
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
    m, grid_data = create_choropleth_map(warehouses_df, stats_df, grid_size, selected_indicator)
    streamlit_folium.st_folium(m, width=800)

with col2:
    # Display statistics
    st.subheader(t["stats_title"])

    # Calculate and display statistics
    stats = calculate_statistics(
        grid_data[0],  # grid_counts
        grid_data[1],  # lat_edges
        stats_df,
        selected_indicator,
        grid_data[3]   # grid_values
    )

    # Create two columns for grid and department analysis
    grid_col, dept_col = st.columns(2)

    with grid_col:
        st.subheader(t["grid_analysis"])
        for name, value in stats['Grid Analysis'].items():
            st.metric(name, value)

    with dept_col:
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
st.markdown("""
## Understanding MAUP Effects

The Modifiable Areal Unit Problem demonstrates how different spatial aggregation levels affect analysis outcomes:
""")

st.markdown("""
| Scale Level | Analytical Impact | Statistical Implications | Policy Relevance |
|------------|-------------------|------------------------|------------------|
| Fine Grid (5x5) | High local detail, captures micro-patterns | Higher variance, risk of data sparsity | Best for local planning and site selection |
| Medium Grid (10x10) | Balanced detail, stable patterns | Moderate smoothing, good pattern detection | Ideal for regional analysis |
| Coarse Grid (20x20) | Strong smoothing, shows trends | Lower variance, risk of oversimplification | Suitable for strategic planning |
| Administrative | Political boundaries, varying sizes | Size bias, border effects | Critical for governance |
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



## Adding the credit and the GitHub repo to the side bar
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Developed by:**  
**Mohammed Younes**  
[LVMT - Gustave Eiffel University](https://www.lvmt.fr/)
""")

github_url = "https://github.com/mohammedyounes98/WarehousingMAUP"
st.sidebar.markdown(f"""
<a href="{github_url}" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-Repo-black?style=for-the-badge&logo=github" width="180">
</a>
""", unsafe_allow_html=True)
