# GEE Data Pipeline

A FastAPI web application for downloading satellite data from Google Earth Engine with an integrated frontend interface.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Run the web application:
```bash
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000
```

4. Access the web interface:
```
http://127.0.0.1:8000
```

## How The Code Actually Works

### 1. Universal Dataset Detection

The core magic happens in the `UniversalGEEHandler.detect_dataset_type()` method:

```python
def detect_dataset_type(self, dataset_id: str) -> Dict:
    # Try ImageCollection first (most datasets are collections)
    try:
        collection = ee.ImageCollection(dataset_id)
        first_image = collection.limit(1).first()
        info = first_image.getInfo()  # Gets ALL metadata from GEE
        
        # Extract everything automatically:
        bands = info['bands']                    # All band information
        properties = info.get('properties', {})  # Dataset properties
        band_names = [b['id'] for b in bands]    # Band names like ['B1', 'B2', ...]
        has_time = 'system:time_start' in properties  # Does it have dates?
        
        # Auto-detect native resolution from first band
        scale = abs(bands[0].get('crs_transform', [1000])[0])
        
        return {
            "type": "ImageCollection",
            "bands": band_names,           # ALL bands found
            "scale": scale,                # Native resolution
            "requires_date": has_time      # Whether dates are needed
        }
    except:
        # If ImageCollection fails, try as single Image
        image = ee.Image(dataset_id)
        # Same detection process...
```

**This single function works for ANY GEE dataset because:**
- It tries the most common type first (ImageCollection)
- Falls back to single Image if that fails
- Extracts ALL metadata automatically from GEE's own info
- No hardcoded dataset configurations needed

### 2. Resolution: Auto-Detection vs Manual Override

#### Auto-Detection (What Actually Happens)
```python
# From the code: gets resolution from band metadata
scale = abs(bands[0].get('crs_transform', [1000])[0])
if scale == 0 or scale > 100000:
    # Fallback: use GEE's nominal scale
    proj = first_image.select(band_names[0]).projection()
    scale = proj.nominalScale().getInfo()
```

**You DON'T need to specify resolution because:**
- GEE stores native resolution in each band's metadata
- Code extracts this automatically (30m for Landsat, 10m for Sentinel-2, etc.)
- Uses this as the default export resolution
- Shows you what it detected in the preview

#### Manual Override (Optional)
```python
# In the download endpoint:
export_params = {
    'scale': request.get('scale') or config['scale'],  # User value OR auto-detected
    'region': region,
    'format': 'GEO_TIFF'
}
```

**When to manually specify resolution:**
- **Smaller files**: Use 1000m instead of 30m (downsampling)
- **Larger detail**: Use 10m instead of 30m (limited by native resolution)
- **File size limits**: GEE has 32MB download limit, larger scale = smaller file

### 3. Band Selection: Why All Bands Are Included

#### The Code Reality
```python
# From process_dataset method:
all_bands = image.bandNames().getInfo()  # Gets ALL bands from the image

# Download includes everything:
url = image.getDownloadURL({
    'scale': scale,
    'region': region,
    'format': 'GEO_TIFF'  # Multi-band GeoTIFF with ALL bands
})
```

**You DON'T select individual bands because:**
- The code gets ALL available bands automatically
- Downloads them as a single multi-band GeoTIFF file
- Each band becomes a separate layer in the file
- This is simpler and ensures you don't miss important bands

### 4. Image Collection Reduction: Multiple Images → Single File

#### The Problem
```python
# ImageCollections contain many images over time:
collection = ee.ImageCollection("MODIS/061/MOD11A1")  # Could be 1000+ images
# Can't download 1000 separate files directly
```

#### The Solution
```python
# From process_dataset method:
if config['type'] == 'ImageCollection':
    collection = ee.ImageCollection(dataset_id)
    collection = collection.filterDate(start_date, end_date)  # Filter by time
    collection = collection.filterBounds(region)              # Filter by area
    
    # REDUCE to single composite image:
    if method == 'median':
        image = collection.median()    # Takes median of all images (reduces clouds)
    elif method == 'mean':
        image = collection.mean()      # Average of all images
    # Result: Single image representing the entire time period
```

**Why reduction is necessary:**
- ImageCollections have 100s-1000s of individual images
- You want one file, not 1000 separate downloads
- Compositing (median/mean) creates a single "best" image from the time series
- Median is good for removing clouds, mean for averaging values

### 5. The Complete Query Flow

#### Step 1: Auto-Detection (`/preview`)
```python
# User enters any dataset ID like "MODIS/061/MOD11A1"
config = handler.get_config(dataset_id)  # Auto-detects everything
# Returns: type, bands, resolution, whether dates are needed
```

#### Step 2: Processing (`/download`)
```python
# Apply filters based on what was detected:
if config['requires_date']:
    collection = collection.filterDate(start_date, end_date)
collection = collection.filterBounds(region)

# Reduce to single image:
image = collection.median().clip(region)

# Export with auto-detected or user-specified resolution:
url = image.getDownloadURL({
    'scale': user_scale or auto_detected_scale,
    'region': region,
    'format': 'GEO_TIFF'
})
```

### 6. Why This Works for ANY Dataset

The code is universal because:

1. **No hardcoded configurations** - everything is detected from GEE's metadata
2. **Tries both dataset types** - ImageCollection first, then Image
3. **Handles temporal data smartly** - only applies date filters if dataset has dates
4. **Uses GEE's own metadata** - resolution, bands, properties all come from GEE
5. **Graceful fallbacks** - if something fails, uses sensible defaults

### 7. File Size and Limitations

