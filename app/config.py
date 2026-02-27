import os
from dotenv import load_dotenv

load_dotenv()

# All constants in one place. Change here = changes everywhere.
GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "plucky-sight-423703-k5")

SMALL_FILE_THRESHOLD_MB = 5.0   # below → direct download
MEDIUM_FILE_WARNING_MB  = 3.0   # below small → caution warning
COMPRESSION_FACTOR      = 3.0   # GeoTIFF LZW estimate
DEFAULT_DRIVE_FOLDER    = "EarthEngineExports"
CSV_SAMPLE_POINTS       = 100
CITY_BUFFER_METERS      = 20_000