import numpy as np
import folium
from folium import plugins
import branca.colormap as cm
import pandas as pd
from typing import Tuple, Dict, List
from scipy.ndimage import gaussian_filter

def create_grid(data: pd.DataFrame, grid_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict]:
    """Create a grid overlay for the map focused on Paris region."""
    # Paris region bounds (approximately)
    min_lat, max_lat = 48.1, 49.2
    min_lon, max_lon = 1.4, 3.5

    lat_edges = np.linspace(min_lat, max_lat, grid_size + 1)
    lon_edges = np.linspace(min_lon, max_lon, grid_size + 1)

    grid_counts = np.zeros((grid_size, grid_size))
    grid_values = {
        'employment_rate': np.zeros((grid_size, grid_size)),
        'median_income': np.zeros((grid_size, grid_size)),
        'logistics_accessibility': np.zeros((grid_size, grid_size))
    }

    # Generate unique values for each grid cell with spatial correlation
    np.random.seed(42)
    base_employment = np.random.normal(75, 10, (grid_size, grid_size))
    base_income = np.random.normal(35000, 8000, (grid_size, grid_size))
    base_logistics = np.random.normal(70, 15, (grid_size, grid_size))

    # Apply spatial smoothing
    grid_values['employment_rate'] = gaussian_filter(base_employment, sigma=1.0)
    grid_values['median_income'] = gaussian_filter(base_income, sigma=1.0)
    grid_values['logistics_accessibility'] = gaussian_filter(base_logistics, sigma=1.0)

    # Count warehouses in each grid cell
    for i in range(grid_size):
        for j in range(grid_size):
            mask = (
                (data['latitude'] >= lat_edges[i]) &
                (data['latitude'] < lat_edges[i + 1]) &
                (data['longitude'] >= lon_edges[j]) &
                (data['longitude'] < lon_edges[j + 1])
            )
            grid_counts[i, j] = mask.sum()

    return grid_counts, lat_edges, lon_edges, grid_values

def get_indicator_values(stats_df: pd.DataFrame, indicator: str, grid_values: Dict = None, grid_mode: bool = False) -> Tuple[np.ndarray, str, str]:
    """Get values and formatting for the selected indicator."""
    indicator_configs = {
        'warehouse_density': {
            'format': '{:.1f}',
            'suffix': '%'
        },
        'employment_rate': {
            'format': '{:.1f}',
            'suffix': '%'
        },
        'median_income': {
            'format': '{:,.0f}',
            'suffix': '€'
        },
        'logistics_accessibility': {
            'format': '{:.1f}',
            'suffix': ''
        }
    }

    config = indicator_configs[indicator]

    if grid_mode and grid_values and indicator in grid_values:
        values = grid_values[indicator].flatten()
        values = values[values != 0]  # Remove empty cells
    else:
        values = stats_df[indicator]

    return values, config['format'], config['suffix']

def create_choropleth_map(warehouses_df: pd.DataFrame, 
                         stats_df: pd.DataFrame, 
                         grid_size: int,
                         selected_indicator: str) -> Tuple[folium.Map, Tuple]:
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
    grid_data = create_grid(warehouses_df, grid_size)
    grid_counts, lat_edges, lon_edges, grid_values = grid_data

    # Get indicator values for grid cells
    indicator_values, value_format, value_suffix = get_indicator_values(
        stats_df, selected_indicator, grid_values, grid_mode=True
    )

    # Create colormap for the selected indicator
    colormap = cm.LinearColormap(
        colors=['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000'],
        vmin=np.nanmin(indicator_values),
        vmax=np.nanmax(indicator_values),
        caption=f'Selected Indicator: {selected_indicator.replace("_", " ").title()}'
    )

    # Add grid cells with colors based on indicator
    for i in range(grid_size):
        for j in range(grid_size):
            if grid_counts[i, j] > 0:
                cell_value = grid_values[selected_indicator][i, j] if selected_indicator in grid_values else grid_counts[i, j]

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

    return m, grid_data

def calculate_statistics(grid_counts: np.ndarray, 
                        lat_edges: np.ndarray, 
                        stats_df: pd.DataFrame,
                        selected_indicator: str,
                        grid_values: Dict) -> Dict:
    """Calculate statistics for the current grid configuration and selected indicator."""

    # Get indicator values for departments
    dept_values, value_format, value_suffix = get_indicator_values(stats_df, selected_indicator)

    # Get indicator values for grid
    grid_values_array = grid_values[selected_indicator] if selected_indicator in grid_values else grid_counts
    grid_values_flat = grid_values_array[grid_values_array != 0]

    stats = {
        'Grid Analysis': {
            f'Grid Average {selected_indicator.replace("_", " ").title()}': value_format.format(np.mean(grid_values_flat)) + value_suffix,
            f'Grid Min {selected_indicator.replace("_", " ").title()}': value_format.format(np.min(grid_values_flat)) + value_suffix,
            f'Grid Max {selected_indicator.replace("_", " ").title()}': value_format.format(np.max(grid_values_flat)) + value_suffix,
            'Grid Coefficient of Variation': f"{round(np.std(grid_values_flat) / np.mean(grid_values_flat) * 100, 1)}%",
            'Occupied Cells': np.count_nonzero(grid_counts),
            'Total Cells': len(grid_counts.flatten())
        },
        'Department Analysis': {
            f'Dept Average {selected_indicator.replace("_", " ").title()}': value_format.format(dept_values.mean()) + value_suffix,
            f'Dept Min {selected_indicator.replace("_", " ").title()}': value_format.format(dept_values.min()) + value_suffix,
            f'Dept Max {selected_indicator.replace("_", " ").title()}': value_format.format(dept_values.max()) + value_suffix,
            'Dept Coefficient of Variation': f"{round(dept_values.std() / dept_values.mean() * 100, 1)}%",
            'Total Warehouses': int(stats_df['warehouse_count'].sum())
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