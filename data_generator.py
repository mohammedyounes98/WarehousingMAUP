import numpy as np
import pandas as pd

def generate_warehouse_data(n_points=50):
    """Generate mock warehouse location data."""
    # Generate random locations centered around a specific area
    np.random.seed(42)
    
    # Create cluster centers
    centers = [
        (51.5074, -0.1278),  # London center coordinates
        (51.4500, -0.1000),
        (51.5500, -0.1500)
    ]
    
    data = []
    for center in centers:
        n = n_points // len(centers)
        lats = np.random.normal(center[0], 0.02, n)
        lons = np.random.normal(center[1], 0.02, n)
        for lat, lon in zip(lats, lons):
            data.append({
                'latitude': lat,
                'longitude': lon,
                'warehouse_id': f'WH{len(data):03d}'
            })
    
    return pd.DataFrame(data)
