import numpy as np
import pandas as pd

def generate_warehouse_data(n_points=50):
    """Generate mock warehouse location data for French logistics hubs."""
    np.random.seed(42)

    # Major French logistics hubs
    centers = [
        (48.8566, 2.3522),  # Paris
        (45.7589, 4.8414),  # Lyon
        (43.2965, 5.3698),  # Marseille
        (47.2184, -1.5536), # Nantes
        (43.6047, 1.4442)   # Toulouse
    ]

    data = []
    for center in centers:
        n = n_points // len(centers)
        # Smaller spread for more realistic clustering
        lats = np.random.normal(center[0], 0.1, n)
        lons = np.random.normal(center[1], 0.1, n)
        for lat, lon in zip(lats, lons):
            data.append({
                'latitude': lat,
                'longitude': lon,
                'warehouse_id': f'WH{len(data):03d}',
                'city': get_closest_city(center)
            })

    return pd.DataFrame(data)

def get_closest_city(coordinates):
    """Return the name of the closest major city."""
    cities = {
        (48.8566, 2.3522): "Paris",
        (45.7589, 4.8414): "Lyon",
        (43.2965, 5.3698): "Marseille",
        (47.2184, -1.5536): "Nantes",
        (43.6047, 1.4442): "Toulouse"
    }
    return cities[coordinates]