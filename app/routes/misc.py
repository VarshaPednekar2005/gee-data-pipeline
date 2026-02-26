from fastapi import APIRouter
from app.gee_init import init_gee
from app.gee_handler import handler
from app.utils.region import get_region_geometry
from app.utils.viz import get_visualization_params

router = APIRouter()

# paste @router.post("/visualize") — change @app to @router
# paste @router.post("/check_task_status") — change @app to @router

@router.post("/visualize")
async def visualize_data(request: dict):
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        dataset_id = request['dataset']
        config = handler.get_config(dataset_id)
        
        region = get_region_geometry(request['region_type'], request['region_name'])
        
        # Process dataset
        image, _ = handler.process_dataset(
            dataset_id=dataset_id,
            start_date=request.get('start_date'),
            end_date=request.get('end_date'),
            region=region,
            config=config
        )
        
        if image is None:
            return {"success": False, "error": "No data available for visualization"}
        
        # Build visualization params
        vis_params = {
            "bands": config['vis_bands'],
            "min": config['vis_min'],
            "max": config['vis_max']
        }
        
        if config['vis_palette']:
            vis_params['palette'] = config['vis_palette']
        
        # Get map tile URL
        map_id = image.getMapId(vis_params)
        
        return {
            "success": True,
            "tile_url": map_id['tile_fetcher'].url_format,
            "vis_params": vis_params
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/check_task_status")
async def check_task_status(request: dict):
    """Check the status of a GEE export task"""
    if not init_gee():
        return {"success": False, "error": "GEE initialization failed"}
    
    try:
        task_id = request.get('task_id')
        if not task_id:
            return {"success": False, "error": "Task ID required"}
        
        # Get task status
        tasks = ee.batch.Task.list()
        task = None
        for t in tasks:
            if t.id == task_id:
                task = t
                break
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        status = task.status()
        
        return {
            "success": True,
            "state": status['state'],  # READY, RUNNING, COMPLETED, FAILED, CANCELLED
            "progress": status.get('progress', 0),
            "error_message": status.get('error_message', None)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
