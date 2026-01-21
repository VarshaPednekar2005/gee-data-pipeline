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

## Architecture

### Single-File Application
- `clean_downloader.py` - Contains both backend (FastAPI) and frontend (HTML/CSS/JS)
- Service account authentication (no manual GEE auth needed)
- Direct browser downloads

### Backend Query Processing

The application processes GEE queries through three main endpoints:

#### 1. `/preview` Endpoint
```python
# Filters dataset by region and date
collection = ee.ImageCollection(dataset_id).filterBounds(region).filterDate(start_date, end_date)
# Returns metadata: bands, resolution, file size
```

#### 2. `/visualize` Endpoint  
```python
# Creates visualization parameters for different data types
vis_params = get_visualization_params(dataset_id, bands)
# Generates map tiles for web display
```

#### 3. `/download` Endpoint
```python
# Processes and exports data
if export_format == 'geotiff':
    # Clips to region and exports as GeoTIFF
    image = collection.mean().clip(region)
    url = image.getDownloadURL(params)
elif export_format == 'csv':
    # Samples points and exports as CSV
    samples = image.sample(region=region, scale=scale)
```

## Configuration

The web interface allows you to configure:
- **Region**: Country, State, or Continent selection
- **Dataset**: Any GEE dataset ID (MODIS, Landsat, Sentinel, etc.)
- **Date Range**: Start and end dates
- **Export Format**: GeoTIFF or CSV
- **Bands**: Specific bands to download

## Output

Data downloads directly to your browser's download folder in the selected format.
