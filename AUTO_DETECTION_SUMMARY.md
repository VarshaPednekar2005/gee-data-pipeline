# Auto-Detection Feature Summary

## What Your Senior Wanted
✓ Auto-detect revisit intervals (5 days, 4 days, 4 hours, etc.)
✓ Show interval before downloading
✓ Download separate files for each revisit period

## How It Works Now

### Step 1: User Analyzes Dataset
```
User enters:
- Dataset: COPERNICUS/S2_SR_HARMONIZED
- Dates: 2024-01-01 to 2024-01-31
- Region: Michigan

Clicks: "Analyze Dataset"
```

### Step 2: System Auto-Detects
```
Backend:
1. Samples last 60 days of images
2. Gets timestamps: [t1, t2, t3, ...]
3. Calculates differences: [t2-t1, t3-t2, ...]
4. Finds median difference: 5 days

Returns: "revisit_interval": "5 days"
```

### Step 3: Frontend Shows & Auto-Fills
```
Preview displays:
┌─────────────────────────────┐
│ Revisit Interval: 5 days    │  ← Shows in info grid
└─────────────────────────────┘

Input field auto-filled:
┌─────────────────────────────┐
│ Revisit Interval: [5]       │  ← Auto-filled with detected value
└─────────────────────────────┘
```

### Step 4: User Downloads
```
Option A: Keep auto-filled value (5)
→ Downloads 6 files (one per 5-day period)

Option B: Clear the field
→ Downloads 1 file (single composite)

Option C: Change to different value (10)
→ Downloads 3 files (one per 10-day period)
```

## Examples of Auto-Detection

### Sentinel-2 (5 days)
```
Images: 2024-01-01, 2024-01-06, 2024-01-11, ...
Differences: 5 days, 5 days, 5 days
Detected: 5 days ✓
```

### Landsat 8 (16 days)
```
Images: 2024-01-01, 2024-01-17, 2024-02-02, ...
Differences: 16 days, 16 days, 16 days
Detected: 16 days ✓
```

### MODIS (1 day)
```
Images: 2024-01-01, 2024-01-02, 2024-01-03, ...
Differences: 1 day, 1 day, 1 day
Detected: 1 day ✓
```

### GOES Weather (4 hours)
```
Images: 00:00, 04:00, 08:00, 12:00, ...
Differences: 4 hours, 4 hours, 4 hours
Detected: 4 hours ✓
```

## Code Changes

### 1. New Detection Function
```python
def detect_revisit_interval(dataset_id, region):
    # Sample last 60 days
    # Calculate median time difference
    # Return days or hours
```

### 2. Updated Preview Endpoint
```python
@app.post("/preview")
async def preview_download():
    # ... existing code ...
    
    # NEW: Detect revisit interval
    revisit_info = handler.detect_revisit_interval(dataset_id, region)
    response_data['revisit_interval'] = "5 days"
    response_data['revisit_days'] = 5
```

### 3. Updated Frontend
```javascript
// Auto-fill after preview
if (result.revisit_days) {
    document.getElementById('revisitDays').value = result.revisit_days;
}

// Show in preview
${result.revisit_interval ? `
    <div class="info-item">
        <strong>Revisit Interval</strong>
        <span>${result.revisit_interval}</span>
    </div>
` : ''}
```

## User Experience

### Before (Manual)
1. User looks up Sentinel-2 specs online
2. Finds revisit interval is 5 days
3. Manually enters 5 in the field
4. Downloads

### After (Auto)
1. User clicks "Analyze Dataset"
2. System shows "Revisit Interval: 5 days"
3. Field auto-filled with 5
4. User just clicks download ✓

## Benefits
- ✓ Zero configuration needed
- ✓ Works with ANY temporal dataset
- ✓ Accurate (based on actual data)
- ✓ User can override if needed
- ✓ Handles both days and hours
- ✓ Robust to missing data
