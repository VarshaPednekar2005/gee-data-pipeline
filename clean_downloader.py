from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import ee
from typing import Dict, Optional, List, Tuple

app = FastAPI()

# ==================== UNIVERSAL DATASET HANDLER ====================

class UniversalGEEHandler:
    """Handles ANY Google Earth Engine dataset with auto-detection"""
    
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
            
            # Get dataset description and metadata
            try:
                # Try to get collection info
                collection_info = collection.getInfo()
                description = collection_info.get('description', 'No description available')
                dataset_type_info = collection_info.get('type', 'ImageCollection')
            except:
                description = 'Auto-detected ImageCollection'
                dataset_type_info = 'ImageCollection'
            
            # Get date range if temporal
            date_range = None
            if has_time:
                try:
                    # Get first and last image dates
                    first_date = collection.limit(1).first().get('system:time_start')
                    last_date = collection.sort('system:time_start', False).limit(1).first().get('system:time_start')
                    
                    first_date_str = ee.Date(first_date).format('YYYY-MM-dd').getInfo()
                    last_date_str = ee.Date(last_date).format('YYYY-MM-dd').getInfo()
                    date_range = f"{first_date_str} to {last_date_str}"
                except:
                    date_range = "Available (dates vary by region)"
            
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
            
            # Check count
            try:
                count = collection.size().getInfo()
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
    try:
        key_file = 'plucky-sight-423703-k5-5965759cb7dc.json'
        service_account_email = 'gee-service-account@plucky-sight-423703-k5.iam.gserviceaccount.com'
        credentials = ee.ServiceAccountCredentials(service_account_email, key_file)
        ee.Initialize(credentials)
        return True
    except:
        return False

