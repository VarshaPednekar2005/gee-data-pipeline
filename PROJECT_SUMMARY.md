# GEE Data Pipeline Project

## What This Project Does
FastAPI web application that downloads satellite data from Google Earth Engine (GEE) directly to your browser with an integrated frontend interface.

## Architecture Overview

### Single-File Design
- **Main File**: `clean_downloader.py` contains both backend API and frontend HTML/CSS/JS
- **Authentication**: Service account with JSON key (no manual login required)
- **Processing**: Server-side GEE queries with direct browser downloads

## How Backend Queries Work

### 1. Data Collection Query Flow
```python
# Step 1: Initialize GEE with service account
credentials = ee.ServiceAccountCredentials(email, key_file)
ee.Initialize(credentials)

# Step 2: Get region geometry
region = get_region_geometry(region_type, region_name)

# Step 3: Filter dataset by region and date
collection = ee.ImageCollection(dataset_id)
    .filterBounds(region)
    .filterDate(start_date, end_date)
```

### 2. Three Main API Endpoints

#### `/preview` - Data Analysis
```python
# Gets collection metadata
info = collection.getInfo()
bands = image.bandNames().getInfo()
pixel_count = image.select(bands[0]).reduceRegion({
    'reducer': ee.Reducer.count(),
    'geometry': region,
    'scale': 30
}).getInfo()
```

#### `/visualize` - Map Display  
```python
# Creates visualization parameters
vis_params = get_visualization_params(dataset_id, bands)
# Generates map tiles for web display
map_id = image.getMapId(vis_params)
```

#### `/download` - Data Export
```python
# For GeoTIFF export
image = collection.mean().clip(region)
download_url = image.getDownloadURL({
    'scale': scale,
    'crs': 'EPSG:4326',
    'format': 'GEO_TIFF'
})

# For CSV export  
samples = image.sample({
    'region': region,
    'scale': scale,
    'numPixels': 5000
})
```

### 3. Region Processing
```python
def get_region_geometry(region_type, region_name):
    if region_type == "country":
        return ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
            .filter(ee.Filter.eq('country_na', region_name))
    elif region_type == "state":
        return ee.FeatureCollection("FAO/GAUL/2015/level1")
            .filter(ee.Filter.eq('ADM1_NAME', region_name))
```

## Key Features

### Data Selection Interface
- **Region Selection**: Country, State, or Continent dropdown
- **Dataset Input**: Any GEE dataset ID (MODIS, Landsat, Sentinel, CHIRPS)
- **Date Range**: Start and end date pickers
- **Export Format**: GeoTIFF (raster) or CSV (tabular)
- **Band Selection**: Choose specific bands to download

### Processing Pipeline
1. **Frontend**: User selects parameters via web form
2. **Backend**: FastAPI receives request and validates inputs
3. **GEE Query**: Server queries Google Earth Engine API
4. **Processing**: GEE processes data in cloud (filtering, clipping, aggregation)
5. **Download**: Direct download URL generated and returned to browser

## File Structure
```
gee-data-pipeline/
├── clean_downloader.py          # Main FastAPI app (backend + frontend)
├── plucky-sight-423703-k5-*.json # GEE service account credentials
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── venv/                       # Virtual environment
└── README.md                   # Documentation
```

## Usage
```bash
# Start server
cd /home/varshapednekar/projects/gee-data-pipeline
source venv/bin/activate
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000

# Access web interface
http://127.0.0.1:8000
```

## Supported Datasets
- **MODIS**: MOD11A1 (temperature), MOD13Q1 (vegetation)
- **Landsat**: LANDSAT/LC08/C02/T1_L2, LANDSAT/LE07/C02/T1_L2
- **Sentinel**: COPERNICUS/S2_SR_HARMONIZED, COPERNICUS/S1_GRD
- **Climate**: UCSB-CHG/CHIRPS/DAILY (precipitation)
- **Any GEE Dataset**: Enter dataset ID from GEE catalog

## Export Formats
- **GeoTIFF**: Spatial raster data for GIS analysis
- **CSV**: Point samples with coordinates for statistical analysis

## Working Directory
`/home/varshapednekar/projects/gee-data-pipeline`
