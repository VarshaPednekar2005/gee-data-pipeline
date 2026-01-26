# GEE Data Pipeline

A FastAPI web application that provides universal access to Google Earth Engine satellite data through automated detection and processing. Single interface for downloading any GEE dataset with zero configuration required.

## Project Overview

### What This System Does
- **Universal Dataset Access**: Works with ANY Google Earth Engine dataset (1000+ available)
- **Auto-Detection**: Automatically detects dataset type, bands, resolution, and temporal properties
- **Direct Downloads**: Processes satellite data on Google's infrastructure, downloads to browser
- **Zero Configuration**: No hardcoded dataset parameters or manual setup needed

### Architecture
**Three-Tier Processing System:**
1. **Frontend (Browser)**: Web interface for dataset selection and parameter input
2. **Backend (FastAPI)**: Query orchestration and API management  
3. **Processing (Google Earth Engine)**: Distributed satellite data processing on Google's cloud infrastructure

## Technical Deep Dive

### 1. Authentication & GEE Connection

#### Service Account Setup:
```python
import ee
import json

# Load service account credentials
with open('plucky-sight-423703-k5-5965759cb7dc.json', 'r') as f:
    key_data = json.load(f)

# Initialize Earth Engine with service account
credentials = ee.ServiceAccountCredentials(
    email=key_data['client_email'],
    key_file='plucky-sight-423703-k5-5965759cb7dc.json'
)
ee.Initialize(credentials)
```

**Authentication Flow:**
- **Service Account**: Uses Google Cloud service account (no user login required)
- **JSON Key File**: Contains private key and client credentials
- **Automatic Authentication**: Application authenticates on startup
- **API Access**: Enables programmatic access to GEE's full catalog

#### Connection Verification:
```python
# Test GEE connection
try:
    # Simple test query to verify connection
    test_image = ee.Image("USGS/SRTMGL1_003")
    info = test_image.getInfo()
    print("✓ GEE connection successful")
except Exception as e:
    print(f"✗ GEE connection failed: {e}")
```

### 2. Universal Dataset Detection (Core Innovation)

```python
def detect_dataset_type(self, dataset_id: str):
    try:
        # Try ImageCollection first (most datasets are time-series)
        collection = ee.ImageCollection(dataset_id)
        first_image = collection.limit(1).first()
        info = first_image.getInfo()  # Gets ALL metadata from GEE
        
        # Auto-extract everything:
        bands = [b['id'] for b in info['bands']]  # All available bands
        scale = proj.nominalScale().getInfo()     # Native resolution
        has_time = 'system:time_start' in properties  # Temporal dataset?
        
        return {"type": "ImageCollection", "bands": bands, "scale": scale}
    except:
        # Fall back to single Image if ImageCollection fails
        image = ee.Image(dataset_id)
        # Same detection process for single images
```

**Why This Works for ANY Dataset:**
- No hardcoded configurations needed
- Automatically detects ImageCollection vs Image
- Extracts all metadata directly from GEE's catalog
- Works with 1000+ different satellite datasets

### 3. Query Execution Architecture

#### Client-Server-GEE Flow:

```python
# 1. USER BROWSER → YOUR SERVER
# User submits form with dataset ID, dates, region

# 2. YOUR FASTAPI SERVER (Query Building)
@app.post("/download")
async def download_data(request: dict):
    # Build query instructions locally
    collection = ee.ImageCollection(dataset_id)
    collection = collection.filterDate(start_date, end_date)
    collection = collection.filterBounds(region)
    image = collection.median()  # Query built, not executed yet
    
    # 3. GOOGLE EARTH ENGINE SERVERS (Actual Processing)
    url = image.getDownloadURL({
        'scale': scale,
        'region': region,
        'format': 'GEO_TIFF'
    })  # ← This triggers distributed processing on Google's infrastructure
```

#### What Happens on Google's Infrastructure:

