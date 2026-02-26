import ee
from typing import Dict, Optional, List, Tuple

# paste entire class UniversalGEEHandler exactly as-is
# paste: handler = UniversalGEEHandler()

class UniversalGEEHandler:
    """Handles ANY Google Earth Engine dataset with auto-detection"""
    
    # Known revisit intervals from official documentation
    KNOWN_REVISIT_INTERVALS = {
        'COPERNICUS/S2': 5,  # Sentinel-2 (per satellite, 5 days)
        'COPERNICUS/S1': 6,  # Sentinel-1
        'LANDSAT/LC08': 16,  # Landsat 8
        'LANDSAT/LC09': 16,  # Landsat 9
        'LANDSAT/LE07': 16,  # Landsat 7
        'LANDSAT/LT05': 16,  # Landsat 5
        'MODIS/006/MOD': 1,  # MODIS Terra (daily)
        'MODIS/006/MYD': 1,  # MODIS Aqua (daily)
        'MODIS/061/MOD': 1,  # MODIS Terra (daily)
        'MODIS/061/MYD': 1,  # MODIS Aqua (daily)
    }
    
    def get_revisit_interval(self, dataset_id: str) -> Dict:
        """Get revisit interval from known database"""
        # Check known intervals
        for key, days in self.KNOWN_REVISIT_INTERVALS.items():
            if key in dataset_id:
                print(f"Found known revisit interval: {days} days for {dataset_id}")
                return {"interval_days": days, "interval_hours": None}
        
        print(f"No known revisit interval for {dataset_id}")
        return {"interval_days": None, "interval_hours": None}
    
    def detect_dataset_type(self, dataset_id: str) -> Dict:
        """
        AUTO-DETECTION: Works for ANY dataset with comprehensive metadata
        """
        
        # Try ImageCollection first (most common)
        try:
            collection = ee.ImageCollection(dataset_id)
            first_image = collection.limit(1).first()
            
            info = first_image.getInfo()
            bands = info['bands']
            properties = info.get('properties', {})
            
            band_names = [b['id'] for b in bands]
            has_time = 'system:time_start' in properties
            
            # Get scale using proper method - nominalScale() not crs_transform
            try:
                proj = first_image.select(band_names[0]).projection()
                scale = proj.nominalScale().getInfo()
                if scale == 0 or scale > 200000:  # Fallback for invalid scales
                    scale = 1000
            except:
                scale = 1000
            
            # Get comprehensive band information with correct scale
            band_details = []
            for band in bands:
                band_details.append({
                    'name': band['id'],
                    'data_type': band.get('data_type', {}).get('type', 'Unknown'),
                    'scale': f"{scale}m",  # Use the main detected scale for all bands
                    'crs': band.get('crs', 'Unknown'),
                    'dimensions': band.get('dimensions', 'Unknown')
                })
            
            # Skip slow metadata queries for large collections
            description = 'Auto-detected ImageCollection'
            dataset_type_info = 'ImageCollection'
            date_range = "Available (dates vary by region)" if has_time else None
            
            print(f"✓ Auto-detected ImageCollection: {dataset_id}")
            print(f"  - Bands: {band_names[:3]}{'...' if len(band_names) > 3 else ''}")
            print(f"  - Has dates: {has_time}")
            print(f"  - Scale: {scale}m")
            
            return {
                "type": "ImageCollection",
                "requires_date": has_time,
                "bands": band_names,
                "band_details": band_details,
                "scale": abs(scale),
                "description": description,
                "date_range": date_range,
                "dataset_type_info": dataset_type_info
            }
            
        except Exception as e1:
            # Try as single Image
            try:
                image = ee.Image(dataset_id)
                info = image.getInfo()
                bands = info['bands']
                properties = info.get('properties', {})
                band_names = [b['id'] for b in bands]
                
                # Get comprehensive band information with correct scale
                band_details = []
                for band in bands:
                    band_details.append({
                        'name': band['id'],
                        'data_type': band.get('data_type', {}).get('type', 'Unknown'),
                        'scale': f"{scale}m",  # Use the main detected scale for all bands
                        'crs': band.get('crs', 'Unknown'),
                        'dimensions': band.get('dimensions', 'Unknown')
                    })
                
                try:
                    proj = image.select(band_names[0]).projection()
                    scale = proj.nominalScale().getInfo()
                except:
                    scale = 1000
                
                # Get image description
                description = info.get('description', 'Single satellite image')
                
                # Check if image has date
                image_date = None
                if 'system:time_start' in properties:
                    try:
                        image_date = ee.Date(properties['system:time_start']).format('YYYY-MM-dd').getInfo()
                    except:
                        image_date = "Date available"
                
                print(f"✓ Auto-detected Image: {dataset_id}")
                print(f"  - Bands: {band_names}")
                
                return {
                    "type": "Image",
                    "requires_date": False,
                    "bands": band_names,
                    "band_details": band_details,
                    "scale": abs(scale),
                    "description": description,
                    "image_date": image_date,
                    "dataset_type_info": "Single Image"
                }
                
            except Exception as e2:
                raise ValueError(f"Cannot access dataset {dataset_id}. ImageCollection error: {str(e1)[:100]}. Image error: {str(e2)[:100]}")
    
    def get_smart_composite_method(self, dataset_id: str, bands: List[str]) -> str:
        """Choose appropriate composite method based on dataset type"""
        
        # Temperature data - use mean for average conditions
        if any(temp in dataset_id.upper() for temp in ['TEMPERATURE', 'TEMP', 'LST', 'MOD11', 'MYD11', 'CFSV2']):
            return 'mean'
        
        # Precipitation data - use sum for total rainfall
        if any(precip in dataset_id.upper() for precip in ['PRECIPITATION', 'PRECIP', 'RAINFALL', 'CHIRPS', 'TRMM']):
            return 'sum'
        
        # Land cover/classification - use mode for most common class
        if any(lc in dataset_id.upper() for lc in ['LANDCOVER', 'LAND_COVER', 'CLASSIFICATION', 'ESA', 'MODIS_LC']):
            return 'mode'
        
        # NDVI and vegetation indices - use median to reduce noise
        if any(vi in dataset_id.upper() for vi in ['NDVI', 'EVI', 'MOD13', 'MYD13']):
            return 'median'
        
        # Optical imagery (Landsat, Sentinel) - use median to remove clouds
        if any(optical in dataset_id.upper() for optical in ['LANDSAT', 'SENTINEL', 'COPERNICUS/S2']):
            return 'median'
        
        # Default: median (safest for most datasets)
        return 'median'
    def get_config(self, dataset_id: str, user_overrides: Optional[Dict] = None) -> Dict:
        """
        Get configuration using AUTO-DETECTION only
        """
        
        config = {}
        is_curated = False
        print(f"⚡ Auto-detecting dataset: {dataset_id}")
        
        # Auto-detect characteristics
        detected = self.detect_dataset_type(dataset_id)
        
        # Get smart composite method
        composite_method = self.get_smart_composite_method(dataset_id, detected["bands"]) if detected["type"] == "ImageCollection" else None
        
        # Build final config with auto-detected values
        final_config = {
            "dataset_id": dataset_id,
            "name": dataset_id.split('/')[-1],  # Simple name from ID
            "type": detected["type"],
            "requires_date": detected["requires_date"],
            "bands": detected["bands"],
            "scale": detected["scale"],
            "composite_method": composite_method,
            "is_curated": is_curated,
        }
        
        # Apply user overrides (highest priority)
        if user_overrides:
            final_config.update({k: v for k, v in user_overrides.items() if v is not None})
        
        return final_config
    
    def process_dataset(self, dataset_id: str, start_date: Optional[str], end_date: Optional[str], 
                       region: ee.Geometry, config: Dict) -> Tuple[Optional[ee.Image], int]:
        """Process any dataset based on configuration"""
        
        if config['type'] == 'Image':
            # Single image - no dates needed
            image = ee.Image(dataset_id)
            if region:
                image = image.clip(region)
            
            if config.get('preprocessing'):
                image = config['preprocessing'](image)
            
            return image, 1
        
        elif config['type'] == 'ImageCollection':
            # Image collection
            collection = ee.ImageCollection(dataset_id)
            
            # Date filtering (only if dataset has dates AND user provided dates)
            if config['requires_date']:
                if start_date and end_date:
                    # Validate date range
                    try:
                        from datetime import datetime
                        start = datetime.strptime(start_date, '%Y-%m-%d')
                        end = datetime.strptime(end_date, '%Y-%m-%d')
                        if start >= end:
                            raise ValueError("Start date must be before end date")
                    except ValueError as e:
                        raise ValueError(f"Invalid date range: {str(e)}")
                    
                    collection = collection.filterDate(start_date, end_date)
                else:
                    # No dates provided for temporal dataset - use last 30 days as default
                    collection = collection.filterDate(
                        ee.Date(ee.Date.now()).advance(-30, 'day'),
                        ee.Date.now()
                    )
            
            # Region filtering
            if region:
                collection = collection.filterBounds(region)
            
            # Cloud filtering (if curated config has it)
            if config.get('cloud_filter'):
                try:
                    collection = config['cloud_filter'](collection)
                except:
                    pass  # Skip if cloud filter fails
            
            # Check count (optimized for large collections)
            try:
                # For large datasets, limit count check to avoid timeout
                count = collection.limit(1000).size().getInfo()
                if count == 1000:
                    # Collection has 1000+ images, use approximate count
                    count = f"1000+"
            except Exception as e:
                raise ValueError(f"Failed to get image count. The collection might be empty or have invalid date range. Error: {str(e)}")
            
            if count == 0:
                return None, 0
            
            # Preprocessing (if curated config has it)
            if config.get('preprocessing'):
                try:
                    collection = collection.map(config['preprocessing'])
                except:
                    pass  # Skip if preprocessing fails
            
            # Composite based on method
            method = config['composite_method']
            if method == 'median':
                image = collection.median()
            elif method == 'mean':
                image = collection.mean()
            elif method == 'sum':
                image = collection.sum()
            elif method == 'mode':
                image = collection.mode()
            elif method == 'first':
                image = collection.first()
            else:
                image = collection.median()  # Safe default
            
            if region:
                image = image.clip(region)
            
            return image, count
        
        raise ValueError(f"Unknown type: {config['type']}")

# Initialize handler globally
handler = UniversalGEEHandler()
