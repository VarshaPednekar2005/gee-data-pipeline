from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import ee
from typing import Dict, Optional, List, Tuple
import tempfile
import base64
import rasterio
import rasterio.mask
import requests
from shapely.geometry import shape
import os
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

def exact_clip_region(image, region, scale):
    """Exact clipping preserving data values and GEE band metadata"""
    region_geom = region.getInfo()
    
    # Get original GEE band information to preserve metadata
    band_info = image.getInfo()['bands']
    band_names = [band['id'] for band in band_info]
    
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # First get basic clipped image from GEE
        clipped_image = image.clip(region)
        url = clipped_image.getDownloadURL({
            'scale': scale,
            'region': region_geom,
            'format': 'GEO_TIFF'
        })
        
        response = requests.get(url)
        with open(tmp_path, 'wb') as f:
            f.write(response.content)
        
        # Apply exact clipping with rasterio
        with rasterio.open(tmp_path) as src:
            geom = shape(region_geom)
            clipped_data, clipped_transform = rasterio.mask.mask(
                src, [geom], crop=True, filled=True, nodata=src.nodata
            )
            
            clipped_meta = src.meta.copy()
            clipped_meta.update({
                'height': clipped_data.shape[1],
                'width': clipped_data.shape[2],
                'transform': clipped_transform,
                'nodata': src.nodata,
                'compress': 'lzw',  # Add compression like GEE exports
                'tiled': True       # Optimize for GIS software
            })
            
            # Preserve original GEE band names in metadata
            if len(band_names) == clipped_data.shape[0]:
                clipped_meta['descriptions'] = band_names
            
            return clipped_data, clipped_meta
            
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# ==================== UNIVERSAL DATASET HANDLER ====================

