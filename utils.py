import numpy as np
import folium
from folium import plugins
import branca.colormap as cm

def create_grid(data, grid_size):
    """Create a grid overlay for the map."""
    min_lat = data['latitude'].min()
    max_lat = data['latitude'].max()
    min_lon = data['longitude'].min()
    max_lon = data['longitude'].max()
    
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

def create_map(data, grid_size):
    """Create a Folium map with warehouse locations and grid overlay."""
    # Center the map on the mean coordinates
    center_lat = data['latitude'].mean()
    center_lon = data['longitude'].mean()
    
    # Create the base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Add warehouse points
    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='blue',
            fill=True,
            popup=row['warehouse_id']
        ).add_to(m)
    
    # Create and add grid overlay
    grid_counts, lat_edges, lon_edges = create_grid(data, grid_size)
    
    # Create colormap
    colormap = cm.LinearColormap(
        colors=['white', 'yellow', 'red'],
        vmin=0,
        vmax=grid_counts.max()
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
                    fill_color=colormap(grid_counts[i, j]),
                    fill_opacity=0.5,
                    popup=f'Count: {int(grid_counts[i, j])}'
                ).add_to(m)
    
    # Add colormap to map
    colormap.add_to(m)
    
    return m

def calculate_statistics(grid_counts):
    """Calculate statistics for the current grid configuration."""
    stats = {
        'Total Cells': len(grid_counts.flatten()),
        'Occupied Cells': np.count_nonzero(grid_counts),
        'Max Count': int(grid_counts.max()),
        'Mean Count': round(grid_counts[grid_counts > 0].mean(), 2),
        'Standard Deviation': round(grid_counts[grid_counts > 0].std(), 2)
    }
    return stats
