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

def init_gee():
    """Initialize Google Earth Engine - try OAuth first (free), then service account"""
    try:
        # Try OAuth first (gives Drive access, completely free)
        try:
            ee.Initialize(project='plucky-sight-423703-k5')
            print("✅ GEE initialized with OAuth (FREE Google Drive access available)")
            return True
        except:
            print("⚠️  OAuth not set up, using service account (no Drive access)")
            # Fallback to service account
            key_file = 'plucky-sight-423703-k5-5965759cb7dc.json'
            service_account_email = 'gee-service-account@plucky-sight-423703-k5.iam.gserviceaccount.com'
            credentials = ee.ServiceAccountCredentials(service_account_email, key_file)
            ee.Initialize(credentials)
            print("✅ GEE initialized with service account (no Drive access)")
            return True
    except Exception as e:
        print(f"❌ GEE initialization failed: {e}")
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
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Earth Engine Data Pipeline</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #fafafa;
                color: #333;
                line-height: 1.5;
                height: 100vh;
                overflow: hidden;
            }
            .container {
                display: grid;
                grid-template-columns: 400px 1fr;
                height: 100vh;
            }
            .form-panel {
                background: white;
                border-right: 1px solid #e5e5e5;
                padding: 2rem;
                overflow-y: auto;
            }
            .preview-panel {
                background: #f8f9fa;
                padding: 2rem;
                overflow-y: auto;
            }
            .header {
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #e5e5e5;
            }
            .header h1 {
                font-size: 1.5rem;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 0.25rem;
            }
            .header p {
                color: #666;
                font-size: 0.9rem;
            }
            .form-group {
                margin-bottom: 1.25rem;
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: #333;
                font-size: 0.85rem;
            }
            input, select {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 0.9rem;
                background: white;
                transition: border-color 0.2s;
            }
            input:focus, select:focus {
                outline: none;
                border-color: #6b7280;
            }
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
            }
            button {
                width: 100%;
                padding: 0.75rem;
                border: none;
                border-radius: 6px;
                font-size: 0.9rem;
                font-weight: 500;
                cursor: pointer;
                margin-bottom: 0.75rem;
                transition: all 0.2s;
            }
            .btn-primary {
                background: #1a1a1a;
                color: white;
            }
            .btn-primary:hover {
                background: #333;
            }
            .btn-secondary {
                background: white;
                color: #333;
                border: 1px solid #d1d5db;
            }
            .btn-secondary:hover {
                background: #f9fafb;
            }
            .preview-header {
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #e5e5e5;
            }
            .preview-header h2 {
                font-size: 1.25rem;
                font-weight: 600;
                color: #1a1a1a;
            }
            .preview-content {
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                border: 1px solid #e5e5e5;
            }
            .info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 1.5rem;
            }
            .info-item {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 6px;
                border-left: 3px solid #6b7280;
            }
            .info-item.optimized {
                border-left-color: #10b981;
            }
            .info-item strong {
                display: block;
                color: #666;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.25rem;
            }
            .info-item span {
                font-size: 1rem;
                font-weight: 600;
                color: #1a1a1a;
            }
            .badge {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            .badge.optimized {
                background: #d1fae5;
                color: #065f46;
            }
            .badge.auto {
                background: #dbeafe;
                color: #1e40af;
            }
            .bands-list {
                background: #f8f9fa;
                border-radius: 6px;
                padding: 1rem;
                margin: 1rem 0;
            }
            .bands-list h4 {
                margin-bottom: 0.75rem;
                color: #666;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .band-item {
                background: white;
                padding: 0.75rem;
                margin: 0.5rem 0;
                border-radius: 4px;
                border-left: 2px solid #6b7280;
                font-size: 0.85rem;
            }
            .empty-state {
                text-align: center;
                color: #999;
                padding: 3rem 1rem;
            }
            .empty-state h3 {
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
                color: #666;
            }
            .loading {
                text-align: center;
                padding: 2rem;
                color: #666;
            }
            .spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #666;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 0.5rem;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result {
                margin-top: 1rem;
                padding: 1rem;
                border-radius: 6px;
                background: #f0f9ff;
                border-left: 3px solid #0ea5e9;
            }
            .error {
                background: #fef2f2;
                border-left-color: #ef4444;
            }
            details {
                margin-top: 1rem;
                background: #f8f9fa;
                border-radius: 6px;
                padding: 1rem;
            }
            summary {
                cursor: pointer;
                font-weight: 500;
                color: #666;
                font-size: 0.85rem;
            }
            pre {
                background: #1a1a1a;
                color: #e5e5e5;
                padding: 1rem;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 0.8rem;
                margin-top: 0.5rem;
            }
            @media (max-width: 1024px) {
                .container {
                    grid-template-columns: 1fr;
                    grid-template-rows: auto 1fr;
                }
                .form-panel {
                    border-right: none;
                    border-bottom: 1px solid #e5e5e5;
                }
            }
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }
            .modal.active {
                display: flex;
            }
            .modal-content {
                background: white;
                padding: 2rem;
                border-radius: 8px;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }
            .modal-content label:has(input[type="radio"]:checked) {
                border-color: #1a1a1a;
                background: #f8f9fa;
            }
            .progress-bar {
                width: 100%;
                height: 24px;
                background: #e5e5e5;
                border-radius: 12px;
                overflow: hidden;
                margin: 1rem 0;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #10b981, #059669);
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.75rem;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="form-panel">
                <div class="header">
                    <h1>Earth Engine Pipeline</h1>
                    <p>Universal satellite data downloader</p>
                </div>
                
                <div class="form-group">
                    <label for="dataset">Dataset Collection ID</label>
                    <input type="text" id="dataset" placeholder="MODIS/061/MOD11A1" required>
                    <small style="color: #666; font-size: 0.8rem;">Try any GEE dataset - auto-detection enabled!</small>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="startDate">Start Date <span style="color: #999; font-size: 0.75rem;">(optional for static datasets)</span></label>
                        <input type="date" id="startDate" value="2023-01-01">
                    </div>
                    <div class="form-group">
                        <label for="endDate">End Date <span style="color: #999; font-size: 0.75rem;">(optional for static datasets)</span></label>
                        <input type="date" id="endDate" value="2023-01-31">
                    </div>
                </div>
                
                <input type="hidden" id="revisitDays">
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="regionType">Region Selection Method</label>
                        <select id="regionType" onchange="updateRegionMethod()">
                            <option value="">Select Method</option>
                            <option value="country">Predefined - Country</option>
                            <option value="state">Predefined - State/Province</option>
                            <option value="city">Predefined - City</option>
                            <option value="continent">Predefined - Continent</option>
                            <option value="geojson">Upload GeoJSON</option>
                            <option value="coordinates">Enter Coordinates</option>
                            <option value="draw">Draw on Map</option>
                        </select>
                    </div>
                    <div id="regionInputContainer"></div>
                </div>
                
                <div class="form-group">
                    <label for="exportFormat">Export Format</label>
                    <select id="exportFormat">
                        <option value="GeoTIFF">GeoTIFF (Raster)</option>
                        <option value="CSV">CSV (100 samples)</option>
                    </select>
                </div>
                
                <button class="btn-primary" onclick="preview()">Analyze Dataset</button>
                
                <div id="result"></div>
            </div>
            
            <div class="preview-panel">
                <div class="preview-header">
                    <h2>Dataset Preview</h2>
                </div>
                
                <div id="previewContent">
                    <div class="empty-state">
                        <h3>No Dataset Selected</h3>
                        <p>Enter any GEE dataset ID and click "Analyze Dataset"</p>
                        <p style="margin-top: 1rem; font-size: 0.85rem;">Examples: MODIS/061/MOD11A1, COPERNICUS/S2_SR_HARMONIZED, USGS/SRTMGL1_003</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="progressModal" class="modal">
            <div class="modal-content">
                <h3 style="margin-bottom: 1rem;">Exporting to Google Drive</h3>
                <div id="progressInfo" style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">
                    Initializing export...
                </div>
                <div class="progress-bar">
                    <div id="progressFill" class="progress-fill" style="width: 0%">0%</div>
                </div>
                <div id="progressStatus" style="color: #999; font-size: 0.85rem; text-align: center;">
                    Status: READY
                </div>
                <button id="closeProgressBtn" class="btn-secondary" style="margin-top: 1rem; display: none;" onclick="closeProgressModal()">
                    Close
                </button>
            </div>
        </div>

        <script>
            const regions = {
                country: ["United States", "China", "India", "Brazil", "Russia", "Canada", "Australia", "Germany", "United Kingdom", "France", "Italy", "Spain", "Mexico", "Japan", "South Africa", "Nigeria", "Egypt", "Turkey", "Iran", "Pakistan"],
                state: ["California", "Texas", "Florida", "New York", "Pennsylvania", "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan", "Maharashtra", "Uttar Pradesh", "Bihar", "West Bengal", "Madhya Pradesh", "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh"],
                city: ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ludhiana", "Agra", "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
                continent: ["Asia", "Europe", "Africa", "North America", "South America", "Oceania"]
            };
            
            function updateRegionMethod() {
                const method = document.getElementById('regionType').value;
                const container = document.getElementById('regionInputContainer');
                
                if (method === 'country' || method === 'state' || method === 'continent' || method === 'city') {
                    // Existing dropdown selection
                    container.innerHTML = `
                        <div class="form-group">
                            <label for="regionName">Region Name</label>
                            <select id="regionName">
                                <option value="">Select Region</option>
                            </select>
                        </div>
                    `;
                    updateRegionOptions();
                }
                else if (method === 'geojson') {
                    container.innerHTML = `
                        <div class="form-group">
                            <label for="geoJsonFile">Upload GeoJSON File</label>
                            <input type="file" id="geoJsonFile" accept=".json,.geojson" 
                                onchange="handleGeoJSONUpload(event)">
                            <small style="color: #666; font-size: 0.8rem;">
                                Upload a GeoJSON file with your area of interest
                            </small>
                            <div id="geoJsonPreview" style="margin-top: 0.5rem;"></div>
                        </div>
                    `;
                }
                else if (method === 'coordinates') {
                    container.innerHTML = `
                        <div class="form-group">
                            <label>Bounding Box Coordinates</label>
                            <div class="form-row">
                                <input type="number" id="minLon" placeholder="Min Longitude" step="0.0001">
                                <input type="number" id="minLat" placeholder="Min Latitude" step="0.0001">
                            </div>
                            <div class="form-row">
                                <input type="number" id="maxLon" placeholder="Max Longitude" step="0.0001">
                                <input type="number" id="maxLat" placeholder="Max Latitude" step="0.0001">
                            </div>
                            <small style="color: #666; font-size: 0.8rem;">
                                Example: San Francisco Bay: minLon=-122.5, minLat=37.3, maxLon=-122.0, maxLat=37.9
                            </small>
                        </div>
                    `;
                }
                else if (method === 'draw') {
                    container.innerHTML = `
                        <div class="form-group">
                            <label>Draw Custom Region</label>
                            <div id="mapContainer" style="width: 100%; height: 400px; border: 1px solid #d1d5db; border-radius: 6px; margin-top: 0.5rem;"></div>
                            <button class="btn-secondary" onclick="initDrawMap()" style="margin-top: 0.5rem;">
                                Initialize Map
                            </button>
                            <div id="drawInstructions" style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;"></div>
                        </div>
                    `;
                }
            }
            // Store custom geometry globally
            window.customGeometry = null;

            // Handle GeoJSON file upload
            function handleGeoJSONUpload(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const geoJson = JSON.parse(e.target.result);
                        
                        // Extract geometry from different GeoJSON structures
                        let geometry;
                        if (geoJson.type === 'FeatureCollection') {
                            // Get geometry from first feature
                            geometry = geoJson.features[0].geometry;
                        } else if (geoJson.type === 'Feature') {
                            // Get geometry from feature
                            geometry = geoJson.geometry;
                        } else if (geoJson.type === 'Polygon' || geoJson.type === 'MultiPolygon' || 
                                geoJson.type === 'Point' || geoJson.type === 'LineString') {
                            // Already a geometry object
                            geometry = geoJson;
                        } else {
                            throw new Error('Unsupported GeoJSON type');
                        }
                        
                        window.customGeometry = geometry;
                        
                        // Show preview
                        document.getElementById('geoJsonPreview').innerHTML = `
                            <div style="background: #f0f9ff; padding: 0.75rem; border-radius: 4px; border-left: 3px solid #0ea5e9;">
                                <strong>✓ GeoJSON Loaded</strong><br>
                                <small>Type: ${geometry.type}</small>
                            </div>
                        `;
                    } catch (error) {
                        document.getElementById('geoJsonPreview').innerHTML = `
                            <div style="background: #fef2f2; padding: 0.75rem; border-radius: 4px; border-left: 3px solid #ef4444;">
                                <strong>✗ Invalid GeoJSON</strong><br>
                                <small>${error.message}</small>
                            </div>
                        `;
                    }
                };
                reader.readAsText(file);
            }

            // Handle coordinate input
            function getCoordinateGeometry() {
                const minLon = parseFloat(document.getElementById('minLon').value);
                const minLat = parseFloat(document.getElementById('minLat').value);
                const maxLon = parseFloat(document.getElementById('maxLon').value);
                const maxLat = parseFloat(document.getElementById('maxLat').value);
                
                if (isNaN(minLon) || isNaN(minLat) || isNaN(maxLon) || isNaN(maxLat)) {
                    return null;
                }
                
                // Create GeoJSON rectangle
                return {
                    "type": "Polygon",
                    "coordinates": [[
                        [minLon, minLat],
                        [maxLon, minLat],
                        [maxLon, maxLat],
                        [minLon, maxLat],
                        [minLon, minLat]
                    ]]
                };
            }

            function updateRegionOptions() {
                const regionType = document.getElementById('regionType').value;
                const regionSelect = document.getElementById('regionName');
                regionSelect.innerHTML = '<option value="">Select Region</option>';
                regionSelect.disabled = !regionType;
                if (regionType && regions[regionType]) {
                    regions[regionType].forEach(region => {
                        regionSelect.innerHTML += `<option value="${region}">${region}</option>`;
                    });
                }
            }
            
            function showLoading(message) {
                document.getElementById('previewContent').innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        ${message}
                    </div>
                `;
            }
            
            async function preview() {
                const dataset = document.getElementById('dataset').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const regionType = document.getElementById('regionType').value;

                let requestData = {
                    dataset,
                    start_date: startDate,
                    end_date: endDate,
                    region_type: regionType,
                    region_name: regionType
                };
                            
                // Add region-specific data
                if (regionType === 'country' || regionType === 'state' || regionType === 'continent') {
                    const regionName = document.getElementById('regionName').value;
                    if (!regionName) {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Please select a region</div>
                        `;
                        return;
                    }
                    requestData.region_name = regionName;
                }
                else if (regionType === 'geojson' || regionType === 'draw') {
                    if (!window.customGeometry) {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Please upload/draw a region first</div>
                        `;
                        return;
                    }
                    requestData.region_name = 'Custom Region';
                    requestData.custom_geometry = window.customGeometry;
                }
                else if (regionType === 'coordinates') {
                    const geometry = getCoordinateGeometry();
                    if (!geometry) {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Please enter valid coordinates</div>
                        `;
                        return;
                    }
                    requestData.region_name = 'Custom Region';
                    requestData.custom_geometry = geometry;
                }
                
                
                showLoading('Analyzing dataset...');
                
                try {
                    const response = await fetch('/preview', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(requestData)
                    });
                    
                    const result = await response.json();
                    console.log('Preview result:', result);
                    
                    if (result.success) {
                        // Auto-fill revisit interval if detected
                        console.log('Revisit days:', result.revisit_days, 'Revisit hours:', result.revisit_hours);
                        if (result.revisit_days) {
                            document.getElementById('revisitDays').value = result.revisit_days;
                            console.log('Set revisit days to:', result.revisit_days);
                        } else if (result.revisit_hours) {
                            document.getElementById('revisitDays').value = (result.revisit_hours / 24).toFixed(2);
                            console.log('Set revisit hours to:', result.revisit_hours);
                        }
                        
                        // Store band details globally for showAllBands function
                        window.currentBandDetails = result.band_details || result.bands.map(b => ({name: b, data_type: 'N/A', scale: 'N/A', crs: 'N/A'}));
                        
                        // Enhanced band details display
                        let bandDetails = '';
                        if (result.band_details && result.band_details.length > 0) {
                            bandDetails = result.band_details.slice(0, 12).map(band => 
                                `<div class="band-item" style="padding: 8px; font-size: 0.85rem; border: 1px solid #e0e0e0; border-radius: 4px; background: white;">
                                    <div style="font-weight: 600; color: #333;">${band.name}</div>
                                    <div style="font-size: 0.75rem; color: #666; margin-top: 2px;">
                                        ${band.data_type} | ${band.scale}m | ${band.crs}
                                    </div>
                                </div>`
                            ).join('');
                        } else {
                            bandDetails = result.bands.slice(0, 12).map(b => 
                                `<div class="band-item" style="padding: 6px 8px; font-size: 0.85rem; border: 1px solid #e0e0e0; border-radius: 4px;">${b}</div>`
                            ).join('');
                        }
                        
                        // Size warning display
                        let sizeWarningDisplay = '';
                        if (result.size_warning) {
                            const warningColor = result.size_warning.type === 'size_limit' ? '#dc3545' : '#ffc107';
                            const warningBg = result.size_warning.type === 'size_limit' ? '#f8d7da' : '#fff3cd';
                            
                            sizeWarningDisplay = `
                                <div style="background: ${warningBg}; padding: 1rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid ${warningColor};">
                                    <strong style="font-size: 0.85rem; color: ${warningColor};">⚠️ ${result.size_warning.message}</strong>
                                    <ul style="margin: 0.5rem 0 0 1.25rem; font-size: 0.8rem; color: #666;">
                                        ${result.size_warning.suggestions.map(s => `<li>${s}</li>`).join('')}
                                    </ul>
                                </div>`;
                        }
                        
                        // Download mode selection for temporal datasets
                        let downloadModeSelector = '';
                        if (result.revisit_interval && result.revisit_days) {
                            console.log('Creating download mode selector for revisit:', result.revisit_interval);
                            const numPeriods = Math.ceil((new Date(document.getElementById('endDate').value) - new Date(document.getElementById('startDate').value)) / (1000 * 60 * 60 * 24 * result.revisit_days));
                            console.log('Number of periods:', numPeriods);
                            downloadModeSelector = `
                                <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; margin: 1rem 0; border: 2px solid #059669;">
                                    <h4 style="margin: 0 0 0.75rem 0; color: #059669;">📊 Download Mode</h4>
                                    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                                        <label style="display: flex; align-items: start; cursor: pointer; padding: 0.75rem; background: white; border: 2px solid #e0e0e0; border-radius: 4px;">
                                            <input type="radio" name="downloadMode" value="composite" checked style="margin-top: 0.25rem; margin-right: 0.75rem;">
                                            <div>
                                                <strong>Single Composite File</strong>
                                                <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">
                                                    Merge all ${result.image_count} images into 1 file using <strong>${result.composite_method}</strong> reduction
                                                </div>
                                                <div style="font-size: 0.8rem; color: #999; margin-top: 0.25rem;">
                                                    ✓ Best for general analysis | ✓ Single file to manage
                                                </div>
                                            </div>
                                        </label>
                                        <label style="display: flex; align-items: start; cursor: pointer; padding: 0.75rem; background: white; border: 2px solid #e0e0e0; border-radius: 4px;">
                                            <input type="radio" name="downloadMode" value="timeseries" style="margin-top: 0.25rem; margin-right: 0.75rem;">
                                            <div>
                                                <strong>Time-Series (${numPeriods} Files)</strong>
                                                <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">
                                                    Download ${numPeriods} separate files, one per ${result.revisit_interval} (each uses ${result.composite_method} for that period)
                                                </div>
                                                <div style="font-size: 0.8rem; color: #999; margin-top: 0.25rem;">
                                                    ✓ Track changes over time | ✓ Better cloud handling per period
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                </div>
                            `;
                        }
                        
                            // Size-based download options with GCS option for all
                            const downloadButton = result.estimated_mb > 5
                                ? `<button class="btn-primary" onclick="confirmDownload()">
                                    Export to Google Drive (approx ${result.estimated_size})
                                </button>
                                <button class="btn-secondary" onclick="exportToGCS()" style="margin-top: 0.5rem;">
                                    Also Export to GCS Bucket
                                </button>`
                                : `<button class="btn-primary" onclick="confirmDownload()">
                                    Download to Computer (approx ${result.estimated_size})
                                </button>
                                <button class="btn-secondary" onclick="exportToGCS()" style="margin-top: 0.5rem;">
                                    Also Export to GCS Bucket
                                </button>`;
                        
                        document.getElementById('previewContent').innerHTML = `
                            <div class="preview-content">
                                <h3 style="margin-bottom: 0.5rem;">
                                    ${result.dataset_name || dataset}
                                </h3>
                                <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.4;">
                                    ${result.description}
                                </p>
                                
                                ${sizeWarningDisplay}
                                
                                <div class="info-grid">
                                    <div class="info-item">
                                        <strong>Dataset Type</strong>
                                        <span>${result.dataset_type_info}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Region</strong>
                                        <span>${requestData.region_name}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Images Found</strong>
                                        <span>${result.image_count}</span>
                                    </div>
                                    ${result.revisit_interval ? `
                                    <div class="info-item">
                                        <strong>Revisit Interval</strong>
                                        <span>${result.revisit_interval}</span>
                                    </div>
                                    ` : ''}
                                    <div class="info-item">
                                        <strong>Reduction Method</strong>
                                        <span>${result.composite_method || 'N/A'}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Area Coverage</strong>
                                        <span>${result.area_km2} km²</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Native Resolution</strong>
                                        <span>${result.native_resolution}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Approx File Size</strong>
                                        <span>${result.estimated_size}</span>
                                    </div>
                                </div>
                                
                                <div class="bands-list">
                                    <h4>Band Information (${result.bands.length} total)</h4>
                                    <div id="bandsList" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; max-height: 300px; overflow-y: auto;">
                                        ${bandDetails}
                                    </div>
                                    ${result.bands.length > 12 ? `<div style="text-align: center; margin-top: 8px;"><button onclick="showAllBands()" style="background: #f0f0f0; border: 1px solid #ccc; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem;">Show All ${result.bands.length} Bands</button></div>` : ''}
                                </div>
                                
                                ${downloadModeSelector}
                                
                                ${downloadButton}
                                
                                <details style="margin-top: 1rem;">
                                    <summary>Technical Details</summary>
                                    <pre>${JSON.stringify({
                                        dataset_id: result.dataset_id,
                                        type: result.dataset_type,
                                        requires_date: result.requires_date,
                                        composite_method: result.composite_method,
                                        native_resolution: result.native_resolution
                                    }, null, 2)}</pre>
                                </details>
                            </div>
                        `;
                        document.getElementById('result').innerHTML = '';
                        
                    } else {
                        let errorMsg = result.error;
                        let suggestion = '';
                        
                        // Provide helpful suggestions based on error type
                        if (errorMsg.includes('Empty date range') || errorMsg.includes('date')) {
                            suggestion = '<p style="margin-top: 0.5rem;">💡 <strong>Try:</strong> Make sure start date is before end date, or leave dates empty for static datasets.</p>';
                        } else if (errorMsg.includes('No images found')) {
                            suggestion = '<p style="margin-top: 0.5rem;">💡 <strong>Try:</strong> Different date range, different region, or check if dataset ID is correct.</p>';
                        } else if (errorMsg.includes('Cannot access dataset')) {
                            suggestion = '<p style="margin-top: 0.5rem;">💡 <strong>Try:</strong> Verify the dataset ID is correct. Check <a href="https://developers.google.com/earth-engine/datasets" target="_blank">GEE Catalog</a>.</p>';
                        }
                        
                        document.getElementById('previewContent').innerHTML = `
                            <div class="preview-content">
                                <div class="result error">
                                    <strong>Analysis Error:</strong><br>
                                    ${errorMsg}
                                    ${suggestion}
                                </div>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('previewContent').innerHTML = `
                        <div class="result error">Network Error: ${error.message}</div>
                    `;
                }
            }
            
            function showAllBands() {
                const allBands = window.currentBandDetails || [];
                const bandListDiv = document.querySelector('.bands-list');
                
                const bandDetails = allBands.map(band => 
                    `<div class="band-item">
                        <strong>${band.name}</strong><br>
                        ${band.pixel_size_m}m | ${band.crs}
                    </div>`
                ).join('');
                
                bandListDiv.innerHTML = `
                    <h4>All Bands (${allBands.length} total)</h4>
                    ${bandDetails}
                `;
            }
            
            // Global variable to store pending download request
            let pendingDownloadRequest = null;

            function closeProgressModal() {
                document.getElementById('progressModal').classList.remove('active');
            }

            async function exportToGCS() {
                const bucketName = prompt('Enter GCS bucket name:', 'gee-exports-free');
                if (!bucketName) return;
                
                const dataset = document.getElementById('dataset').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const regionType = document.getElementById('regionType').value;
                const exportFormat = document.getElementById('exportFormat').value;
                
                let requestData = {
                    dataset,
                    start_date: startDate,
                    end_date: endDate,
                    region_type: regionType,
                    export_format: exportFormat,
                    export_to: 'gcs',
                    gcs_bucket: bucketName
                };
                
                // Add region data
                if (regionType === 'country' || regionType === 'state' || regionType === 'continent') {
                    const regionName = document.getElementById('regionName').value;
                    if (!regionName) {
                        alert('Please select a region');
                        return;
                    }
                    requestData.region_name = regionName;
                }
                else if (regionType === 'geojson' || regionType === 'draw') {
                    if (!window.customGeometry) {
                        alert('Please upload/draw a region first');
                        return;
                    }
                    requestData.region_name = 'Custom Region';
                    requestData.custom_geometry = window.customGeometry;
                }
                else if (regionType === 'coordinates') {
                    const geometry = getCoordinateGeometry();
                    if (!geometry) {
                        alert('Please enter valid coordinates');
                        return;
                    }
                    requestData.region_name = 'Custom Region';
                    requestData.custom_geometry = geometry;
                }
                
                showLoading('Starting GCS export...');
                
                try {
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(requestData)
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('previewContent').innerHTML = '';
                    
                    if (result.success && result.export_method === 'gcs') {
                        document.getElementById('result').innerHTML = `
                            <div class="result">
                                <strong>🚀 GCS Export Started</strong><br>
                                Bucket: ${result.bucket}<br>
                                File: ${result.filename}<br>
                                <button onclick="checkGCSStatus('${result.task_id}')" class="btn-secondary" style="margin-top: 0.5rem;">
                                    Check Status
                                </button>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">GCS Export Error: ${result.error}</div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('previewContent').innerHTML = '';
                    document.getElementById('result').innerHTML = `
                        <div class="result error">Network Error: ${error.message}</div>
                    `;
                }
            }

            async function checkGCSStatus(taskId) {
                try {
                    const response = await fetch('/check_task_status', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({task_id: taskId})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        if (result.state === 'COMPLETED') {
                            document.getElementById('result').innerHTML = `
                                <div class="result">
                                    <strong>✅ GCS Export Complete</strong><br>
                                    <small>File is now in your GCS bucket</small>
                                </div>
                            `;
                        } else if (result.state === 'FAILED') {
                            document.getElementById('result').innerHTML = `
                                <div class="result error">
                                    <strong>❌ GCS Export Failed</strong><br>
                                    ${result.error_message || 'Unknown error'}
                                </div>
                            `;
                        } else {
                            document.getElementById('result').innerHTML = `
                                <div class="result">
                                    <strong>⏳ GCS Export Running</strong><br>
                                    Status: ${result.state}<br>
                                    <button onclick="checkGCSStatus('${taskId}')" class="btn-secondary" style="margin-top: 0.5rem;">
                                        Check Again
                                    </button>
                                </div>
                            `;
                        }
                    }
                } catch (error) {
                    alert('Error checking status: ' + error.message);
                }
            }

            async function confirmDownload() {
                const dataset = document.getElementById('dataset').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const regionType = document.getElementById('regionType').value;
                const exportFormat = document.getElementById('exportFormat').value;
                
                // Check download mode selection
                const downloadMode = document.querySelector('input[name="downloadMode"]:checked');
                const useTimeSeries = downloadMode && downloadMode.value === 'timeseries';
                
                let requestData = {
                    dataset,
                    start_date: startDate,
                    end_date: endDate,
                    region_type: regionType,
                    export_format: exportFormat
                };
                
                // Only add revisit_days if time-series mode is selected
                if (useTimeSeries) {
                    const revisitDaysInput = document.getElementById('revisitDays');
                    if (revisitDaysInput && revisitDaysInput.value) {
                        requestData.revisit_days = parseInt(revisitDaysInput.value);
                    }
                }
                
                // Add region data
                if (regionType === 'country' || regionType === 'state' || regionType === 'continent') {
                    const regionName = document.getElementById('regionName').value;
                    if (!regionName) {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Please select a region</div>
                        `;
                        return;
                    }
                    requestData.region_name = regionName;
                }
                else if (regionType === 'geojson' || regionType === 'draw') {
                    if (!window.customGeometry) {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Please upload/draw a region first</div>
                        `;
                        return;
                    }
                    requestData.region_name = 'Custom Region';
                    requestData.custom_geometry = window.customGeometry;
                }
                else if (regionType === 'coordinates') {
                    const geometry = getCoordinateGeometry();
                    if (!geometry) {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Please enter valid coordinates</div>
                        `;
                        return;
                    }
                    requestData.region_name = 'Custom Region';
                    requestData.custom_geometry = geometry;
                }
                
                // Send request directly
                showLoading('Processing download...');
                
                try {
                    console.log('Sending download request:', requestData);
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(requestData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        if (result.export_method === 'time_series') {
                            // Show time-series export progress
                            let taskList = result.tasks.map((t, i) => 
                                `<li><strong>File ${i+1}:</strong> ${t.filename}.tif (${t.period})</li>`
                            ).join('');
                            
                            document.getElementById('previewContent').innerHTML = `
                                <div class="preview-content">
                                    <div class="result">
                                        <h3>🚀 Time-Series Export Started</h3>
                                        <p><strong>${result.total_files} files</strong> are being exported to Google Drive folder: <strong>${result.drive_folder}</strong></p>
                                        <ul style="text-align: left; margin: 1rem 0;">${taskList}</ul>
                                        <p style="font-size: 0.85rem; color: #666; margin-top: 1rem;">
                                            Check your Google Drive in 5-30 minutes. Each file represents one time period.
                                        </p>
                                    </div>
                                </div>
                            `;
                        } else if (result.export_method === 'cloud_storage') {
                            // Show cloud storage export progress
                            document.getElementById('previewContent').innerHTML = `
                                <div class="preview-content">
                                    <div class="result">
                                        <h3>🚀 Export Started</h3>
                                        <p>Large file (${result.estimated_size}) is being processed in Google Cloud Storage.</p>
                                        <p><strong>Export ID:</strong> ${result.export_id}</p>
                                        <p><strong>Estimated time:</strong> 5-30 minutes</p>
                                        <div style="margin-top: 1rem;">
                                            <button onclick="checkCloudStorageStatus('${result.task_id}', '${result.download_url}', '${result.filename}')" 
                                                    class="btn-primary">Check Status</button>
                                        </div>
                                        <p style="font-size: 0.85rem; color: #666; margin-top: 1rem;">
                                            The file will be available for download once processing is complete.
                                        </p>
                                    </div>
                                </div>
                            `;
                        } else if (result.export_method === 'drive') {
                            // Show progress modal for Drive export
                            showProgressModal(result);
                        } else {
                            // Direct download - handle both URL and base64 data
                            const filename = result.filename || 'gee_download';
                            
                            if (result.exact_clip && result.file_data) {
                                // Handle base64 encoded exact clip
                                document.getElementById('previewContent').innerHTML = `
                                    <div class="preview-content">
                                        <div class="result">
                                            <h3>✅ Exact Clip Ready</h3>
                                            <p>Your ${result.format} file with exact boundary clipping is ready.</p>
                                            <p style="color: #059669; font-weight: 500;">✓ Exact region boundaries preserved</p>
                                            <button onclick="downloadBase64File('${result.file_data}', '${filename}')" 
                                            style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; 
                                                    background: #1a1a1a; color: white; border: none; 
                                                    border-radius: 4px; cursor: pointer;">📥 Download Exact Clip</button>
                                        </div>
                                    </div>
                                `;
                            } else {
                                // Handle regular URL download
                                document.getElementById('previewContent').innerHTML = `
                                    <div class="preview-content">
                                        <div class="result">
                                            <h3>✅ Download Ready</h3>
                                            <p>Your ${result.format} file is ready for download.</p>
                                            <a href="${result.download_url}" download="${filename}" 
                                            style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; 
                                                    background: #1a1a1a; color: white; text-decoration: none; 
                                                    border-radius: 4px;">📥 Download File</a>
                                        </div>
                                    </div>
                                `;
                            }
                        }
                    } else {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">Download Error: ${result.error}</div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result error">Network Error: ${error.message}</div>
                    `;
                }
                
                hideLoading();
            }

            async function checkCloudStorageStatus(taskId, downloadUrl, filename) {
                try {
                    const response = await fetch('/check_task_status', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({task_id: taskId})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        if (result.status === 'COMPLETED') {
                            document.getElementById('previewContent').innerHTML = `
                                <div class="preview-content">
                                    <div class="result">
                                        <h3>✅ Export Complete</h3>
                                        <p>Your file is ready for download!</p>
                                        <div style="margin-top: 1rem;">
                                            <a href="${downloadUrl}" download="${filename}" 
                                               style="display: inline-block; padding: 0.75rem 1.5rem; 
                                                      background: #1a1a1a; color: white; text-decoration: none; 
                                                      border-radius: 4px;">Download File</a>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else if (result.status === 'FAILED') {
                            document.getElementById('previewContent').innerHTML = `
                                <div class="preview-content">
                                    <div class="result error">
                                        <h3>❌ Export Failed</h3>
                                        <p>The export failed. Please try again with a smaller area.</p>
                                    </div>
                                </div>
                            `;
                        } else {
                            // Still running
                            document.getElementById('previewContent').innerHTML = `
                                <div class="preview-content">
                                    <div class="result">
                                        <h3>⏳ Processing...</h3>
                                        <p>Status: ${result.status}</p>
                                        <p>Export is still running. Please wait...</p>
                                        <div style="margin-top: 1rem;">
                                            <button onclick="checkCloudStorageStatus('${taskId}', '${downloadUrl}', '${filename}')" 
                                                    class="btn-primary">Check Again</button>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    } else {
                        alert('Error checking status: ' + result.error);
                    }
                } catch (error) {
                    alert('Network error: ' + error.message);
                }
            }

            function showProgressModal(exportResult) {
                // Hide preview panel, show modal
                document.getElementById('progressModal').classList.add('active');
                document.getElementById('progressInfo').innerHTML = `
                    <strong>File:</strong> ${exportResult.filename}<br>
                    <strong>Size:</strong> ${exportResult.estimated_size}<br>
                    <strong>Folder:</strong> ${exportResult.folder}
                `;
                
                // Start monitoring progress
                monitorTaskProgress(exportResult.task_id);
            }

            async function monitorTaskProgress(taskId) {
                const checkInterval = 3000; // Check every 3 seconds
                let attempts = 0;
                const maxAttempts = 600; // 30 minutes max
                
                const checkStatus = async () => {
                    try {
                        const response = await fetch('/check_task_status', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ task_id: taskId })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            const state = result.state;
                            const progress = Math.round(result.progress * 100);
                            
                            // Update progress bar
                            document.getElementById('progressFill').style.width = `${progress}%`;
                            document.getElementById('progressFill').textContent = `${progress}%`;
                            document.getElementById('progressStatus').textContent = `Status: ${state}`;
                            
                            if (state === 'COMPLETED') {
                                // Success!
                                document.getElementById('progressInfo').innerHTML = `
                                    <div style="background: #d1fae5; padding: 1rem; border-radius: 6px; border-left: 3px solid #10b981;">
                                        <strong>✅ Export Complete!</strong><br>
                                        <small>Check your Google Drive for the file.</small>
                                    </div>
                                `;
                                document.getElementById('progressFill').style.width = '100%';
                                document.getElementById('progressFill').textContent = '100%';
                                document.getElementById('closeProgressBtn').style.display = 'block';
                                
                                // Update preview panel
                                document.getElementById('previewContent').innerHTML = `
                                    <div class="preview-content">
                                        <div class="result" style="background: #d1fae5; border-left-color: #10b981;">
                                            <h3>✅ Export Complete!</h3>
                                            <p>Your file has been successfully exported to Google Drive.</p>
                                            <a href="https://drive.google.com" target="_blank" 
                                            style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; 
                                                    background: #1a1a1a; color: white; text-decoration: none; 
                                                    border-radius: 6px; font-weight: 500;">
                                                Open Google Drive
                                            </a>
                                        </div>
                                    </div>
                                `;
                                
                            } else if (state === 'FAILED') {
                                // Failed
                                document.getElementById('progressInfo').innerHTML = `
                                    <div style="background: #fef2f2; padding: 1rem; border-radius: 6px; border-left: 3px solid #ef4444;">
                                        <strong>❌ Export Failed</strong><br>
                                        <small>${result.error_message || 'Unknown error'}</small>
                                    </div>
                                `;
                                document.getElementById('closeProgressBtn').style.display = 'block';
                                
                            } else if (state === 'CANCELLED') {
                                document.getElementById('progressInfo').innerHTML = `
                                    <div style="background: #fff3cd; padding: 1rem; border-radius: 6px; border-left: 3px solid #ffc107;">
                                        <strong>⚠️ Export Cancelled</strong>
                                    </div>
                                `;
                                document.getElementById('closeProgressBtn').style.display = 'block';
                                
                            } else {
                                // Still running - check again
                                attempts++;
                                if (attempts < maxAttempts) {
                                    setTimeout(checkStatus, checkInterval);
                                } else {
                                    document.getElementById('progressInfo').innerHTML = `
                                        <div style="background: #fff3cd; padding: 1rem; border-radius: 6px;">
                                            <strong>⏱️ Export taking longer than expected</strong><br>
                                            <small>Check Google Drive manually or close this dialog.</small>
                                        </div>
                                    `;
                                    document.getElementById('closeProgressBtn').style.display = 'block';
                                }
                            }
                        }
                    } catch (error) {
                        console.error('Status check failed:', error);
                        // Retry
                        attempts++;
                        if (attempts < maxAttempts) {
                            setTimeout(checkStatus, checkInterval);
                        }
                    }
                };
                
                // Start checking
                checkStatus();
            }
            
            async function visualize() {
                const dataset = document.getElementById('dataset').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const regionType = document.getElementById('regionType').value;
                const regionName = document.getElementById('regionName').value;
                
                if (!dataset || !regionType || !regionName) {
                    document.getElementById('result').innerHTML = `
                        <div class="result error">Please complete all required fields</div>
                    `;
                    return;
                }
                
                showLoading('Generating visualization...');
                
                try {
                    const response = await fetch('/visualize', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            dataset, start_date: startDate, end_date: endDate,
                            region_type: regionType, region_name: regionName
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('previewContent').innerHTML = `
                            <div class="preview-content">
                                <h3>Visualization Preview</h3>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <strong>Type</strong>
                                        <span>Map Tiles</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Bands</strong>
                                        <span>${result.vis_params.bands ? result.vis_params.bands.join(', ') : 'Default'}</span>
                                    </div>
                                </div>
                                <details>
                                    <summary>Visualization Parameters</summary>
                                    <pre>${JSON.stringify(result.vis_params, null, 2)}</pre>
                                </details>
                                <p style="margin-top: 1rem;">
                                    <a href="${result.tile_url}" target="_blank" 
                                       style="color: #1a1a1a; font-weight: 500;">
                                        View Map Tiles →
                                    </a>
                                </p>
                            </div>
                        `;
                    } else {
                        document.getElementById('previewContent').innerHTML = `
                            <div class="result error">Visualization Error: ${result.error}</div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('previewContent').innerHTML = `
                        <div class="result error">Network Error: ${error.message}</div>
                    `;
                }
            }

            let drawMap = null;
            let drawnItems = null;

            function initDrawMap() {
                if (drawMap) {
                    drawMap.remove();
                }
                
                // Initialize map
                drawMap = L.map('mapContainer').setView([20, 0], 2);
                
                // Add base layer
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(drawMap);
                
                // Initialize draw controls
                drawnItems = new L.FeatureGroup();
                drawMap.addLayer(drawnItems);
                
                const drawControl = new L.Control.Draw({
                    draw: {
                        polygon: {
                            allowIntersection: false,
                            shapeOptions: {
                                color: '#1a1a1a'
                            }
                        },
                        rectangle: {
                            shapeOptions: {
                                color: '#1a1a1a'
                            }
                        },
                        circle: false,
                        circlemarker: false,
                        marker: false,
                        polyline: false
                    },
                    edit: {
                        featureGroup: drawnItems,
                        remove: true
                    }
                });
                
                drawMap.addControl(drawControl);
                
                // Handle drawn shapes
                drawMap.on(L.Draw.Event.CREATED, function(event) {
                    const layer = event.layer;
                    drawnItems.clearLayers();  // Clear previous drawings
                    drawnItems.addLayer(layer);
                    
                    // Convert to GeoJSON
                    const geoJson = layer.toGeoJSON();
                    window.customGeometry = geoJson.geometry;
                    
                    document.getElementById('drawInstructions').innerHTML = `
                        <div style="background: #d1fae5; padding: 0.75rem; border-radius: 4px;">
                            <strong>✓ Region drawn successfully</strong><br>
                            <small>You can edit or delete the shape using the tools above</small>
                        </div>
                    `;
                });
                
                document.getElementById('drawInstructions').innerHTML = `
                    <div style="background: #dbeafe; padding: 0.75rem; border-radius: 4px;">
                        Use the drawing tools in the top-left corner to draw a polygon or rectangle on the map
                    </div>
                `;
            }
            
            function downloadBase64File(base64Data, filename) {
                try {
                    const byteCharacters = atob(base64Data);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {type: 'image/tiff'});
                    
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } catch (error) {
                    console.error('Download failed:', error);
                    alert('Download failed. Please try again.');
                }
            }
        </script>
    </body>
    </html>
    """)

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