1. **Query Reception**: Google receives your Earth Engine API call
2. **Distributed Processing**: 
   - Query distributed across Google's data centers
   - Parallel processing on thousands of servers with GPUs
   - Accesses pre-indexed satellite imagery catalog (80+ petabytes)
3. **Data Processing**:
   - Filters imagery by date/region from global catalog
   - Applies median reduction across time series (removes clouds/noise)
   - Clips to exact geographic boundaries
   - Converts to requested format (multi-band GeoTIFF)
4. **Result Generation**: Creates temporary download URL for processed file

### 4. Processing Implementation

#### Image vs ImageCollection Handling:
```python
if config['type'] == 'ImageCollection':
    # Time-series data (Landsat, Sentinel, MODIS)
    collection = ee.ImageCollection(dataset_id)
    if config['requires_date']:
        collection = collection.filterDate(start_date, end_date)
    collection = collection.filterBounds(region)
    image = collection.median()  # Reduce multiple images to single composite
else:
    # Single snapshot (DEM, land cover maps)
    image = ee.Image(dataset_id).clip(region)
```

#### Temporal Reduction (Currently Fixed to Median):
```python
# Current implementation uses median reduction
image = collection.median()  # Removes clouds and noise effectively

# Could be enhanced to offer user choice:
# collection.mean()   # Average values
# collection.first()  # Most recent image
# collection.max()    # Maximum values
```

#### Band Selection (Automatic):
```python
# System automatically includes ALL available bands
all_bands = image.bandNames().getInfo()  # ['B1', 'B2', 'B3', 'B4', ...]
# Downloads as single multi-band GeoTIFF file
# Each band becomes separate layer in the file
```

### 5. Resolution Handling

#### Auto-Detection (Default):
```python
# System detects native resolution automatically
proj = first_image.select(band_names[0]).projection()
scale = proj.nominalScale().getInfo()  # 30m for Landsat, 10m for Sentinel-2
```

#### Manual Override (Optional):
```python
export_params = {
    'scale': user_specified_scale or auto_detected_scale,
    'region': region,
    'format': 'GEO_TIFF'
}
```

**When to specify custom resolution:**
- **Smaller files**: Use 1000m instead of 30m (downsampling)
- **Higher detail**: Use 10m instead of 30m (limited by native resolution)
- **File size limits**: GEE has 32MB direct download limit

### 6. API Endpoints

#### `/preview` - Dataset Analysis
```python
# Auto-detect dataset characteristics
config = handler.get_config(dataset_id)

# Process with smart defaults
image, count = handler.process_dataset(
    dataset_id=dataset_id,
    start_date=start_date,
    end_date=end_date,
    region=region,
    config=config
)

# Return: bands, resolution, file size, image count
```

#### `/download` - Data Export
```python
# Same processing pipeline as preview
image, count = handler.process_dataset(...)

# Export based on format
if export_format == 'GeoTIFF':
    url = image.getDownloadURL({
        'scale': scale,           # Auto-detected or user-specified
        'region': region,         # User-selected area
        'format': 'GEO_TIFF'     # Multi-band raster
    })
elif export_format == 'CSV':
    # Sample random points for tabular data
    points = ee.FeatureCollection.randomPoints(region, 100)
    samples = image.sampleRegions(collection=points, scale=scale)
    url = samples.getDownloadURL('CSV')
```

#### `/visualize` - Map Display
```python
# Creates visualization parameters
vis_params = get_visualization_params(dataset_id, bands)
# Generates map tiles for web display
map_id = image.getMapId(vis_params)
```

### 7. Google Earth Engine Infrastructure

#### Technical Specifications:
- **Data Volume**: 80+ petabytes of Earth observation data
- **Processing Power**: Distributed GPU clusters across global data centers
- **Coverage**: 40+ years of satellite imagery (Landsat since 1972)
- **Updates**: Real-time ingestion of new satellite acquisitions
- **Global Access**: Sub-second query response times worldwide

