import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

def generate_paris_region_data(n_points: int = 100) -> pd.DataFrame:
    """Generate mock warehouse and socioeconomic data for Paris region."""
    np.random.seed(42)

    # Paris region departments with their rough centers
    departments = {
        "75": {"name": "Paris", "center": (48.8566, 2.3522)},
        "77": {"name": "Seine-et-Marne", "center": (48.8411, 2.6377)},
        "78": {"name": "Yvelines", "center": (48.8044, 1.9722)},
        "91": {"name": "Essonne", "center": (48.6333, 2.4333)},
        "92": {"name": "Hauts-de-Seine", "center": (48.8917, 2.2500)},
        "93": {"name": "Seine-Saint-Denis", "center": (48.9167, 2.4833)},
        "94": {"name": "Val-de-Marne", "center": (48.7833, 2.4667)},
        "95": {"name": "Val-d'Oise", "center": (49.0833, 2.2500)}
    }

    # Generate warehouse locations with realistic clustering
    warehouses = []
    for dept_code, info in departments.items():
        # More warehouses in outer departments
        n_dept_points = n_points // 4 if dept_code == "75" else n_points // len(departments)

        # Add some randomness to the spread based on department size
        spread = 0.05 if dept_code == "75" else 0.1

        lats = np.random.normal(info["center"][0], spread, n_dept_points)
        lons = np.random.normal(info["center"][1], spread, n_dept_points)

        for lat, lon in zip(lats, lons):
            warehouses.append({
                'warehouse_id': f'WH{len(warehouses):03d}',
                'latitude': lat,
                'longitude': lon,
                'department': dept_code,
                'department_name': info["name"]
            })

    return pd.DataFrame(warehouses)

def generate_socioeconomic_data() -> pd.DataFrame:
    """Generate simulated socioeconomic indicators for Paris region departments."""
    np.random.seed(42)

    # Base values for Paris region
    departments = {
        "75": "Paris",
        "77": "Seine-et-Marne",
        "78": "Yvelines",
        "91": "Essonne",
        "92": "Hauts-de-Seine",
        "93": "Seine-Saint-Denis",
        "94": "Val-de-Marne",
        "95": "Val-d'Oise"
    }

    data = []
    for dept_code, name in departments.items():
        # Generate realistic but simulated data
        # Paris and western departments generally have higher socioeconomic indicators
        base_multiplier = 1.2 if dept_code in ['75', '92', '78'] else 1.0
        if dept_code == '93':  # Seine-Saint-Denis typically has lower indicators
            base_multiplier = 0.8

        data.append({
            'department': dept_code,
            'department_name': name,
            'employment_rate': min(95, max(60, np.random.normal(75, 5) * base_multiplier)),
            'median_income': int(np.random.normal(30000, 5000) * base_multiplier),
            'logistics_accessibility': min(100, max(0, np.random.normal(70, 10) * base_multiplier))
        })

    return pd.DataFrame(data)

def get_department_stats(warehouses_df: pd.DataFrame, socio_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate department-level statistics combining warehouse and socioeconomic data."""
    # Count warehouses per department
    warehouse_counts = warehouses_df['department'].value_counts().reset_index()
    warehouse_counts.columns = ['department', 'warehouse_count']

    # Merge with socioeconomic data
    stats = pd.merge(socio_df, warehouse_counts, on='department', how='left')
    stats['warehouse_count'] = stats['warehouse_count'].fillna(0)

    # Calculate warehouse density (normalized score)
    stats['warehouse_density'] = stats['warehouse_count'] / stats['warehouse_count'].max() * 100

    return stats