import tempfile, os, requests
import rasterio, rasterio.mask
from shapely.geometry import shape
import ee

# paste exact_clip_region() exactly as-is
def exact_clip_region(image, region, scale):
    """Exact clipping preserving data values and GEE band metadata"""
    region_geom = region.getInfo()
    
    # Get original GEE band information to preserve metadata
    band_info = image.getInfo()['bands']
    band_names = [band['id'] for band in band_info]
    
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # First get basic clipped image from GEE
        clipped_image = image.clip(region)
        url = clipped_image.getDownloadURL({
            'scale': scale,
            'region': region_geom,
            'format': 'GEO_TIFF'
        })
        
        response = requests.get(url)
        with open(tmp_path, 'wb') as f:
            f.write(response.content)
        
        # Apply exact clipping with rasterio
        with rasterio.open(tmp_path) as src:
            geom = shape(region_geom)
            clipped_data, clipped_transform = rasterio.mask.mask(
                src, [geom], crop=True, filled=True, nodata=src.nodata
            )
            
            clipped_meta = src.meta.copy()
            clipped_meta.update({
                'height': clipped_data.shape[1],
                'width': clipped_data.shape[2],
                'transform': clipped_transform,
                'nodata': src.nodata,
                'compress': 'lzw',  # Add compression like GEE exports
                'tiled': True       # Optimize for GIS software
            })
            
            # Preserve original GEE band names in metadata
            if len(band_names) == clipped_data.shape[0]:
                clipped_meta['descriptions'] = band_names
            
            return clipped_data, clipped_meta
            
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
