# GEE Data Pipeline

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Authenticate with Google Earth Engine:
```bash
earthengine authenticate
```

3. Run the pipeline:
```bash
python run_pipeline.py
```

## Configuration

Edit `run_pipeline.py` to modify:
- Region of interest
- Date range
- Data collections (Landsat, Sentinel-2, etc.)

## Output

Data will be exported to your Google Drive in the 'GEE_Downloads' folder.
