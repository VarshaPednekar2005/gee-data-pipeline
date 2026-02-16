# Time-Series Download Feature

## Overview
Added support for downloading multiple files based on **auto-detected** satellite revisit intervals instead of a single composite image.

## What Changed

### Backend (clean_downloader.py)

1. **New Function: `detect_revisit_interval()`**
   - Samples last 60 days of images
   - Calculates median time difference between images
   - Returns interval in days or hours
   - Works for any ImageCollection dataset

2. **New Function: `download_time_series()`**
   - Splits date range into periods based on revisit interval
   - Creates a composite for each period
   - Exports each period as a separate file to Google Drive
   - Returns task IDs for all exports

3. **Modified: `/preview` endpoint**
   - Detects revisit interval automatically
   - Returns interval in response (days or hours)
   - Shows in preview before download

4. **Modified: `/download` endpoint**
   - Checks for `revisit_days` parameter
   - Routes to time-series download if interval is specified
   - Falls back to single composite if no interval provided

### Frontend (HTML/JavaScript)

1. **New Input Field: "Revisit Interval (days)"**
   - Optional numeric input
   - **Auto-filled** after preview with detected interval
   - User can modify if needed
   - Includes helpful description

2. **Updated: Preview Display**
   - Shows detected revisit interval in info grid
   - Displays as "5 days" or "4 hours" etc.

3. **Updated: `preview()` function**
   - Auto-fills revisit interval field with detected value
   - Converts hours to days if needed

4. **Updated: `confirmDownload()` function**
   - Captures revisit_days value
   - Sends to backend if provided

5. **New Response Handler: Time-Series Export**
   - Shows list of all files being exported
   - Displays period for each file
   - Shows Google Drive folder location

## How It Works

### Auto-Detection Process

1. **User clicks "Analyze Dataset"**
2. System samples recent images (last 60 days)
3. Calculates median time between images
4. Determines if interval is in days or hours
5. **Auto-fills the revisit interval field**
6. Shows interval in preview (e.g., "5 days")

### Example: Sentinel-2 for 30 days

**User Input:**
- Dataset: `COPERNICUS/S2_SR_HARMONIZED`
- Start Date: `2024-01-01`
- End Date: `2024-01-31`
- Region: Michigan
- Click "Analyze Dataset"

**System Auto-Detects:**
- Revisit Interval: **5 days** (auto-filled)
- Shows in preview: "Revisit Interval: 5 days"

**User Downloads:**
- System creates 6 files (30 days ÷ 5 days)
- Each file covers one 5-day period
- All exported to Google Drive

**Result:**
- 6 separate GeoTIFF files in Google Drive
- Filenames: `S2_SR_HARMONIZED_Michigan_period1_2024-01-01.tif`, etc.

## Usage

### For Single Composite (Original Behavior)
1. Analyze dataset
2. Clear the auto-filled revisit interval field
3. Download → Gets 1 file (composite of all images)

### For Time-Series (New Feature)
1. Analyze dataset
2. Keep the auto-filled revisit interval (or modify it)
3. Download → Gets multiple files (one per period)

## Auto-Detected Intervals

| Satellite | Typical Interval | Auto-Detected |
|-----------|------------------|---------------|
| Sentinel-2 | 5 days | ✓ |
| Landsat 8/9 | 16 days | ✓ |
| MODIS | 1 day | ✓ |
| Sentinel-1 | 6-12 days | ✓ |
| GOES (weather) | 1-4 hours | ✓ |

## Benefits

1. **Zero Configuration**: No need to look up revisit intervals
2. **Accurate**: Based on actual image timestamps
3. **Flexible**: User can override auto-detected value
4. **Universal**: Works with any temporal dataset
5. **Time-Series Analysis**: Track changes over time
6. **Cloud Avoidance**: Each period has its own composite

## Technical Details

- Samples up to 20 images from last 60 days
- Uses median difference (robust to outliers)
- Handles both days and hours
- Falls back gracefully if detection fails
- Uses same exact clipping method as single downloads
- All exports go to Google Drive (no size limit)

## Testing

Test with:
```
Dataset: COPERNICUS/S2_SR_HARMONIZED
Start: 2024-01-01
End: 2024-01-31
Region: Any state/city
```

Expected:
1. Preview shows "Revisit Interval: 5 days"
2. Input field auto-filled with "5"
3. Download creates 6 files in Google Drive
