# Download Mode Selection Feature

## What Changed

### User Experience Flow

#### Step 1: User Analyzes Dataset
```
User enters:
- Dataset: COPERNICUS/S2_SR_HARMONIZED
- Dates: 2024-01-01 to 2024-01-31
- Region: Michigan

Clicks: "Analyze Dataset"
```

#### Step 2: Preview Shows Auto-Detected Info
```
┌─────────────────────────────────────────────────┐
│ Dataset Preview                                  │
├─────────────────────────────────────────────────┤
│ Images Found: 484                                │
│ Revisit Interval: 5 days (auto-detected)        │
│ Reduction Method: median                         │
│ File Size: ~10 MB                                │
├─────────────────────────────────────────────────┤
│ 📊 Download Mode                                 │
│                                                  │
│ ○ Single Composite File                         │
│   Merge all 484 images into 1 file using        │
│   median reduction                               │
│   ✓ Best for general analysis                   │
│   ✓ Single file to manage                       │
│                                                  │
│ ○ Time-Series (6 Files)                         │
│   Download 6 separate files, one per 5 days     │
│   (each uses median for that period)            │
│   ✓ Track changes over time                     │
│   ✓ Better cloud handling per period            │
│                                                  │
│ [Download to Computer]                           │
└─────────────────────────────────────────────────┘
```

#### Step 3: User Selects Mode & Downloads

**Option A: Single Composite (Default)**
```
User: Keeps "Single Composite File" selected
System: Downloads 1 file with all 484 images merged
Result: S2_SR_HARMONIZED_Michigan_20240210.tif
```

**Option B: Time-Series**
```
User: Selects "Time-Series (6 Files)"
System: Exports 6 files to Google Drive
Result: 
  - S2_SR_HARMONIZED_Michigan_period1_2024-01-01.tif
  - S2_SR_HARMONIZED_Michigan_period2_2024-01-06.tif
  - S2_SR_HARMONIZED_Michigan_period3_2024-01-11.tif
  - S2_SR_HARMONIZED_Michigan_period4_2024-01-16.tif
  - S2_SR_HARMONIZED_Michigan_period5_2024-01-21.tif
  - S2_SR_HARMONIZED_Michigan_period6_2024-01-26.tif
```

## Key Features

### 1. Auto-Detection
- ✓ Revisit interval detected automatically
- ✓ Number of files calculated automatically
- ✓ No manual input needed

### 2. Clear Options
- ✓ Radio buttons for easy selection
- ✓ Descriptions explain what each mode does
- ✓ Shows exact number of files for time-series

### 3. Reduction Method Clarity
**Question: "Do we need reduction method for individual files?"**

**Answer: YES, but it's automatic**

Even in time-series mode:
- Each period may have multiple images (overlapping tiles, multiple satellites)
- Example: 5-day period might have 10-20 images for Michigan
- System uses median reduction for each period automatically
- User doesn't need to worry about it

**Why median is still needed:**
```
Period 1 (Jan 1-5):
  - 15 images from Sentinel-2A and 2B
  - Multiple overlapping tiles
  - Some with clouds
  → Median composite creates 1 clean image for this period
```

### 4. Smart Defaults
- Single composite selected by default (most common use case)
- Time-series available for advanced users
- Both modes clearly explained

## Code Changes

### 1. Hidden Input Field
```html
<!-- Old: Visible input field -->
<input type="number" id="revisitDays" placeholder="5">

<!-- New: Hidden field (auto-filled by preview) -->
<input type="hidden" id="revisitDays">
```

### 2. Mode Selector in Preview
```javascript
if (result.revisit_interval && result.revisit_days) {
    // Show radio button selector
    // Calculate number of periods
    // Display both options with descriptions
}
```

### 3. Download Logic
```javascript
async function confirmDownload() {
    // Check which mode is selected
    const downloadMode = document.querySelector('input[name="downloadMode"]:checked');
    const useTimeSeries = downloadMode && downloadMode.value === 'timeseries';
    
    // Only add revisit_days if time-series selected
    if (useTimeSeries) {
        requestData.revisit_days = parseInt(revisitDaysInput.value);
    }
}
```

## Benefits

### For Users
1. **No confusion**: Clear choice between 1 file or multiple files
2. **Informed decision**: See exactly how many files before downloading
3. **No manual calculation**: System calculates everything
4. **Safe default**: Single composite selected by default

### For Your Senior
1. **Answers the question**: Reduction method is still used (automatically)
2. **User control**: Users choose what they want
3. **Professional UI**: Clean, clear interface
4. **Flexible**: Works for any temporal dataset

## Examples

### Sentinel-2 (30 days)
```
Detected: 5 days revisit
Options:
  ○ Single file (484 images → 1 file)
  ○ Time-series (484 images → 6 files, ~80 images each)
```

### Landsat 8 (60 days)
```
Detected: 16 days revisit
Options:
  ○ Single file (all images → 1 file)
  ○ Time-series (all images → 4 files, one per 16 days)
```

### MODIS (7 days)
```
Detected: 1 day revisit
Options:
  ○ Single file (7 images → 1 file)
  ○ Time-series (7 images → 7 files, one per day)
```

## UI Improvements

### Before
- Manual input field for revisit interval
- User had to know the interval
- Unclear what would happen

### After
- Auto-detected and displayed
- Clear radio button choice
- Shows exact outcome (number of files)
- Explains benefits of each mode
- Reduction method explained in context
