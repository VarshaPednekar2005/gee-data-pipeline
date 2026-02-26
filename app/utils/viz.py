from typing import Dict, List

# paste get_visualization_params() exactly as-is

def get_visualization_params(dataset_id: str, bands: List[str]) -> Dict:
    """Generate appropriate visualization parameters for different datasets"""
    
    # Common visualization configurations
    if 'MODIS' in dataset_id:
        if 'MOD11' in dataset_id or 'MYD11' in dataset_id:  # Temperature
            return {'bands': ['LST_Day_1km'], 'min': 13000, 'max': 16000, 'palette': ['blue', 'cyan', 'yellow', 'red']}
        elif 'MOD13' in dataset_id or 'MYD13' in dataset_id:  # NDVI
            return {'bands': ['NDVI'], 'min': 0, 'max': 9000, 'palette': ['red', 'yellow', 'green']}
    
    elif 'LANDSAT' in dataset_id:
        if any(b in bands for b in ['SR_B4', 'SR_B3', 'SR_B2']):  # Landsat 8/9
            return {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 30000}
        elif any(b in bands for b in ['B4', 'B3', 'B2']):  # Landsat 5/7
            return {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 30000}
    
    elif 'COPERNICUS/S2' in dataset_id:  # Sentinel-2
        if any(b in bands for b in ['B4', 'B3', 'B2']):
            return {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
    
    elif 'SRTM' in dataset_id:  # Elevation
        return {'bands': ['elevation'], 'min': 0, 'max': 6000, 'palette': ['blue', 'green', 'yellow', 'red']}
    
    # Default: use first 3 bands or first band
    if len(bands) >= 3:
        return {'bands': bands[:3], 'min': 0, 'max': 1000}
    else:
        return {'bands': [bands[0]], 'min': 0, 'max': 1000, 'palette': ['blue', 'white', 'red']}

