from fastapi import APIRouter, Request
from app.gee_init import init_gee
from app.gee_handler import handler
from app.utils.region import get_region_geometry
from app.utils.clipping import exact_clip_region
from app.utils.files import estimate_size_mb, build_filename
from app.config import SMALL_FILE_THRESHOLD_MB, DEFAULT_DRIVE_FOLDER, CSV_SAMPLE_POINTS
import ee
import json
import os
import base64
import tempfile
import rasterio

router = APIRouter()

async def download_time_series(body, dataset_id, config, region, scale, drive_folder):
    """Download multiple files for each revisit period"""
    from datetime import datetime, timedelta
    
    start_date = body.get('start_date')
    end_date = body.get('end_date')
    revisit_days = int(body.get('revisit_days'))
    
    if not start_date or not end_date:
        return {"success": False, "error": "Start and end dates required for time-series"}
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Split into periods
    periods = []
    current = start
    while current < end:
        period_end = min(current + timedelta(days=revisit_days), end)
        periods.append((current.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d')))
        current = period_end
    
    # Start exports for each period
    tasks = []
    for i, (p_start, p_end) in enumerate(periods):
        collection = ee.ImageCollection(dataset_id).filterDate(p_start, p_end).filterBounds(region)
        
        if config.get('cloud_filter'):
            try:
                collection = config['cloud_filter'](collection)
            except:
                pass
        
        if config.get('preprocessing'):
            try:
                collection = collection.map(config['preprocessing'])
            except:
                pass
        
        image = collection.median()
        region_collection = ee.FeatureCollection([ee.Feature(region)])
        exact_clipped = image.clipToCollection(region_collection)
        
        dataset_simple = dataset_id.split('/')[-1]
        region_simple = str(body.get('region_name', 'region')).replace(' ', '_')[:15]
        filename = f"{dataset_simple}_{region_simple}_period{i+1}_{p_start}"
        
        task = ee.batch.Export.image.toDrive(
            image=exact_clipped,
            description=filename[:100],
            folder=drive_folder,
            fileNamePrefix=filename,
            scale=scale,
            region=region,
            maxPixels=1e13,
            fileFormat='GeoTIFF',
            formatOptions={'cloudOptimized': True, 'noData': -9999},
            shardSize=256
        )
        task.start()
        tasks.append({"task_id": task.id, "filename": filename, "period": f"{p_start} to {p_end}"})
    
    return {
        "success": True,
        "export_method": "time_series",
        "total_files": len(tasks),
        "tasks": tasks,
        "drive_folder": drive_folder,
        "message": f"Started {len(tasks)} exports (one per {revisit_days}-day period)"
    }

@router.post("/download")
async def download(request: Request):
    try:
        # Get raw body first to debug
        raw_body = await request.body()
        print(f"Raw body: {raw_body}")
        
        # Try to parse JSON
        if raw_body and raw_body != b'null':
            import json
            body = json.loads(raw_body.decode('utf-8'))
        else:
            return {"success": False, "error": "No request data received - check frontend"}
            
        print(f"Parsed body: {body}")
        
        if not body or body is None:
            return {"success": False, "error": "Request body is null"}
        
        if not init_gee():
            return {"success": False, "error": "GEE initialization failed"}
        
        # Validate required fields
        if 'dataset' not in body:
            return {"success": False, "error": "Dataset is required"}
        if 'region_type' not in body:
            return {"success": False, "error": "Region type is required"}
            
        dataset_id = body['dataset']
        config = handler.get_config(dataset_id)
        export_format = body.get('export_format', 'GeoTIFF')
        drive_folder = body.get('drive_folder', DEFAULT_DRIVE_FOLDER)
        
        scale = config['scale']
        
        # Validate format compatibility
        if export_format == 'CSV' and config['type'] == 'ImageCollection':
            return {
                "success": False, 
                "error": "CSV format not suitable for ImageCollections with multiple images. Use GeoTIFF instead."
            }
        
        # Handle region based on type
        region_type = body.get('region_type')
        
        if region_type in ['geojson', 'coordinates', 'draw']:
            region_data = body.get('custom_geometry')
            if not region_data:
                return {"success": False, "error": "Custom geometry required"}
        else:
            region_data = body.get('region_name')
            if not region_data:
                return {"success": False, "error": "Region name required"}
        
        region = get_region_geometry(region_type, region_data)
        if not region:
            return {"success": False, "error": "Region not found"}
        
        # Check for time-series download
        revisit_days = body.get('revisit_days')
        if revisit_days and config['type'] == 'ImageCollection':
            return await download_time_series(body, dataset_id, config, region, scale, drive_folder)
        
        # Process dataset (single composite)
        image, count = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=body.get('start_date'),
            end_date=body.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {"success": False, "error": "No images found"}
        
        # Create CLEANER filename
        filename = build_filename(dataset_id, body.get('region_name', 'region'))
        
        # Calculate file size
        area_km2 = region.area().divide(1000000).getInfo()
        estimated_mb = estimate_size_mb(area_km2, scale, len(config['bands']))
        
        # IMPORTANT: GEE has TWO limits:
        # 1. Direct download: ~32MB file size limit via getDownloadURL()
        # 2. Request payload: 50MB limit for the entire HTTP request
        # Use 5MB threshold to be conservative (actual size may be 2-5x estimated)
        
        export_to = body.get('export_to', 'auto')
        
        # Handle GCS export (available for any file size)
        if export_to == 'gcs':
            bucket_name = body.get('gcs_bucket', 'gee-exports-free')
            
            try:
                region_collection = ee.FeatureCollection([ee.Feature(region)])
                exact_clipped_image = image.clipToCollection(region_collection)
                
                task = ee.batch.Export.image.toCloudStorage(
                    image=exact_clipped_image,
                    description=filename[:100],
                    bucket=bucket_name,
                    fileNamePrefix=filename + '_exact',
                    scale=scale,
                    region=region,
                    maxPixels=1e13,
                    fileFormat='GeoTIFF',
                    formatOptions={
                        'cloudOptimized': True,
                        'noData': -9999
                    },
                    shardSize=256  # Prevent tiling by using large shard size
                )
                task.start()
                
                return {
                    "success": True,
                    "export_method": "gcs",
                    "task_id": task.id,
                    "filename": filename + '_exact.tif',
                    "bucket": bucket_name,
                    "message": f"Export started to GCS bucket '{bucket_name}'",
                    "estimated_size": f"~{estimated_mb:.1f}MB",
                    "exact_clip": True
                }
            except Exception as e:
                return {"success": False, "error": f"GCS export failed: {str(e)}"}
        
        # Auto-routing based on file size (use 5MB threshold)
        if estimated_mb > SMALL_FILE_THRESHOLD_MB and export_format == 'GeoTIFF':
            # LARGE FILE: Export to Drive
            # drive_folder = body.get('drive_folder', DEFAULT_DRIVE_FOLDER)
            
            try:
                region_collection = ee.FeatureCollection([ee.Feature(region)])
                exact_clipped_image = image.clipToCollection(region_collection)
                
                task = ee.batch.Export.image.toDrive(
                    image=exact_clipped_image,
                    description=filename[:100],
                    folder=drive_folder,
                    fileNamePrefix=filename + '_exact',
                    scale=scale,
                    region=region,
                    maxPixels=1e13,
                    fileFormat='GeoTIFF',
                    formatOptions={
                        'cloudOptimized': True,
                        'noData': -9999
                    },
                    shardSize=256  # Prevent tiling by using large shard size
                )
                task.start()
                
                return {
                    "success": True,
                    "export_method": "drive",
                    "task_id": task.id,
                    "filename": filename + '_exact.tif',
                    "folder": drive_folder,
                    "message": f"Large file (~{estimated_mb:.1f}MB) - Export started to Google Drive '{drive_folder}'",
                    "estimated_size": f"~{estimated_mb:.1f}MB",
                    "exact_clip": True
                }
                
            except Exception as export_error:
                error_msg = str(export_error)
                if "Service accounts do not have storage quota" in error_msg:
                    return {
                        "success": False,
                        "error": "OAuth authentication required for large files.",
                        "oauth_required": True,
                        "estimated_size": f"{estimated_mb:.1f}MB"
                    }
                return {
                    "success": False,
                    "error": f"Export failed: {error_msg}",
                    "estimated_size": f"{estimated_mb:.1f}MB"
                }
        
        # SMALL FILE: Direct download with exact clipping using rasterio
        elif export_format == 'GeoTIFF':
            try:
                # Apply exact clipping with rasterio for precise boundaries
                clipped_data, clipped_meta = exact_clip_region(image, region, scale)
                
                # Save to temporary file and encode
                with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                with rasterio.open(tmp_path, 'w', **clipped_meta) as dst:
                    dst.write(clipped_data)
                    # Set band descriptions to preserve GEE band names
                    if 'descriptions' in clipped_meta:
                        for i, band_name in enumerate(clipped_meta['descriptions'], 1):
                            dst.set_band_description(i, band_name)
                
                # Read and encode for download
                with open(tmp_path, 'rb') as f:
                    file_data = f.read()
                
                os.remove(tmp_path)
                
                # Return base64 encoded data for exact clip
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                
                return {
                    "success": True,
                    "export_method": "direct",
                    "exact_clip": True,
                    "file_data": encoded_data,
                    "format": export_format,
                    "filename": filename + '_exact.tif',
                    "file_size_mb": len(file_data) / (1024*1024),
                    "estimated_size": f"{len(file_data)/(1024*1024):.1f}MB",
                    "message": f"✓ Exact boundary clip ready ({len(file_data)/(1024*1024):.1f} MB)"
                }
            except Exception as download_error:
                error_msg = str(download_error)
                return {"success": False, "error": f"Exact clipping failed: {error_msg}"}
        
        elif export_format == 'CSV':
            points = ee.FeatureCollection.randomPoints(region, CSV_SAMPLE_POINTS)
            samples = image.sampleRegions(
                collection=points,
                scale=scale,
                geometries=True
            )
            url = samples.getDownloadURL('CSV')
            return {
                "success": True,
                "export_method": "direct",
                "download_url": url,
                "format": "CSV",
                "filename": filename + '.csv'
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Download error: {error_details}")
        return {"success": False, "error": f"Download failed: {str(e)}"}