class UniversalGEEHandler:
    """Handles ANY Google Earth Engine dataset with auto-detection"""
    
    # Known revisit intervals from official documentation
    KNOWN_REVISIT_INTERVALS = {
        'COPERNICUS/S2': 5,  # Sentinel-2 (per satellite, 5 days)
        'COPERNICUS/S1': 6,  # Sentinel-1
        'LANDSAT/LC08': 16,  # Landsat 8
        'LANDSAT/LC09': 16,  # Landsat 9
        'LANDSAT/LE07': 16,  # Landsat 7
        'LANDSAT/LT05': 16,  # Landsat 5
        'MODIS/006/MOD': 1,  # MODIS Terra (daily)
        'MODIS/006/MYD': 1,  # MODIS Aqua (daily)
        'MODIS/061/MOD': 1,  # MODIS Terra (daily)
        'MODIS/061/MYD': 1,  # MODIS Aqua (daily)
    }
    
    def get_revisit_interval(self, dataset_id: str) -> Dict:
        """Get revisit interval from known database"""
        # Check known intervals
        for key, days in self.KNOWN_REVISIT_INTERVALS.items():
            if key in dataset_id:
                print(f"Found known revisit interval: {days} days for {dataset_id}")
                return {"interval_days": days, "interval_hours": None}
        
        print(f"No known revisit interval for {dataset_id}")
        return {"interval_days": None, "interval_hours": None}
    
    def detect_dataset_type(self, dataset_id: str) -> Dict:
        """
        AUTO-DETECTION: Works for ANY dataset with comprehensive metadata
        """
        
        # Try ImageCollection first (most common)
        try:
            collection = ee.ImageCollection(dataset_id)
            first_image = collection.limit(1).first()
            
            info = first_image.getInfo()
            bands = info['bands']
            properties = info.get('properties', {})
            
            band_names = [b['id'] for b in bands]
            has_time = 'system:time_start' in properties
            
            # Get scale using proper method - nominalScale() not crs_transform
            try:
                proj = first_image.select(band_names[0]).projection()
                scale = proj.nominalScale().getInfo()
                if scale == 0 or scale > 200000:  # Fallback for invalid scales
                    scale = 1000
            except:
                scale = 1000
            
            # Get comprehensive band information with correct scale
            band_details = []
            for band in bands:
                band_details.append({
                    'name': band['id'],
                    'data_type': band.get('data_type', {}).get('type', 'Unknown'),
                    'scale': f"{scale}m",  # Use the main detected scale for all bands
                    'crs': band.get('crs', 'Unknown'),
                    'dimensions': band.get('dimensions', 'Unknown')
                })
            
            # Skip slow metadata queries for large collections
            description = 'Auto-detected ImageCollection'
            dataset_type_info = 'ImageCollection'
            date_range = "Available (dates vary by region)" if has_time else None
            
            print(f"✓ Auto-detected ImageCollection: {dataset_id}")
            print(f"  - Bands: {band_names[:3]}{'...' if len(band_names) > 3 else ''}")
            print(f"  - Has dates: {has_time}")
            print(f"  - Scale: {scale}m")
            
            return {
                "type": "ImageCollection",
                "requires_date": has_time,
                "bands": band_names,
                "band_details": band_details,
                "scale": abs(scale),
                "description": description,
                "date_range": date_range,
                "dataset_type_info": dataset_type_info
            }
            
        except Exception as e1:
            # Try as single Image
            try:
                image = ee.Image(dataset_id)
                info = image.getInfo()
                bands = info['bands']
                properties = info.get('properties', {})
                band_names = [b['id'] for b in bands]
                
                # Get comprehensive band information with correct scale
                band_details = []
                for band in bands:
                    band_details.append({
                        'name': band['id'],
                        'data_type': band.get('data_type', {}).get('type', 'Unknown'),
                        'scale': f"{scale}m",  # Use the main detected scale for all bands
                        'crs': band.get('crs', 'Unknown'),
                        'dimensions': band.get('dimensions', 'Unknown')
                    })
                
                try:
                    proj = image.select(band_names[0]).projection()
                    scale = proj.nominalScale().getInfo()
                except:
                    scale = 1000
                
                # Get image description
                description = info.get('description', 'Single satellite image')
                
                # Check if image has date
                image_date = None
                if 'system:time_start' in properties:
                    try:
                        image_date = ee.Date(properties['system:time_start']).format('YYYY-MM-dd').getInfo()
                    except:
                        image_date = "Date available"
                
                print(f"✓ Auto-detected Image: {dataset_id}")
                print(f"  - Bands: {band_names}")
                
                return {
                    "type": "Image",
                    "requires_date": False,
                    "bands": band_names,
                    "band_details": band_details,
                    "scale": abs(scale),
                    "description": description,
                    "image_date": image_date,
                    "dataset_type_info": "Single Image"
                }
                
            except Exception as e2:
                raise ValueError(f"Cannot access dataset {dataset_id}. ImageCollection error: {str(e1)[:100]}. Image error: {str(e2)[:100]}")
    
    def get_smart_composite_method(self, dataset_id: str, bands: List[str]) -> str:
        """Choose appropriate composite method based on dataset type"""
        
        # Temperature data - use mean for average conditions
        if any(temp in dataset_id.upper() for temp in ['TEMPERATURE', 'TEMP', 'LST', 'MOD11', 'MYD11', 'CFSV2']):
            return 'mean'
        
        # Precipitation data - use sum for total rainfall
        if any(precip in dataset_id.upper() for precip in ['PRECIPITATION', 'PRECIP', 'RAINFALL', 'CHIRPS', 'TRMM']):
            return 'sum'
        
        # Land cover/classification - use mode for most common class
        if any(lc in dataset_id.upper() for lc in ['LANDCOVER', 'LAND_COVER', 'CLASSIFICATION', 'ESA', 'MODIS_LC']):
            return 'mode'
        
        # NDVI and vegetation indices - use median to reduce noise
        if any(vi in dataset_id.upper() for vi in ['NDVI', 'EVI', 'MOD13', 'MYD13']):
            return 'median'
        
        # Optical imagery (Landsat, Sentinel) - use median to remove clouds
        if any(optical in dataset_id.upper() for optical in ['LANDSAT', 'SENTINEL', 'COPERNICUS/S2']):
            return 'median'
        
        # Default: median (safest for most datasets)
        return 'median'
    def get_config(self, dataset_id: str, user_overrides: Optional[Dict] = None) -> Dict:
        """
        Get configuration using AUTO-DETECTION only
        """
        
        config = {}
        is_curated = False
        print(f"⚡ Auto-detecting dataset: {dataset_id}")
        
        # Auto-detect characteristics
        detected = self.detect_dataset_type(dataset_id)
        
        # Get smart composite method
        composite_method = self.get_smart_composite_method(dataset_id, detected["bands"]) if detected["type"] == "ImageCollection" else None
        
        # Build final config with auto-detected values
        final_config = {
            "dataset_id": dataset_id,
            "name": dataset_id.split('/')[-1],  # Simple name from ID
            "type": detected["type"],
            "requires_date": detected["requires_date"],
            "bands": detected["bands"],
            "scale": detected["scale"],
            "composite_method": composite_method,
            "is_curated": is_curated,
        }
        
        # Apply user overrides (highest priority)
        if user_overrides:
            final_config.update({k: v for k, v in user_overrides.items() if v is not None})
        
        return final_config
    
    def process_dataset(self, dataset_id: str, start_date: Optional[str], end_date: Optional[str], 
                       region: ee.Geometry, config: Dict) -> Tuple[Optional[ee.Image], int]:
        """Process any dataset based on configuration"""
        
        if config['type'] == 'Image':
            # Single image - no dates needed
            image = ee.Image(dataset_id)
            if region:
                image = image.clip(region)
            
            if config.get('preprocessing'):
                image = config['preprocessing'](image)
            
            return image, 1
        
        elif config['type'] == 'ImageCollection':
            # Image collection
            collection = ee.ImageCollection(dataset_id)
            
            # Date filtering (only if dataset has dates AND user provided dates)
            if config['requires_date']:
                if start_date and end_date:
                    # Validate date range
                    try:
                        from datetime import datetime
                        start = datetime.strptime(start_date, '%Y-%m-%d')
                        end = datetime.strptime(end_date, '%Y-%m-%d')
                        if start >= end:
                            raise ValueError("Start date must be before end date")
                    except ValueError as e:
                        raise ValueError(f"Invalid date range: {str(e)}")
                    
                    collection = collection.filterDate(start_date, end_date)
                else:
                    # No dates provided for temporal dataset - use last 30 days as default
                    collection = collection.filterDate(
                        ee.Date(ee.Date.now()).advance(-30, 'day'),
                        ee.Date.now()
                    )
            
            # Region filtering
            if region:
                collection = collection.filterBounds(region)
            
            # Cloud filtering (if curated config has it)
            if config.get('cloud_filter'):
                try:
                    collection = config['cloud_filter'](collection)
                except:
                    pass  # Skip if cloud filter fails
            
            # Check count (optimized for large collections)
            try:
                # For large datasets, limit count check to avoid timeout
                count = collection.limit(1000).size().getInfo()
                if count == 1000:
                    # Collection has 1000+ images, use approximate count
                    count = f"1000+"
            except Exception as e:
                raise ValueError(f"Failed to get image count. The collection might be empty or have invalid date range. Error: {str(e)}")
            
            if count == 0:
                return None, 0
            
            # Preprocessing (if curated config has it)
            if config.get('preprocessing'):
                try:
                    collection = collection.map(config['preprocessing'])
                except:
                    pass  # Skip if preprocessing fails
            
            # Composite based on method
            method = config['composite_method']
            if method == 'median':
                image = collection.median()
            elif method == 'mean':
                image = collection.mean()
            elif method == 'sum':
                image = collection.sum()
            elif method == 'mode':
                image = collection.mode()
            elif method == 'first':
                image = collection.first()
            else:
                image = collection.median()  # Safe default
            
            if region:
                image = image.clip(region)
            
            return image, count
        
        raise ValueError(f"Unknown type: {config['type']}")

