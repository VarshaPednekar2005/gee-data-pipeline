# GEE Data Pipeline

A FastAPI web application that provides universal access to Google Earth Engine satellite data through automated detection and processing. Single interface for downloading any GEE dataset with zero configuration required.

## Project Overview

### What This System Does
- **Universal Dataset Access**: Works with ANY Google Earth Engine dataset (1000+ available)
- **Auto-Detection**: Automatically detects dataset type, bands, resolution, and temporal properties
- **Smart Downloads**: Small files (<10MB) download directly, large files export to Google Drive
- **Zero Configuration**: No hardcoded dataset parameters or manual setup needed

### Architecture
**Three-Tier Processing System:**
1. **Frontend (Browser)**: Web interface for dataset selection and parameter input
2. **Backend (FastAPI)**: Query orchestration and API management  
3. **Processing (Google Earth Engine)**: Distributed satellite data processing on Google's cloud infrastructure

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Authentication (One-time only)

#### Method 1: Automatic Setup Script (Easiest):
```bash
# Activate virtual environment
source venv/bin/activate

# Run the complete setup script (handles everything automatically)
python3 setup_oauth.py
```

#### Method 2: Manual Setup (What we actually did):
```bash
# Activate virtual environment
source venv/bin/activate

# First we tried this command
earthengine authenticate
```

**What happened with earthengine authenticate:**
1. **Copy the URL** shown in terminal and open in browser
2. **Sign in** with your Google account
3. **Grant all permissions** (Earth Engine, Drive, Cloud Platform)
4. **Browser redirects to localhost:8085** with a code (connection will fail - that's normal)
5. **Terminal doesn't detect automatically** - gets stuck waiting

**Then we used this command that actually worked:**
```bash
# This command worked automatically
python3 -c "import ee; ee.Authenticate(force=True)"
```

**What happened:**
1. **Copy the URL** shown in terminal and open in browser
2. **Sign in** with your Google account
3. **Grant all permissions** (Earth Engine, Drive, Cloud Platform)
4. **Browser redirects to localhost:8085** with a code (connection will fail - that's normal)
5. **Terminal automatically detects the code** and completes authentication
6. **You see "Successfully saved authorization token"**

**If the python command also gets stuck:**
- Use the setup script that handles manual code extraction:
```bash
python3 setup_oauth.py
```
- This is a backup solution for cases where automatic detection fails

**Benefits of OAuth:**
- ✅ **Completely FREE** - no payment required
- ✅ **Unlimited Google Drive exports** for large files
- ✅ **No file size restrictions**
- ✅ **One-time setup** - credentials saved permanently

#### Alternative: Service Account (Limited):
If OAuth fails, the system automatically falls back to service account with limited capabilities.

### 3. Run the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start the web server
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000

# Access the web interface
# Open: http://127.0.0.1:8000
```

## How It Works

### Download Logic
- **Small files (<10MB)**: Direct download to your computer
- **Large files (>10MB)**: Export to your Google Drive folder "EarthEngineExports"

### Authentication Status
- **With OAuth**: `✅ GEE initialized with OAuth (FREE Google Drive access available)`
- **Service Account**: `⚠️ OAuth not set up, using service account (no Drive access)`

## Technical Deep Dive

### 1. Authentication & GEE Connection

#### OAuth Setup (Recommended):
```python
import ee
# One-time setup
ee.Authenticate(force=True)
ee.Initialize(project='plucky-sight-423703-k5')
```

**Authentication Flow:**
- **OAuth**: Uses your personal Google account (FREE Google Drive access)
- **Service Account**: Fallback with limited capabilities
- **Automatic Detection**: Application tries OAuth first, falls back to service account

#### Connection Verification:
```python
# Test GEE connection
try:
    ee.Initialize(project='plucky-sight-423703-k5')
    print("✓ GEE connection successful with Drive access")
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

### 3. Download Implementation

#### Small Files (Direct Download):
```python
if estimated_mb <= 10:
    url = image.getDownloadURL({
        'scale': scale,
        'region': region,
        'format': 'GEO_TIFF'
    })
    # Returns direct download URL
```

#### Large Files (Google Drive Export):
```python
if estimated_mb > 10:
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=filename,
        folder='EarthEngineExports',
        scale=scale,
        region=region,
        maxPixels=1e13,
        fileFormat='GeoTIFF'
    )
    task.start()
    # File appears in Google Drive after 5-30 minutes
```

### 4. API Endpoints

#### `/preview` - Dataset Analysis
```python
# Auto-detect dataset characteristics
config = handler.get_config(dataset_id)
# Return: bands, resolution, file size, image count
```

#### `/download` - Data Export
```python
# Size-based routing:
# Small files: Direct download URL
# Large files: Google Drive export task
```

## Supported Datasets

- **MODIS**: MOD11A1 (temperature), MOD13Q1 (vegetation)
- **Landsat**: LANDSAT/LC08/C02/T1_L2, LANDSAT/LE07/C02/T1_L2
- **Sentinel**: COPERNICUS/S2_SR_HARMONIZED, COPERNICUS/S1_GRD
- **Climate**: UCSB-CHG/CHIRPS/DAILY (precipitation)
- **Any GEE Dataset**: Enter dataset ID from GEE catalog

## File Structure
```
gee-data-pipeline/
├── clean_downloader.py          # Main FastAPI app (backend + frontend)
├── plucky-sight-423703-k5-*.json # GEE service account credentials
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── venv/                       # Virtual environment
└── README.md                   # This file
```

## Troubleshooting

### OAuth Authentication Issues
```bash
# If OAuth fails, try manual setup:
earthengine authenticate

# Or reset and try again:
python3 -c "import ee; ee.Authenticate(force=True)"
```

### Common Issues
- **"Service accounts do not have storage quota"**: OAuth not set up, run authentication
- **"File not available"**: Temporary download URL expired, regenerate
- **"Connection refused"**: Port 8000 in use, try different port or kill existing process

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

**Cost Effective:**
- OAuth authentication: **Completely FREE**
- Google Drive exports: **FREE** (15GB storage limit)
- Processing: Sub-penny costs per download

## Screenshots

### Main Interface
![Main Interface](images/main.png)

### Output Received
![Output Received](images/outputreceived.png)

## Interview Key Points

### Technical Innovation
- **Universal Dataset Handler**: Single codebase works with ANY Google Earth Engine dataset
- **Auto-Detection**: Automatically detects dataset type, bands, resolution, and temporal properties
- **Smart Routing**: Size-based download routing (direct vs Google Drive)

### Architecture Benefits
- **Distributed Processing**: Leverages Google's petabyte-scale infrastructure
- **Cost Effective**: FREE OAuth authentication, sub-penny processing costs
- **Scalable**: No server hardware limitations, global availability
- **Real-time**: Process terabytes in seconds using Google's distributed computing