def get_region_geometry(region_type, region_name):
    try:
        if region_type == "country":
            return ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(ee.Filter.eq('country_na', region_name)).geometry()
        elif region_type == "state":
            return ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_NAME', region_name)).geometry()
        elif region_type == "continent":
            continent_countries = {
                "Asia": ["China", "India", "Indonesia", "Pakistan", "Bangladesh", "Japan", "Philippines", "Vietnam", "Turkey", "Iran"],
                "Europe": ["Russia", "Germany", "United Kingdom", "France", "Italy", "Spain", "Ukraine", "Poland", "Romania", "Netherlands"],
                "Africa": ["Nigeria", "Ethiopia", "Egypt", "South Africa", "Kenya", "Uganda", "Algeria", "Sudan", "Morocco", "Angola"],
                "North America": ["United States", "Mexico", "Canada", "Guatemala", "Cuba", "Haiti", "Dominican Republic", "Honduras", "Nicaragua", "Costa Rica"],
                "South America": ["Brazil", "Colombia", "Argentina", "Peru", "Venezuela", "Chile", "Ecuador", "Bolivia", "Paraguay", "Uruguay"],
                "Oceania": ["Australia", "Papua New Guinea", "New Zealand", "Fiji", "Solomon Islands", "Vanuatu", "Samoa", "Kiribati", "Tonga", "Palau"]
            }
            if region_name in continent_countries:
                return ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(
                    ee.Filter.inList('country_na', continent_countries[region_name])
                ).geometry()
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
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="regionType">Region Type</label>
                        <select id="regionType" onchange="updateRegionOptions()">
                            <option value="">Select Type</option>
                            <option value="country">Country</option>
                            <option value="state">State/Province</option>
                            <option value="continent">Continent</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="regionName">Region Name</label>
                        <select id="regionName" disabled>
                            <option value="">Select Region</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="exportFormat">Export Format</label>
                    <select id="exportFormat">
                        <option value="GeoTIFF">GeoTIFF (Raster)</option>
                        <option value="CSV">CSV (100 samples)</option>
                        <option value="JSON">JSON (Metadata)</option>
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
        
        <script>
            const regions = {
                country: ["United States", "China", "India", "Brazil", "Russia", "Canada", "Australia", "Germany", "United Kingdom", "France", "Italy", "Spain", "Mexico", "Japan", "South Africa", "Nigeria", "Egypt", "Turkey", "Iran", "Pakistan"],
                state: ["California", "Texas", "Florida", "New York", "Pennsylvania", "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan", "Maharashtra", "Uttar Pradesh", "Bihar", "West Bengal", "Madhya Pradesh", "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh"],
                continent: ["Asia", "Europe", "Africa", "North America", "South America", "Oceania"]
            };
            
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
                const regionName = document.getElementById('regionName').value;
                
                if (!dataset || !regionType || !regionName) {
                    document.getElementById('result').innerHTML = `
                        <div class="result error">Please complete all required fields</div>
                    `;
                    return;
                }
                
                showLoading('Analyzing dataset...');
                
                try {
                    const response = await fetch('/preview', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            dataset, start_date: startDate, end_date: endDate,
                            region_type: regionType, region_name: regionName
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        // Store band details globally for showAllBands function
                        window.currentBandDetails = result.band_details || result.bands.map(b => ({name: b, data_type: 'N/A', scale: 'N/A', crs: 'N/A'}));
                        
                        const optimizedBadge = '<span class="badge auto">⚡ Auto-detected</span>';
                        
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
                        
                        // Date information
                        let dateInfo = '';
                        if (result.date_range) {
                            dateInfo = `<div style="background: #e8f4fd; padding: 0.75rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid #1976d2;">
                                <strong style="font-size: 0.85rem;">📅 Temporal Dataset</strong>
                                <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; color: #666;">Available: ${result.date_range}</p>
                            </div>`;
                        } else if (result.image_date) {
                            dateInfo = `<div style="background: #f3e5f5; padding: 0.75rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid #7b1fa2;">
                                <strong style="font-size: 0.85rem;">📷 Single Image</strong>
                                <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; color: #666;">Date: ${result.image_date}</p>
                            </div>`;
                        }
                        
                        // Sample image display
                        let sampleImageDisplay = '';
                        if (result.sample_image_url) {
                            sampleImageDisplay = `
                                <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; margin: 1rem 0; border: 1px solid #e9ecef;">
                                    <h4 style="margin-bottom: 0.75rem; color: #666; font-size: 0.85rem;">🖼️ SAMPLE PREVIEW</h4>
                                    <div style="text-align: center;">
                                        <img src="${result.sample_image_url.replace('{z}/{x}/{y}', '8/128/128')}" 
                                             style="max-width: 200px; border-radius: 4px; border: 1px solid #ddd;"
                                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                                        <div style="display: none; padding: 2rem; color: #666; font-size: 0.8rem;">
                                            Preview not available for this dataset
                                        </div>
                                    </div>
                                    <p style="font-size: 0.75rem; color: #666; margin-top: 0.5rem; text-align: center;">
                                        Sample visualization from dataset center
                                    </p>
                                </div>`;
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
                        
                        const imageCountInfo = result.image_count > 1 ? 
                            `<div style="background: #fff3cd; padding: 0.75rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid #ffc107;">
                                <strong style="font-size: 0.85rem;">📊 ${result.image_count} images found</strong>
                                <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; color: #666;">Will be combined using ${result.composite_method} method</p>
                            </div>` : '';
                        
                        // Disable download button if file is too large
                        const downloadButton = result.size_warning && result.size_warning.type === 'size_limit' 
                            ? `<button class="btn-secondary" disabled style="opacity: 0.6; cursor: not-allowed;">Download Unavailable (File Too Large)</button>`
                            : `<button class="btn-primary" onclick="confirmDownload()">Download Dataset</button>`;
                        
                        document.getElementById('previewContent').innerHTML = `
                            <div class="preview-content">
                                <h3 style="margin-bottom: 0.5rem;">
                                    ${result.dataset_name || dataset}
                                    ${optimizedBadge}
                                </h3>
                                <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.4;">
                                    ${result.description}
                                </p>
                                
                                ${dateInfo}
                                ${sizeWarningDisplay}
                                ${sampleImageDisplay}
                                
                                <div class="info-grid">
                                    <div class="info-item">
                                        <strong>Dataset Type</strong>
                                        <span>${result.dataset_type_info}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Region</strong>
                                        <span>${regionName}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Images Found</strong>
                                        <span>${result.image_count}</span>
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
                                        <strong>File Size</strong>
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
                                
                                ${imageCountInfo}
                                
                                <div style="background: #f0f9ff; padding: 1rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid #0ea5e9;">
                                    <strong style="font-size: 0.85rem;">📦 What You'll Download:</strong>
                                    <ul style="margin: 0.5rem 0 0 1.25rem; font-size: 0.85rem; color: #666;">
                                        <li><strong>Format:</strong> Multi-band GeoTIFF file</li>
                                        <li><strong>Resolution:</strong> ${result.native_resolution} (auto-detected)</li>
                                        <li><strong>Bands:</strong> All ${result.bands.length} bands included</li>
                                        ${result.composite_method ? `<li><strong>Processing:</strong> ${result.composite_method} composite from ${result.image_count} images</li>` : ''}
                                    </ul>
                                </div>
                                
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
            
            async function confirmDownload() {
                const dataset = document.getElementById('dataset').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const regionType = document.getElementById('regionType').value;
                const regionName = document.getElementById('regionName').value;
                const exportFormat = document.getElementById('exportFormat').value;
                
                showLoading('Processing download...');
                
                try {
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            dataset, start_date: startDate, end_date: endDate,
                            region_type: regionType, region_name: regionName, 
                            export_format: exportFormat
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const filename = result.filename || 'gee_download';
                        const extension = result.format === 'CSV' ? '.csv' : '.tif';
                        document.getElementById('previewContent').innerHTML = `
                            <div class="preview-content">
                                <div class="result">
                                    <h3>Download Ready</h3>
                                    <p>Your ${result.format} file is ready for download.</p>
                                    <a href="${result.download_url}" download="${filename}${extension}" 
                                       style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; 
                                              background: #1a1a1a; color: white; text-decoration: none; 
                                              border-radius: 6px; font-weight: 500;">
                                        Download ${result.format}
                                    </a>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('previewContent').innerHTML = `
                            <div class="result error">Download Error: ${result.error}</div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('previewContent').innerHTML = `
                        <div class="result error">Network Error: ${error.message}</div>
                    `;
                }
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

def get_resolution_suggestions(dataset_id, native_scale):
    """Removed - will implement later if needed"""
    return None

@app.post("/preview")
async def preview_download(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        dataset_id = request['dataset']
        
        # Get smart configuration (auto-detected only)
        config = handler.get_config(dataset_id=dataset_id)
        
        # Get region
        region = get_region_geometry(request['region_type'], request['region_name'])
        if not region:
            return {"success": False, "error": "Region not found"}
        
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
        
        # Calculate area and file size with proper validation
        area_km2 = region.area().divide(1000000).getInfo()
        scale = config['scale']
        pixels_per_km2 = 1000000 / (scale * scale)
        estimated_pixels = area_km2 * pixels_per_km2 * len(config['bands'])
        estimated_mb = (estimated_pixels * 4) / (1024 * 1024)
        
        # Size validation and warnings
        size_warning = None
        size_str = f"{estimated_mb:.1f} MB"
        
        if estimated_mb > 1024:
            size_str = f"{estimated_mb/1024:.1f} GB"
            
        if estimated_mb > 32:
            size_warning = {
                "type": "size_limit",
                "message": f"File size ({size_str}) exceeds GEE's 32MB direct download limit",
                "suggestions": [
                    "Choose a smaller region",
                    "Use coarser resolution (if available)",
                    "Export to Google Drive (not implemented yet)"
                ]
            }
        elif estimated_mb > 16:
            size_warning = {
                "type": "size_caution", 
                "message": f"Large file size ({size_str}) - download may be slow",
                "suggestions": ["Consider smaller region for faster download"]
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
            "export_resolution": f"{config['scale']}m",  # Same as native since no user override
            "estimated_size": size_str,
            "size_warning": size_warning,
            "area_km2": f"{area_km2:.1f}",
            "composite_method": config['composite_method'],
            "requires_date": config['requires_date'],
            "date_range": detected_info.get('date_range'),
            "image_date": detected_info.get('image_date'),
            "sample_image_url": sample_image_url,
            "dataset_type_info": detected_info.get('dataset_type_info', config['type'])
        }
        
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

@app.post("/download")
async def download(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        dataset_id = request['dataset']
        config = handler.get_config(dataset_id)
        export_format = request.get('export_format', 'GeoTIFF')
        
        # Use auto-detected scale (no user override)
        scale = config['scale']
        
        # Validate format compatibility
        if export_format == 'CSV' and config['type'] == 'ImageCollection':
            return {
                "success": False, 
                "error": "CSV format not suitable for ImageCollections with multiple images. Use GeoTIFF instead.",
                "suggestion": "CSV works better for single images or point sampling. For weather/time-series data like this, use GeoTIFF format."
            }
        
        region = get_region_geometry(request['region_type'], request['region_name'])
        if not region:
            return {"success": False, "error": "Region not found"}
        
        # Process dataset
        image, count = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=request.get('start_date'),
            end_date=request.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {"success": False, "error": "No images found"}
        
        # Create filename
        dataset_clean = dataset_id.replace('/', '_').replace(' ', '_')
        region_clean = request['region_name'].replace(' ', '_')
        date_str = f"{request.get('start_date', 'nodate')}_{request.get('end_date', 'nodate')}"
        filename = f"{dataset_clean}_{region_clean}_{date_str}"
        
        # Handle different export formats
        if export_format == 'CSV':
            # CSV: Sample points only (not suitable for full imagery)
            points = ee.FeatureCollection.randomPoints(region, 100)
            samples = image.sampleRegions(
                collection=points,
                scale=scale,
                geometries=True
            )
            url = samples.getDownloadURL('CSV')
            file_ext = '.csv'
            
        elif export_format == 'JSON':
            # JSON: Export metadata/statistics
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    reducer2=ee.Reducer.minMax(),
                    sharedInputs=True
                ),
                geometry=region,
                scale=scale,
                maxPixels=1e9
            ).getInfo()
            
            return {
                "success": True,
                "format": "JSON",
                "data": stats,
                "filename": filename
            }
            
        else:  # GeoTIFF (default)
            # Validate: Check if size is reasonable
            area_km2 = region.area().divide(1000000).getInfo()
            pixels_per_km2 = 1000000 / (scale * scale)
            total_pixels = area_km2 * pixels_per_km2
            
            # GEE has a 32MB limit for direct download via getDownloadURL
            estimated_mb = (total_pixels * len(config['bands']) * 4) / (1024 * 1024)
            
            if estimated_mb > 32:
                return {
                    "success": False,
                    "error": f"File too large ({estimated_mb:.1f}MB) for direct download. GEE limit is 32MB. Try: (1) Smaller region, (2) Coarser resolution, or (3) Export to Google Drive instead."
                }
            
            url = image.getDownloadURL({
                'scale': scale,
                'region': region,
                'format': 'GEO_TIFF'
            })
            file_ext = '.tif'
        
        return {
            "success": True,
            "download_url": url,
            "format": export_format,
            "filename": filename + file_ext
        }
        
    except Exception as e:
        return {"success": False, "error": f"Download failed: {str(e)}"}