```python
# The code checks file size before download:
area_km2 = region.area().divide(1000000).getInfo()
pixels_per_km2 = 1000000 / (scale * scale)
estimated_mb = (area_km2 * pixels_per_km2 * len(bands) * 4) / (1024 * 1024)

if estimated_mb > 32:
    return {"error": "File too large for direct download. Try smaller region or coarser resolution."}
```

**GEE Limitations:**
- 32MB limit for direct downloads via `getDownloadURL()`
- Larger files need Google Drive export (not implemented in this code)
- Resolution vs file size tradeoff: finer resolution = larger files

## How It Works: Universal Dataset Handler

### Core Architecture: Single Query for Any Dataset

The application uses a **Universal GEE Handler** that can process ANY Google Earth Engine dataset through auto-detection:

```python
class UniversalGEEHandler:
    def detect_dataset_type(self, dataset_id: str) -> Dict:
        # Try ImageCollection first (most common)
        try:
            collection = ee.ImageCollection(dataset_id)
            first_image = collection.limit(1).first()
            # Auto-detect: bands, scale, temporal properties
        except:
            # Try as single Image
            image = ee.Image(dataset_id)
            # Auto-detect: bands, scale
```

### How Single Query Downloads All Datasets

#### 1. **Auto-Detection Process**
```python
# Step 1: Detect dataset type (ImageCollection vs Image)
detected = self.detect_dataset_type(dataset_id)

# Step 2: Extract metadata automatically
bands = [b['id'] for b in info['bands']]           # All available bands
scale = abs(bands[0].get('crs_transform')[0])      # Native resolution
has_time = 'system:time_start' in properties       # Temporal dataset?
```

#### 2. **Universal Processing Pipeline**
```python
def process_dataset(self, dataset_id, start_date, end_date, region, config):
    if config['type'] == 'Image':
        # Single image - no dates needed
        image = ee.Image(dataset_id).clip(region)
        return image, 1
    
    elif config['type'] == 'ImageCollection':
        collection = ee.ImageCollection(dataset_id)
        
        # Apply filters based on what dataset supports
        if config['requires_date'] and start_date:
            collection = collection.filterDate(start_date, end_date)
        
        collection = collection.filterBounds(region)
        
        # Reduce collection to single image
        image = collection.median().clip(region)  # or mean(), first(), etc.
        return image, collection.size().getInfo()
```

### Resolution Handling: Auto vs Manual

#### **Auto-Detection (Default)**
```python
# System automatically detects native resolution
scale = abs(bands[0].get('crs_transform')[0])
if scale == 0 or scale > 100000:
    # Fallback: use projection nominal scale
    proj = first_image.select(band_names[0]).projection()
    scale = proj.nominalScale().getInfo()
```

**You DON'T need to specify resolution** - the system:
- Detects native resolution automatically (e.g., 30m for Landsat, 10m for Sentinel-2)
- Uses this as default export resolution
- Shows you the native resolution in preview

#### **Manual Override (Optional)**
```python
# User can override with custom resolution
export_params = {
    'scale': user_specified_scale or auto_detected_scale,
    'region': region,
    'format': 'GEO_TIFF'
}
```

**When to specify resolution:**
- **Downsample**: Use larger scale (e.g., 1000m) for smaller files
- **Upsample**: Use smaller scale (e.g., 10m) for higher detail (limited by native resolution)

### Band Selection: All Bands Included

#### **Automatic Band Inclusion**
```python
# System gets ALL available bands
all_bands = image.bandNames().getInfo()  # ['B1', 'B2', 'B3', 'B4', 'B5', ...]

# Downloads ALL bands in single file
url = image.getDownloadURL({
    'scale': scale,
    'region': region,
    'format': 'GEO_TIFF'  # Multi-band GeoTIFF
})
```

**You DON'T select individual bands** - the system:
- Automatically includes ALL available bands
- Downloads as single multi-band file
- Each band becomes a separate layer in the GeoTIFF

### Image Collection Reduction Methods

#### **Temporal Compositing**
```python
# Multiple images → Single composite image
if method == 'median':
    image = collection.median()    # Reduces noise, good for clouds
elif method == 'mean':
    image = collection.mean()      # Average values
elif method == 'first':
    image = collection.first()     # Most recent image
elif method == 'sum':
    image = collection.sum()       # Total accumulation
```

**Why reduction is needed:**
- ImageCollections contain multiple images over time
- Can't download 100+ individual images directly
- Reduction creates single composite representing the time period

### Backend Query Processing

#### 1. `/preview` Endpoint - Dataset Analysis
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

#### 2. `/download` Endpoint - Data Export
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
    # Sample 100 random points for tabular data
    points = ee.FeatureCollection.randomPoints(region, 100)
    samples = image.sampleRegions(collection=points, scale=scale)
    url = samples.getDownloadURL('CSV')
```

### Key Advantages

1. **Universal Compatibility**: Works with ANY GEE dataset ID
2. **Zero Configuration**: Auto-detects all parameters
3. **Smart Defaults**: Uses optimal settings for each dataset type
4. **All-Inclusive**: Downloads all bands in single file
5. **Temporal Handling**: Automatically composites time-series data

## Configuration

The web interface allows you to configure:
- **Region**: Country, State, or Continent selection
- **Dataset**: Any GEE dataset ID (MODIS, Landsat, Sentinel, etc.)
- **Date Range**: Start and end dates
- **Export Format**: GeoTIFF or CSV
- **Bands**: Specific bands to download

## Screenshots

### Main Interface
![Main Interface](images/main.png)

### Output Received
![Output Received](images/outputreceived.png)

## Output

Data downloads directly to your browser's download folder in the selected format.
