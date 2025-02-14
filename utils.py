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

def get_indicator_values(stats_df: pd.DataFrame, indicator: str) -> Tuple[np.ndarray, str, str]:
    """Get values and formatting for the selected indicator."""
    indicator_configs = {
        'warehouse_density': {
            'values': stats_df['warehouse_density'],
            'format': '{:.1f}',
            'suffix': '%'
        },
        'employment_rate': {
            'values': stats_df['employment_rate'],
            'format': '{:.1f}',
            'suffix': '%'
        },
        'median_income': {
            'values': stats_df['median_income'],
            'format': '{:,.0f}',
            'suffix': '€'
        },
        'logistics_accessibility': {
            'values': stats_df['logistics_accessibility'],
            'format': '{:.1f}',
            'suffix': ''
        }
    }

    config = indicator_configs[indicator]
    return config['values'], config['format'], config['suffix']

def create_choropleth_map(warehouses_df: pd.DataFrame, 
                         stats_df: pd.DataFrame, 
                         grid_size: int,
                         selected_indicator: str) -> folium.Map:
    """Create a Folium map with warehouse points and selected indicator analysis."""
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

    # Get indicator values
    indicator_values, value_format, value_suffix = get_indicator_values(stats_df, selected_indicator)

    # Create colormap for the selected indicator
    colormap = cm.LinearColormap(
        colors=['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000'],
        vmin=indicator_values.min(),
        vmax=indicator_values.max(),
        caption=f'Selected Indicator: {selected_indicator.replace("_", " ").title()}'
    )

    # Add grid cells with colors based on indicator
    for i in range(grid_size):
        for j in range(grid_size):
            if grid_counts[i, j] > 0:
                # Calculate average indicator value for the cell
                cell_value = np.mean(indicator_values)
                bounds = [
                    [lat_edges[i], lon_edges[j]],
                    [lat_edges[i+1], lon_edges[j]],
                    [lat_edges[i+1], lon_edges[j+1]],
                    [lat_edges[i], lon_edges[j+1]]
                ]

                formatted_value = value_format.format(cell_value) + value_suffix

                folium.Polygon(
                    locations=bounds,
                    color='black',
                    weight=1,
                    fill=True,
                    fill_color=colormap(cell_value),
                    fill_opacity=0.7,
                    popup=f'Value: {formatted_value}<br>Warehouses: {int(grid_counts[i, j])}'
                ).add_to(m)

    # Add the colormap to the map
    colormap.add_to(m)

    return m

def calculate_statistics(grid_counts: np.ndarray, 
                        lat_edges: np.ndarray, 
                        stats_df: pd.DataFrame,
                        selected_indicator: str) -> Dict:
    """Calculate statistics for the current grid configuration and selected indicator."""

    # Get indicator values
    indicator_values, value_format, value_suffix = get_indicator_values(stats_df, selected_indicator)

    stats = {
        'Grid Analysis': {
            'Total Cells': len(grid_counts.flatten()),
            'Occupied Cells': np.count_nonzero(grid_counts),
            'Max Count per Cell': int(grid_counts.max()),
            'Mean Count (Occupied Cells)': round(grid_counts[grid_counts > 0].mean(), 2),
            'Density Variation (CV)': round(np.std(grid_counts) / np.mean(grid_counts[grid_counts > 0]) * 100, 2) if np.mean(grid_counts[grid_counts > 0]) > 0 else 0
        },
        'Department Analysis': {
            f'Average {selected_indicator.replace("_", " ").title()}': value_format.format(indicator_values.mean()) + value_suffix,
            f'Min {selected_indicator.replace("_", " ").title()}': value_format.format(indicator_values.min()) + value_suffix,
            f'Max {selected_indicator.replace("_", " ").title()}': value_format.format(indicator_values.max()) + value_suffix,
            'Total Warehouses': int(stats_df['warehouse_count'].sum()),
            'Coefficient of Variation': f"{round(indicator_values.std() / indicator_values.mean() * 100, 1)}%"
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