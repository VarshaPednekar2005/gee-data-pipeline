from fastapi import APIRouter
from app.gee_init import init_gee
from app.gee_handler import handler
from app.utils.region import get_region_geometry
from app.utils.viz import get_visualization_params
from app.utils.files import estimate_size_mb, format_size_str
from app.config import SMALL_FILE_THRESHOLD_MB, MEDIUM_FILE_WARNING_MB

router = APIRouter()

@router.post("/preview")
async def preview_download(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        dataset_id = request['dataset']
        config = handler.get_config(dataset_id=dataset_id)
        
        # Get region - handle both old and new formats
        region_type = request['region_type']
        
        if region_type in ['geojson', 'coordinates', 'draw']:
            # Custom geometry
            region_data = request.get('custom_geometry')
            if not region_data:
                return {"success": False, "error": "Custom geometry required"}
        else:
            # Predefined region
            region_data = request['region_name']
        
        region = get_region_geometry(region_type, region_data)
        if not region:
            return {"success": False, "error": "Invalid region"}
        
        # Process dataset using universal handler
        image, count = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=request.get('start_date'),
            end_date=request.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {
                "success": False,
                "error": f"No images found for {dataset_id}. Try different date range or region."
            }
        
        # Get comprehensive dataset information
        detected_info = handler.detect_dataset_type(dataset_id)
        
        area_km2 = region.area().divide(1000000).getInfo()
        scale = config['scale']
        estimated_mb = estimate_size_mb(area_km2, scale, len(config['bands']))
        
        # Size validation and warnings
        size_warning = None
        size_str = format_size_str(estimated_mb)
            
        # Use 5MB threshold instead of 10MB to be more conservative
        # Accounts for compression variability (actual size may be 2-5x estimated)
        if estimated_mb > SMALL_FILE_THRESHOLD_MB:  
            size_warning = {
                "type": "size_limit",
                "message": f"File size (~{size_str}, may vary) requires Google Drive export",
                "suggestions": [
                    "File will be exported to Google Drive automatically",
                    "Actual size depends on data compression",
                    "Check your Drive after 5-30 minutes",
                    "💡 Tip: Use 'City' region for faster Sentinel-2 exports (2-5 min vs 30-60 min)"
                ]
            }
        elif estimated_mb > MEDIUM_FILE_WARNING_MB:  # Warning for medium files
            size_warning = {
                "type": "size_caution", 
                "message": f"Medium file size (~{size_str}) - actual size may vary",
                "suggestions": [
                    "Download should complete in a few minutes",
                    "💡 Tip: Use 'City' region for faster exports"
                ]
            }

        # Generate sample visualization
        sample_image_url = None
        try:
            # Create appropriate visualization for the dataset
            vis_params = get_visualization_params(dataset_id, config['bands'])
            if vis_params:
                # Get a small sample region for visualization
                sample_region = region.centroid().buffer(10000)  # 10km around center
                sample_image = image.clip(sample_region)
                
                # Generate map tiles
                map_id = sample_image.getMapId(vis_params)
                sample_image_url = map_id['tile_fetcher'].url_format
        except Exception as e:
            print(f"Could not generate sample image: {e}")
        
        # Prepare comprehensive response
        response_data = {
            "success": True,
            "dataset_name": config['name'],
            "dataset_id": dataset_id,
            "dataset_type": config['type'],
            "description": detected_info.get('description', 'No description available'),
            "image_count": count,
            "bands": config['bands'],
            "band_details": detected_info.get('band_details', []),
            "native_resolution": f"{config['scale']}m",
            "export_resolution": f"{config['scale']}m",
            "estimated_size": size_str,
            "estimated_mb": estimated_mb,
            "size_warning": size_warning,
            "area_km2": f"{area_km2:.1f}",
            "composite_method": config['composite_method'],
            "requires_date": config['requires_date'],
            "date_range": detected_info.get('date_range'),
            "image_date": detected_info.get('image_date'),
            "sample_image_url": sample_image_url,
            "dataset_type_info": detected_info.get('dataset_type_info', config['type'])
        }
        
        # Get revisit interval for ImageCollections
        if config['type'] == 'ImageCollection' and config['requires_date']:
            try:
                print(f"Getting revisit interval for {dataset_id}")
                revisit_info = handler.get_revisit_interval(dataset_id)
                print(f"Revisit info: {revisit_info}")
                if revisit_info['interval_days']:
                    response_data['revisit_interval'] = f"{revisit_info['interval_days']} days"
                    response_data['revisit_days'] = revisit_info['interval_days']
                    print(f"Set revisit_days to {revisit_info['interval_days']}")
                elif revisit_info['interval_hours']:
                    response_data['revisit_interval'] = f"{revisit_info['interval_hours']} hours"
                    response_data['revisit_hours'] = revisit_info['interval_hours']
                    print(f"Set revisit_hours to {revisit_info['interval_hours']}")
                else:
                    print("No revisit interval found")
            except Exception as e:
                print(f"Error getting revisit interval: {e}")
        
        return response_data
        
    except Exception as e:
        return {"success": False, "error": f"Analysis failed: {str(e)}"}