#### Processing Optimizations:
- Pre-indexed spatial data (no full dataset scanning)
- Pyramid storage (multiple resolutions pre-computed)
- Chunked processing (data split into manageable tiles)
- Query result caching for common requests

### 8. Cost Structure

#### Google Earth Engine Pricing (2024):

**Commercial Use:**
- Compute: $0.20 per 1,000 compute units
- Storage: $0.20 per GB-month for private assets
- Egress: $0.12 per GB for downloads

**Academic/Research:**
- FREE for non-commercial research
- Educational institutions get complimentary access

#### Typical Download Costs:
```python
# Example: 100km² region, 30m resolution, 10 bands, median of 50 images
# Compute: ~5-10 compute units = $0.001-0.002
# Download: ~50MB file = $0.006
# Total per download: ~$0.007-0.008 (under 1 cent)
```

## Key Technical Advantages

**No Local Processing:**
- Zero satellite data storage on your servers
- Leverage Google's petabyte-scale infrastructure
- Process terabytes in seconds without expensive hardware

**Universal Compatibility:**
- Single codebase works with ANY GEE dataset
- Auto-detection eliminates manual configuration
- Supports 1000+ different satellite data products

**Scalability:**
- Google handles concurrent users globally
- No server hardware limitations
- Distributed processing across data centers

**Real-time Access:**
- Immediate access to latest satellite acquisitions
- No data synchronization delays
- Global coverage with consistent performance

## Current Implementation

### Features
- **Reduction Method**: Fixed to median (optimal for cloud removal)
- **Band Selection**: Automatically includes all available bands
- **Resolution**: Auto-detected from dataset metadata with manual override option
- **Export Format**: Multi-band GeoTIFF files
- **Region Selection**: Country, State, or Continent dropdown
- **Authentication**: Service account with JSON key (no manual login required)

### Supported Datasets
- **MODIS**: MOD11A1 (temperature), MOD13Q1 (vegetation)
- **Landsat**: LANDSAT/LC08/C02/T1_L2, LANDSAT/LE07/C02/T1_L2
- **Sentinel**: COPERNICUS/S2_SR_HARMONIZED, COPERNICUS/S1_GRD
- **Climate**: UCSB-CHG/CHIRPS/DAILY (precipitation)
- **Any GEE Dataset**: Enter dataset ID from GEE catalog

### File Structure
```
gee-data-pipeline/
├── clean_downloader.py          # Main FastAPI app (backend + frontend)
├── plucky-sight-423703-k5-*.json # GEE service account credentials
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── venv/                       # Virtual environment
└── images/                     # Screenshots
```

## Setup and Usage

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source venv/bin/activate

# Run the web application
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000

# Access the web interface
http://127.0.0.1:8000
```

### Authentication
```python
# Initialize GEE with service account
credentials = ee.ServiceAccountCredentials(email, key_file)
ee.Initialize(credentials)
```

## Enhancement Opportunities

- User-selectable reduction methods (median, mean, first, max)
- Custom band selection interface
- Google Drive export for large files (>32MB)
- Batch processing capabilities
- Advanced visualization options

## Screenshots

### Main Interface
![Main Interface](images/main.png)

### Output Received
![Output Received](images/outputreceived.png)

## Interview Key Points

### Technical Innovation
- **Universal Dataset Handler**: Single codebase works with ANY Google Earth Engine dataset
- **Auto-Detection**: Automatically detects dataset type, bands, resolution, and temporal properties
- **Zero Configuration**: No hardcoded dataset parameters needed

### Architecture Benefits
- **Distributed Processing**: Leverages Google's petabyte-scale infrastructure
- **Cost Effective**: Sub-penny costs per download, free for academic use
- **Scalable**: No server hardware limitations, global availability
- **Real-time**: Process terabytes in seconds using Google's distributed computing
