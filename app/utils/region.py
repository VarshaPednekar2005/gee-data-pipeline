import json
import ee
from app.config import CITY_BUFFER_METERS

# city_coords dict stays exactly as is
# get_region_geometry() function stays exactly as is
# only change: point.buffer(20000) → point.buffer(CITY_BUFFER_METERS)


def get_region_geometry(region_type, region_data):
    """
    Enhanced region handler supporting multiple input types
    
    Args:
        region_type: 'country', 'state', 'city', 'continent', 'geojson', 'coordinates', 'draw'
        region_data: Either region name (str) or geometry dict for custom regions
    """
    try:
        if region_type == "country":
            return ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(
                ee.Filter.eq('country_na', region_data)
            ).geometry()
            
        elif region_type == "state":
            return ee.FeatureCollection("FAO/GAUL/2015/level1").filter(
                ee.Filter.eq('ADM1_NAME', region_data)
            ).geometry()
            
        elif region_type == "city":
            # Use a buffer around city center (approximate 20km radius)
            # For major cities, use known coordinates
            city_coords = {
                "Mumbai": [72.8777, 19.0760],
                "Delhi": [77.1025, 28.7041],
                "Bangalore": [77.5946, 12.9716],
                "Hyderabad": [78.4867, 17.3850],
                "Chennai": [80.2707, 13.0827],
                "Kolkata": [88.3639, 22.5726],
                "Pune": [73.8567, 18.5204],
                "Ahmedabad": [72.5714, 23.0225],
                "Surat": [72.8311, 21.1702],
                "Jaipur": [75.7873, 26.9124],
                "Lucknow": [80.9462, 26.8467],
                "Kanpur": [80.3319, 26.4499],
                "Nagpur": [79.0882, 21.1458],
                "Indore": [75.8577, 22.7196],
                "Bhopal": [77.4126, 23.2599],
                "Visakhapatnam": [83.2185, 17.6868],
                "Patna": [85.1376, 25.5941],
                "Vadodara": [73.1812, 22.3072],
                "Ludhiana": [75.8573, 30.9010],
                "Agra": [78.0081, 27.1767],
                "New York": [-74.0060, 40.7128],
                "Los Angeles": [-118.2437, 34.0522],
                "Chicago": [-87.6298, 41.8781],
                "Houston": [-95.3698, 29.7604],
                "Phoenix": [-112.0740, 33.4484],
                "Philadelphia": [-75.1652, 39.9526],
                "San Antonio": [-98.4936, 29.4241],
                "San Diego": [-117.1611, 32.7157],
                "Dallas": [-96.7970, 32.7767],
                "San Jose": [-121.8863, 37.3382]
            }
            
            if region_data in city_coords:
                lon, lat = city_coords[region_data]
                # Create 20km buffer around city center
                point = ee.Geometry.Point([lon, lat])
                return point.buffer(CITY_BUFFER_METERS)  # 20km radius
            else:
                return None
            
        elif region_type == "continent":
            continent_countries = {
                "Asia": ["China", "India", "Indonesia", "Pakistan", "Bangladesh", "Japan", "Philippines", "Vietnam", "Turkey", "Iran"],
                # ... other continents ...
            }
            if region_data in continent_countries:
                return ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(
                    ee.Filter.inList('country_na', continent_countries[region_data])
                ).geometry()
                
        elif region_type in ["geojson", "coordinates", "draw"]:
            # Handle custom GeoJSON geometry
            if isinstance(region_data, dict):
                # Check if it's a FeatureCollection
                if region_data.get('type') == 'FeatureCollection':
                    print(f"DEBUG: FeatureCollection with {len(region_data['features'])} features")
                    features = [ee.Feature(ee.Geometry(f['geometry'])) for f in region_data['features']]
                    result = ee.FeatureCollection(features).geometry()
                    print("DEBUG: Successfully converted FeatureCollection")
                    return result
                else:
                    print(f"DEBUG: Single geometry type: {region_data.get('type')}")
                    return ee.Geometry(region_data)
            else:
                # Try to parse as JSON string
                import json
                print("DEBUG: Parsing JSON string")
                geometry_dict = json.loads(region_data)
                if geometry_dict.get('type') == 'FeatureCollection':
                    print(f"DEBUG: FeatureCollection from string with {len(geometry_dict['features'])} features")
                    features = [ee.Feature(ee.Geometry(f['geometry'])) for f in geometry_dict['features']]
                    return ee.FeatureCollection(features).geometry()
                return ee.Geometry(geometry_dict)
        
        return None
        
    except Exception as e:
        print(f"Region error: {e}")
        return None
