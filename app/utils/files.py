from datetime import datetime
from app.config import COMPRESSION_FACTOR

def estimate_size_mb(area_km2: float, scale: float, band_count: int) -> float:
    """Single source of truth for file size estimation."""
    pixels = area_km2 * (1_000_000 / (scale * scale)) * band_count
    return (pixels * 4) / (1_024 * 1_024) / COMPRESSION_FACTOR

def format_size_str(estimated_mb: float) -> str:
    """Human-readable size string."""
    if estimated_mb > 1024:
        return f"{estimated_mb/1024:.1f} GB"
    return f"{estimated_mb:.1f} MB"

def build_filename(dataset_id: str, region_name: str) -> str:
    """Clean filename from dataset + region + timestamp."""
    timestamp    = datetime.now().strftime('%Y%m%d_%H%M%S')
    dataset_part = dataset_id.split('/')[-1]
    region_part  = str(region_name).replace(' ', '_').replace(',', '').replace('.', '')[:15]
    return f"{dataset_part}_{region_part}_{timestamp}"