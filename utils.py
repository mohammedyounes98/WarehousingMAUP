import numpy as np
import folium
from folium import plugins
import branca.colormap as cm
import pandas as pd
from typing import Tuple, Dict, List

def create_grid(data: pd.DataFrame, grid_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a grid overlay for the map focused on Paris region."""
    # Paris region bounds (approximately)
    min_lat, max_lat = 48.1, 49.2
    min_lon, max_lon = 1.4, 3.5

    lat_edges = np.linspace(min_lat, max_lat, grid_size + 1)
    lon_edges = np.linspace(min_lon, max_lon, grid_size + 1)

    grid_counts = np.zeros((grid_size, grid_size))

    for i in range(grid_size):
        for j in range(grid_size):
            mask = (
                (data['latitude'] >= lat_edges[i]) &
                (data['latitude'] < lat_edges[i + 1]) &
                (data['longitude'] >= lon_edges[j]) &
                (data['longitude'] < lon_edges[j + 1])
            )
            grid_counts[i, j] = mask.sum()

    return grid_counts, lat_edges, lon_edges

def create_choropleth_map(warehouses_df: pd.DataFrame, 
                         stats_df: pd.DataFrame, 
                         grid_size: int) -> folium.Map:
    """Create a Folium map with both warehouse points and department-level analysis."""
    # Center on Paris region
    center_lat, center_lon = 48.8566, 2.3522

    # Create the base map
    m = folium.Map(location=[center_lat, center_lon], 
                  zoom_start=9,
                  tiles='cartodbpositron')

    # Add warehouse points
    for _, row in warehouses_df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='blue',
            fill=True,
            popup=f"Warehouse {row['warehouse_id']}<br>Dept: {row['department_name']}"
        ).add_to(m)

    # Create and add grid overlay
    grid_counts, lat_edges, lon_edges = create_grid(warehouses_df, grid_size)

    # Create colormap for grid
    grid_colormap = cm.LinearColormap(
        colors=['white', 'yellow', 'red'],
        vmin=0,
        vmax=grid_counts.max(),
        caption='Warehouse Density (Grid)'
    )

    # Add grid cells with colors based on count
    for i in range(grid_size):
        for j in range(grid_size):
            if grid_counts[i, j] > 0:
                bounds = [
                    [lat_edges[i], lon_edges[j]],
                    [lat_edges[i+1], lon_edges[j]],
                    [lat_edges[i+1], lon_edges[j+1]],
                    [lat_edges[i], lon_edges[j+1]]
                ]
                folium.Polygon(
                    locations=bounds,
                    color='black',
                    weight=1,
                    fill=True,
                    fill_color=grid_colormap(grid_counts[i, j]),
                    fill_opacity=0.3,
                    popup=f'Warehouses: {int(grid_counts[i, j])}'
                ).add_to(m)

    # Add the colormap to the map
    grid_colormap.add_to(m)

    return m

def calculate_statistics(grid_counts: np.ndarray, lat_edges: np.ndarray, stats_df: pd.DataFrame) -> Dict:
    """Calculate statistics for the current grid configuration and department data."""
    stats = {
        'Grid Analysis': {
            'Total Cells': len(grid_counts.flatten()),
            'Occupied Cells': np.count_nonzero(grid_counts),
            'Max Count per Cell': int(grid_counts.max()),
            'Mean Count (Occupied Cells)': round(grid_counts[grid_counts > 0].mean(), 2),
            'Density Variation (CV)': round(np.std(grid_counts) / np.mean(grid_counts[grid_counts > 0]) * 100, 2) if np.mean(grid_counts[grid_counts > 0]) > 0 else 0
        },
        'Department Analysis': {
            'Total Warehouses': int(stats_df['warehouse_count'].sum()),
            'Max Warehouses per Dept': int(stats_df['warehouse_count'].max()),
            'Avg Employment Rate': round(stats_df['employment_rate'].mean(), 2),
            'Median Income Range': f"{int(stats_df['median_income'].min()):,}€ - {int(stats_df['median_income'].max()):,}€",
            'Avg Logistics Access': round(stats_df['logistics_accessibility'].mean(), 2)
        }
    }
    return stats

def calculate_correlation_analysis(stats_df: pd.DataFrame) -> Dict[str, float]:
    """Calculate correlations between warehouse density and socioeconomic indicators."""
    correlations = {
        'Warehouse Density vs Employment': round(np.corrcoef(stats_df['warehouse_density'], 
                                                           stats_df['employment_rate'])[0,1], 3),
        'Warehouse Density vs Income': round(np.corrcoef(stats_df['warehouse_density'], 
                                                       stats_df['median_income'])[0,1], 3),
        'Warehouse Density vs Logistics Access': round(np.corrcoef(stats_df['warehouse_density'], 
                                                                 stats_df['logistics_accessibility'])[0,1], 3)
    }
    return correlations