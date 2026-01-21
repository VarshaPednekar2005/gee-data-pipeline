from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import ee

app = FastAPI()

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
    """Get geometry for different region types"""
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
                countries = continent_countries[region_name]
                return ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(ee.Filter.inList('country_na', countries)).geometry()
        
        return None
    except Exception as e:
        print(f"Region geometry error: {e}")
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
                    <p>Satellite data processing platform</p>
                </div>
                
                <div class="form-group">
                    <label for="dataset">Dataset Collection</label>
                    <input type="text" id="dataset" placeholder="MODIS/061/MOD11A1" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="startDate">Start Date</label>
                        <input type="date" id="startDate" value="2023-01-01" required>
                    </div>
                    <div class="form-group">
                        <label for="endDate">End Date</label>
                        <input type="date" id="endDate" value="2023-01-31" required>
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
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="exportFormat">Export Format</label>
                        <select id="exportFormat">
                            <option value="GeoTIFF">GeoTIFF</option>
                            <option value="CSV">CSV</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="scale">Resolution (m)</label>
                        <input type="number" id="scale" value="1000" placeholder="1000">
                    </div>
                </div>
                
                <button class="btn-primary" onclick="preview()">Analyze Dataset</button>
                <button class="btn-secondary" onclick="visualize()">Generate Preview</button>
                
                <div id="result"></div>
            </div>
            
            <div class="preview-panel">
                <div class="preview-header">
                    <h2>Dataset Preview</h2>
                </div>
                
                <div id="previewContent">
                    <div class="empty-state">
                        <h3>No Dataset Selected</h3>
                        <p>Configure parameters and click "Analyze Dataset" to preview your data</p>
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
                const scale = document.getElementById('scale').value;
                
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
                            region_type: regionType, region_name: regionName, scale: parseInt(scale)
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        let bandDetails = '';
                        if (result.band_details) {
                            bandDetails = result.band_details.map(band => 
                                `<div class="band-item">
                                    <strong>${band.name}</strong><br>
                                    ${band.pixel_size_m}m | ${band.units} | ${band.crs}
                                </div>`
                            ).join('');
                        }
                        
                        document.getElementById('previewContent').innerHTML = `
                            <div class="preview-content">
                                <div class="info-grid">
                                    <div class="info-item">
                                        <strong>Dataset</strong>
                                        <span>${dataset}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Region</strong>
                                        <span>${regionName}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Images</strong>
                                        <span>${result.image_count}</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Area</strong>
                                        <span>${result.area_km2} km²</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Resolution</strong>
                                        <span>${scale}m</span>
                                    </div>
                                    <div class="info-item">
                                        <strong>Size</strong>
                                        <span>${result.estimated_size}</span>
                                    </div>
                                </div>
                                
                                <div class="bands-list">
                                    <h4>Bands (${result.bands.length})</h4>
                                    ${bandDetails || result.bands.map(b => `<div class="band-item">${b}</div>`).join('')}
                                </div>
                                
                                <button class="btn-primary" onclick="confirmDownload()">Download Dataset</button>
                                
                                <details>
                                    <summary>Technical Details</summary>
                                    <pre>${JSON.stringify(result.properties, null, 2)}</pre>
                                </details>
                            </div>
                        `;
                        document.getElementById('result').innerHTML = '';
                    } else {
                        document.getElementById('previewContent').innerHTML = `
                            <div class="result error">Analysis Error: ${result.error}</div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('previewContent').innerHTML = `
                        <div class="result error">Network Error: ${error.message}</div>
                    `;
                }
            }
            
            async function confirmDownload() {
                const dataset = document.getElementById('dataset').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const regionType = document.getElementById('regionType').value;
                const regionName = document.getElementById('regionName').value;
                const scale = document.getElementById('scale').value;
                const exportFormat = document.getElementById('exportFormat').value;
                
                showLoading('Processing download...');
                
                try {
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            dataset, start_date: startDate, end_date: endDate,
                            region_type: regionType, region_name: regionName, 
                            scale: parseInt(scale), export_format: exportFormat
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
                                    <summary>Parameters</summary>
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

@app.post("/preview")
async def preview_download(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        region = get_region_geometry(request['region_type'], request['region_name'])
        if not region:
            return {"success": False, "error": "Region not found"}
        
        collection = ee.ImageCollection(request['dataset'])
        if request['start_date'] and request['end_date']:
            collection = collection.filterDate(request['start_date'], request['end_date'])
        collection = collection.filterBounds(region)
        
        # Check if collection has any images
        image_count = collection.size().getInfo()
        if image_count == 0:
            return {"success": False, "error": f"No images found for {request['dataset']} in {request['region_name']} between {request['start_date']} and {request['end_date']}. Try a different date range or region."}
        
        # Get first image safely
        first_image = collection.first()
        bands = first_image.bandNames().getInfo()
        
        # Get detailed band information
        band_info = []
        for band in bands:
            try:
                band_data = first_image.select(band)
                projection = band_data.projection()
                pixel_size = projection.nominalScale().getInfo()
                
                band_info.append({
                    "name": band,
                    "pixel_size_m": pixel_size,
                    "units": "Unknown",
                    "crs": projection.crs().getInfo()
                })
            except:
                band_info.append({
                    "name": band,
                    "pixel_size_m": request['scale'],
                    "units": "Unknown",
                    "crs": "EPSG:4326"
                })
        
        # Get image properties
        try:
            properties = first_image.getInfo().get('properties', {})
        except:
            properties = {}
        
        # Estimate size
        area_km2 = region.area().divide(1000000).getInfo()
        pixels_per_km2 = (1000000 / (request['scale'] * request['scale']))
        estimated_pixels = area_km2 * pixels_per_km2 * len(bands)
        estimated_mb = (estimated_pixels * 4) / (1024 * 1024)
        
        size_str = f"{estimated_mb:.1f} MB" if estimated_mb < 1024 else f"{estimated_mb/1024:.1f} GB"
        
        return {
            "success": True,
            "image_count": image_count,
            "bands": bands,
            "band_details": band_info,
            "estimated_size": size_str,
            "area_km2": round(area_km2, 2),
            "properties": properties
        }
        
    except Exception as e:
        return {"success": False, "error": f"Analysis failed: {str(e)}"}

@app.post("/visualize")
async def visualize_data(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        region = get_region_geometry(request['region_type'], request['region_name'])
        collection = ee.ImageCollection(request['dataset'])
        if request['start_date'] and request['end_date']:
            collection = collection.filterDate(request['start_date'], request['end_date'])
        collection = collection.filterBounds(region)
        
        image = collection.first()
        
        # Get visualization parameters based on dataset
        vis_params = {}
        if 'MOD11A1' in request['dataset']:  # Temperature data
            vis_params = {'bands': ['LST_Day_1km'], 'min': 13000, 'max': 16000, 'palette': ['blue', 'cyan', 'yellow', 'red']}
        elif 'LANDSAT' in request['dataset']:  # Landsat data
            vis_params = {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 3000}
        elif 'S2' in request['dataset']:  # Sentinel-2
            vis_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
        else:
            # Default visualization
            bands = image.bandNames().getInfo()
            vis_params = {'bands': [bands[0]], 'min': 0, 'max': 1000}
        
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
        region = get_region_geometry(request['region_type'], request['region_name'])
        if not region:
            return {"success": False, "error": "Region not found"}
        
        collection = ee.ImageCollection(request['dataset'])
        if request['start_date'] and request['end_date']:
            collection = collection.filterDate(request['start_date'], request['end_date'])
        collection = collection.filterBounds(region)
        
        # Check if collection has images
        image_count = collection.size().getInfo()
        if image_count == 0:
            return {"success": False, "error": f"No images found for {request['dataset']} in {request['region_name']} between {request['start_date']} and {request['end_date']}"}
        
        # Get composite image (mean of collection)
        image = collection.mean()
        
        # Create filename
        dataset_clean = request['dataset'].replace('/', '_').replace(' ', '_')
        region_clean = request['region_name'].replace(' ', '_')
        filename = f"{dataset_clean}_{region_clean}_{request['start_date']}_{request['end_date']}"
        
        if request['export_format'] == 'CSV':
            # Create sample points for CSV export
            points = ee.FeatureCollection.randomPoints(region, 100)
            
            # Sample the image at points
            samples = image.sampleRegions(
                collection=points,
                scale=request['scale'],
                geometries=True
            )
            
            url = samples.getDownloadURL('CSV')
            
        else:
            # GeoTIFF download
            url = image.getDownloadURL({
                'scale': request['scale'],
                'region': region,
                'format': 'GEO_TIFF'
            })
        
        return {"success": True, "download_url": url, "format": request['export_format'], "filename": filename}
        
    except Exception as e:
        return {"success": False, "error": f"Download failed: {str(e)}"}