# Initialize handler globally
handler = UniversalGEEHandler()

# ==================== FASTAPI SETUP ====================

_gee_initialised = False

def init_gee() -> bool:
    """Initialize GEE once per process using OAuth credentials."""
    global _gee_initialised
    if _gee_initialised:
        return True
    try:
        ee.Initialize(project='plucky-sight-423703-k5')
        print("✅ GEE initialized with OAuth")
        _gee_initialised = True
        return True
    except Exception as e:
        print(f"❌ GEE initialization failed: {e}")
        print("   Run: earthengine authenticate")
        return False

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
                return point.buffer(20000)  # 20km radius
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
                # region_data is a GeoJSON geometry object
                return ee.Geometry(region_data)
            else:
                # Try to parse as JSON string
                import json
                geometry_dict = json.loads(region_data)
                return ee.Geometry(geometry_dict)
        
        return None
        
    except Exception as e:
        print(f"Region error: {e}")
        return None

@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "app" / "static" / "index.html")

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


@app.post("/preview")
async def preview_download(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        dataset_id = request['dataset']
        config = handler.get_config(dataset_id=dataset_id)
        
        # Get region - handle both old and new formats
        region_type = request['region_type']
        
        if region_type in ['geojson', 'coordinates', 'draw']:
            # Custom geometry
            region_data = request.get('custom_geometry')
            if not region_data:
                return {"success": False, "error": "Custom geometry required"}
        else:
            # Predefined region
            region_data = request['region_name']
        
        region = get_region_geometry(region_type, region_data)
        if not region:
            return {"success": False, "error": "Invalid region"}
        
        # Process dataset using universal handler
        image, count = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=request.get('start_date'),
            end_date=request.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {
                "success": False,
                "error": f"No images found for {dataset_id}. Try different date range or region."
            }
        
        # Get comprehensive dataset information
        detected_info = handler.detect_dataset_type(dataset_id)
        
        # Calculate area and file size with compression factor
        area_km2 = region.area().divide(1000000).getInfo()
        scale = config['scale']
        pixels_per_km2 = 1000000 / (scale * scale)
        estimated_pixels = area_km2 * pixels_per_km2 * len(config['bands'])
        
        # Account for GeoTIFF LZW compression (typically 3-5x compression)
        # Use conservative 3x compression factor for estimation
        uncompressed_mb = (estimated_pixels * 4) / (1024 * 1024)
        estimated_mb = uncompressed_mb / 3  # Apply compression factor
        
        # Size validation and warnings
        size_warning = None
        size_str = f"{estimated_mb:.1f} MB"
        
        # Use lower threshold (5MB) to be more conservative
        # This accounts for compression variability

        if estimated_mb > 1024:
            size_str = f"{estimated_mb/1024:.1f} GB"
            
        # Use 5MB threshold instead of 10MB to be more conservative
        # Accounts for compression variability (actual size may be 2-5x estimated)
        if estimated_mb > 5:  # Changed from 10
            size_warning = {
                "type": "size_limit",
                "message": f"File size (~{size_str}, may vary) requires Google Drive export",
                "suggestions": [
                    "File will be exported to Google Drive automatically",
                    "Actual size depends on data compression",
                    "Check your Drive after 5-30 minutes",
                    "💡 Tip: Use 'City' region for faster Sentinel-2 exports (2-5 min vs 30-60 min)"
                ]
            }
        elif estimated_mb > 3:  # Warning for medium files
            size_warning = {
                "type": "size_caution", 
                "message": f"Medium file size (~{size_str}) - actual size may vary",
                "suggestions": [
                    "Download should complete in a few minutes",
                    "💡 Tip: Use 'City' region for faster exports"
                ]
            }

        # Generate sample visualization
        sample_image_url = None
        try:
            # Create appropriate visualization for the dataset
            vis_params = get_visualization_params(dataset_id, config['bands'])
            if vis_params:
                # Get a small sample region for visualization
                sample_region = region.centroid().buffer(10000)  # 10km around center
                sample_image = image.clip(sample_region)
                
                # Generate map tiles
                map_id = sample_image.getMapId(vis_params)
                sample_image_url = map_id['tile_fetcher'].url_format
        except Exception as e:
            print(f"Could not generate sample image: {e}")
        
        # Prepare comprehensive response
        response_data = {
            "success": True,
            "dataset_name": config['name'],
            "dataset_id": dataset_id,
            "dataset_type": config['type'],
            "description": detected_info.get('description', 'No description available'),
            "image_count": count,
            "bands": config['bands'],
            "band_details": detected_info.get('band_details', []),
            "native_resolution": f"{config['scale']}m",
            "export_resolution": f"{config['scale']}m",
            "estimated_size": size_str,
            "estimated_mb": estimated_mb,
            "size_warning": size_warning,
            "area_km2": f"{area_km2:.1f}",
            "composite_method": config['composite_method'],
            "requires_date": config['requires_date'],
            "date_range": detected_info.get('date_range'),
            "image_date": detected_info.get('image_date'),
            "sample_image_url": sample_image_url,
            "dataset_type_info": detected_info.get('dataset_type_info', config['type'])
        }
        
        # Get revisit interval for ImageCollections
        if config['type'] == 'ImageCollection' and config['requires_date']:
            try:
                print(f"Getting revisit interval for {dataset_id}")
                revisit_info = handler.get_revisit_interval(dataset_id)
                print(f"Revisit info: {revisit_info}")
                if revisit_info['interval_days']:
                    response_data['revisit_interval'] = f"{revisit_info['interval_days']} days"
                    response_data['revisit_days'] = revisit_info['interval_days']
                    print(f"Set revisit_days to {revisit_info['interval_days']}")
                elif revisit_info['interval_hours']:
                    response_data['revisit_interval'] = f"{revisit_info['interval_hours']} hours"
                    response_data['revisit_hours'] = revisit_info['interval_hours']
                    print(f"Set revisit_hours to {revisit_info['interval_hours']}")
                else:
                    print("No revisit interval found")
            except Exception as e:
                print(f"Error getting revisit interval: {e}")
        
        return response_data
        
    except Exception as e:
        return {"success": False, "error": f"Analysis failed: {str(e)}"}

@app.post("/visualize")
async def visualize_data(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        dataset_id = request['dataset']
        config = handler.get_config(dataset_id)
        
        region = get_region_geometry(request['region_type'], request['region_name'])
        
        # Process dataset
        image, _ = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=request.get('start_date'),
            end_date=request.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {"success": False, "error": "No data available for visualization"}
        
        # Build visualization params
        vis_params = {
            "bands": config['vis_bands'],
            "min": config['vis_min'],
            "max": config['vis_max']
        }
        
        if config['vis_palette']:
            vis_params['palette'] = config['vis_palette']
        
        # Get map tile URL
        map_id = image.getMapId(vis_params)
        
        return {
            "success": True,
            "tile_url": map_id['tile_fetcher'].url_format,
            "vis_params": vis_params
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def download_time_series(body, dataset_id, config, region, scale, drive_folder):
    """Download multiple files for each revisit period"""
    from datetime import datetime, timedelta
    
    start_date = body.get('start_date')
    end_date = body.get('end_date')
    revisit_days = int(body.get('revisit_days'))
    
    if not start_date or not end_date:
        return {"success": False, "error": "Start and end dates required for time-series"}
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Split into periods
    periods = []
    current = start
    while current < end:
        period_end = min(current + timedelta(days=revisit_days), end)
        periods.append((current.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d')))
        current = period_end
    
    # Start exports for each period
    tasks = []
    for i, (p_start, p_end) in enumerate(periods):
        collection = ee.ImageCollection(dataset_id).filterDate(p_start, p_end).filterBounds(region)
        
        if config.get('cloud_filter'):
            try:
                collection = config['cloud_filter'](collection)
            except:
                pass
        
        if config.get('preprocessing'):
            try:
                collection = collection.map(config['preprocessing'])
            except:
                pass
        
        image = collection.median()
        region_collection = ee.FeatureCollection([ee.Feature(region)])
        exact_clipped = image.clipToCollection(region_collection)
        
        dataset_simple = dataset_id.split('/')[-1]
        region_simple = str(body.get('region_name', 'region')).replace(' ', '_')[:15]
        filename = f"{dataset_simple}_{region_simple}_period{i+1}_{p_start}"
        
        task = ee.batch.Export.image.toDrive(
            image=exact_clipped,
            description=filename[:100],
            folder=drive_folder,
            fileNamePrefix=filename,
            scale=scale,
            region=region,
            maxPixels=1e13,
            fileFormat='GeoTIFF',
            formatOptions={'cloudOptimized': True, 'noData': -9999},
            shardSize=256
        )
        task.start()
        tasks.append({"task_id": task.id, "filename": filename, "period": f"{p_start} to {p_end}"})
    
    return {
        "success": True,
        "export_method": "time_series",
        "total_files": len(tasks),
        "tasks": tasks,
        "drive_folder": drive_folder,
        "message": f"Started {len(tasks)} exports (one per {revisit_days}-day period)"
    }

@app.post("/download")
async def download(request: Request):
    try:
        # Get raw body first to debug
        raw_body = await request.body()
        print(f"Raw body: {raw_body}")
        
        # Try to parse JSON
        if raw_body and raw_body != b'null':
            import json
            body = json.loads(raw_body.decode('utf-8'))
        else:
            return {"success": False, "error": "No request data received - check frontend"}
            
        print(f"Parsed body: {body}")
        
        if not body or body is None:
            return {"success": False, "error": "Request body is null"}
        
        if not init_gee():
            return {"success": False, "error": "GEE initialization failed"}
        
        # Validate required fields
        if 'dataset' not in body:
            return {"success": False, "error": "Dataset is required"}
        if 'region_type' not in body:
            return {"success": False, "error": "Region type is required"}
            
        dataset_id = body['dataset']
        config = handler.get_config(dataset_id)
        export_format = body.get('export_format', 'GeoTIFF')
        drive_folder = body.get('drive_folder', 'EarthEngineExports')
        
        scale = config['scale']
        
        # Validate format compatibility
        if export_format == 'CSV' and config['type'] == 'ImageCollection':
            return {
                "success": False, 
                "error": "CSV format not suitable for ImageCollections with multiple images. Use GeoTIFF instead."
            }
        
        # Handle region based on type
        region_type = body.get('region_type')
        
        if region_type in ['geojson', 'coordinates', 'draw']:
            region_data = body.get('custom_geometry')
            if not region_data:
                return {"success": False, "error": "Custom geometry required"}
        else:
            region_data = body.get('region_name')
            if not region_data:
                return {"success": False, "error": "Region name required"}
        
        region = get_region_geometry(region_type, region_data)
        if not region:
            return {"success": False, "error": "Region not found"}
        
        # Check for time-series download
        revisit_days = body.get('revisit_days')
        if revisit_days and config['type'] == 'ImageCollection':
            return await download_time_series(body, dataset_id, config, region, scale, drive_folder)
        
        # Process dataset (single composite)
        image, count = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=body.get('start_date'),
            end_date=body.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {"success": False, "error": "No images found"}
        
        # Create CLEANER filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Extract simple dataset name
        dataset_simple = dataset_id.split('/')[-1]  # Just take last part
        region_simple = str(body.get('region_name', 'region')).replace(' ', '_').replace(',', '').replace('.', '')[:15]  # Clean and limit
        
        # Simple, clean filename format
        filename = f"{dataset_simple}_{region_simple}_{timestamp}"
        
        # Calculate file size
        area_km2 = region.area().divide(1000000).getInfo()
        pixels_per_km2 = 1000000 / (scale * scale)
        total_pixels = area_km2 * pixels_per_km2
        uncompressed_mb = (total_pixels * len(config['bands']) * 4) / (1024 * 1024)
        estimated_mb = uncompressed_mb / 3  # Apply 3x compression factor for GeoTIFF
        
        # IMPORTANT: GEE has TWO limits:
        # 1. Direct download: ~32MB file size limit via getDownloadURL()
        # 2. Request payload: 50MB limit for the entire HTTP request
        # Use 5MB threshold to be conservative (actual size may be 2-5x estimated)
        
        export_to = body.get('export_to', 'auto')
        
        # Handle GCS export (available for any file size)
        if export_to == 'gcs':
            bucket_name = body.get('gcs_bucket', 'gee-exports-free')
            
            try:
                region_collection = ee.FeatureCollection([ee.Feature(region)])
                exact_clipped_image = image.clipToCollection(region_collection)
                
                task = ee.batch.Export.image.toCloudStorage(
                    image=exact_clipped_image,
                    description=filename[:100],
                    bucket=bucket_name,
                    fileNamePrefix=filename + '_exact',
                    scale=scale,
                    region=region,
                    maxPixels=1e13,
                    fileFormat='GeoTIFF',
                    formatOptions={
                        'cloudOptimized': True,
                        'noData': -9999
                    },
                    shardSize=256  # Prevent tiling by using large shard size
                )
                task.start()
                
                return {
                    "success": True,
                    "export_method": "gcs",
                    "task_id": task.id,
                    "filename": filename + '_exact.tif',
                    "bucket": bucket_name,
                    "message": f"Export started to GCS bucket '{bucket_name}'",
                    "estimated_size": f"~{estimated_mb:.1f}MB",
                    "exact_clip": True
                }
            except Exception as e:
                return {"success": False, "error": f"GCS export failed: {str(e)}"}
        
        # Auto-routing based on file size (use 5MB threshold)
        if estimated_mb > 5 and export_format == 'GeoTIFF':
            # LARGE FILE: Export to Drive
            drive_folder = body.get('drive_folder', 'EarthEngineExports')
            
            try:
                region_collection = ee.FeatureCollection([ee.Feature(region)])
                exact_clipped_image = image.clipToCollection(region_collection)
                
                task = ee.batch.Export.image.toDrive(
                    image=exact_clipped_image,
                    description=filename[:100],
                    folder=drive_folder,
                    fileNamePrefix=filename + '_exact',
                    scale=scale,
                    region=region,
                    maxPixels=1e13,
                    fileFormat='GeoTIFF',
                    formatOptions={
                        'cloudOptimized': True,
                        'noData': -9999
                    },
                    shardSize=256  # Prevent tiling by using large shard size
                )
                task.start()
                
                return {
                    "success": True,
                    "export_method": "drive",
                    "task_id": task.id,
                    "filename": filename + '_exact.tif',
                    "folder": drive_folder,
                    "message": f"Large file (~{estimated_mb:.1f}MB) - Export started to Google Drive '{drive_folder}'",
                    "estimated_size": f"~{estimated_mb:.1f}MB",
                    "exact_clip": True
                }
                
            except Exception as export_error:
                error_msg = str(export_error)
                if "Service accounts do not have storage quota" in error_msg:
                    return {
                        "success": False,
                        "error": "OAuth authentication required for large files.",
                        "oauth_required": True,
                        "estimated_size": f"{estimated_mb:.1f}MB"
                    }
                return {
                    "success": False,
                    "error": f"Export failed: {error_msg}",
                    "estimated_size": f"{estimated_mb:.1f}MB"
                }
        
        # SMALL FILE: Direct download with exact clipping using rasterio
        elif export_format == 'GeoTIFF':
            try:
                # Apply exact clipping with rasterio for precise boundaries
                clipped_data, clipped_meta = exact_clip_region(image, region, scale)
                
                # Save to temporary file and encode
                with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                with rasterio.open(tmp_path, 'w', **clipped_meta) as dst:
                    dst.write(clipped_data)
                    # Set band descriptions to preserve GEE band names
                    if 'descriptions' in clipped_meta:
                        for i, band_name in enumerate(clipped_meta['descriptions'], 1):
                            dst.set_band_description(i, band_name)
                
                # Read and encode for download
                with open(tmp_path, 'rb') as f:
                    file_data = f.read()
                
                os.remove(tmp_path)
                
                # Return base64 encoded data for exact clip
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                
                return {
                    "success": True,
                    "export_method": "direct",
                    "exact_clip": True,
                    "file_data": encoded_data,
                    "format": export_format,
                    "filename": filename + '_exact.tif',
                    "file_size_mb": len(file_data) / (1024*1024),
                    "estimated_size": f"{len(file_data)/(1024*1024):.1f}MB",
                    "message": f"✓ Exact boundary clip ready ({len(file_data)/(1024*1024):.1f} MB)"
                }
            except Exception as download_error:
                error_msg = str(download_error)
                return {"success": False, "error": f"Exact clipping failed: {error_msg}"}
        
        elif export_format == 'CSV':
            points = ee.FeatureCollection.randomPoints(region, 100)
            samples = image.sampleRegions(
                collection=points,
                scale=scale,
                geometries=True
            )
            url = samples.getDownloadURL('CSV')
            return {
                "success": True,
                "export_method": "direct",
                "download_url": url,
                "format": "CSV",
                "filename": filename + '.csv'
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Download error: {error_details}")
        return {"success": False, "error": f"Download failed: {str(e)}"}

@app.post("/check_task_status")
async def check_task_status(request: dict):
    """Check the status of a GEE export task"""
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        task_id = request.get('task_id')
        if not task_id:
            return {"success": False, "error": "Task ID required"}
        
        # Get task status
        tasks = ee.batch.Task.list()
        task = None
        for t in tasks:
            if t.id == task_id:
                task = t
                break
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        status = task.status()
        
        return {
            "success": True,
            "state": status['state'],  # READY, RUNNING, COMPLETED, FAILED, CANCELLED
            "progress": status.get('progress', 0),
            "error_message": status.get('error_message', None)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}