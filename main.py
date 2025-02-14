import streamlit as st
import streamlit_folium
from data_generator import generate_warehouse_data
from utils import create_map, calculate_statistics

# Page configuration
st.set_page_config(
    page_title="MAUP Educational Tool",
    page_icon="🗺️",
    layout="wide"
)

# Title and introduction
st.title("Understanding the Modifiable Areal Unit Problem (MAUP)")
st.markdown("""
This interactive tool demonstrates the Modifiable Areal Unit Problem (MAUP) using warehouse locations as an example.
MAUP shows how different spatial aggregations can lead to different interpretations of the same underlying data.
""")

# Sidebar controls
st.sidebar.header("Grid Controls")
grid_size = st.sidebar.slider(
    "Grid Size",
    min_value=5,
    max_value=20,
    value=10,
    help="Adjust the number of grid cells (higher number = smaller cells)"
)

# Generate data
data = generate_warehouse_data()

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Create and display map
    st.subheader("Interactive Map")
    m = create_map(data, grid_size)
    streamlit_folium.folium_static(m)

with col2:
    # Display statistics and explanation
    st.subheader("Grid Statistics")
    grid_counts, _, _ = create_grid(data, grid_size)
    stats = calculate_statistics(grid_counts)
    
    for stat_name, value in stats.items():
        st.metric(stat_name, value)

# Educational content
st.markdown("""
### How to Use This Tool
1. Use the slider in the sidebar to adjust the grid size
2. Observe how different grid sizes affect the visualization
3. Compare the statistics as you change the grid size

### Key Observations
- **Clustering Effect**: Notice how different grid sizes can reveal or hide clusters
- **Statistical Changes**: Watch how the summary statistics change with grid size
- **Interpretation Impact**: Consider how these changes might affect decision-making

### Why This Matters
The MAUP is crucial in:
- Location planning
- Market analysis
- Resource allocation
- Population studies
""")

# Add references
st.markdown("""
---
### References
- Openshaw, S. (1984). The modifiable areal unit problem. Geo Books, Norwich.
- Fotheringham, A.S. & Wong, D.W.S. (1991). The modifiable areal unit problem in multivariate statistical analysis.
""")
