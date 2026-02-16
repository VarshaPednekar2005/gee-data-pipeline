# How to Verify the New Features

## Step 1: Start the Server

```bash
cd /home/varshapednekar/projects/gee-data-pipeline
source venv/bin/activate
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000 --reload
```

Or use the script:
```bash
./START_SERVER.sh
```

## Step 2: Open Browser

Go to: http://127.0.0.1:8000

## Step 3: Test with Sentinel-2

Enter these values:
- **Dataset**: `COPERNICUS/S2_SR_HARMONIZED`
- **Start Date**: `2024-01-01`
- **End Date**: `2024-01-31`
- **Region Type**: Select "State"
- **Region**: Select "Michigan"

Click: **"Analyze Dataset"**

## Step 4: What You Should See

After clicking "Analyze Dataset", the preview should show:

### NEW FEATURE 1: Revisit Interval (Auto-Detected)
```
┌─────────────────────────────────┐
│ Images Found        │ 484       │
│ Revisit Interval    │ 5 days    │  ← NEW! Auto-detected
│ Reduction Method    │ median    │
└─────────────────────────────────┘
```

### NEW FEATURE 2: Download Mode Selector
```
╔════════════════════════════════════════════╗
║ 📊 Download Mode                           ║  ← NEW! Radio buttons
╠════════════════════════════════════════════╣
║                                            ║
║ ◉ Single Composite File                   ║
║   Merge all 484 images into 1 file        ║
║   using median reduction                  ║
║   ✓ Best for general analysis             ║
║                                            ║
║ ○ Time-Series (6 Files)                   ║
║   Download 6 separate files, one per      ║
║   5 days (each uses median for period)    ║
║   ✓ Track changes over time               ║
║                                            ║
╚════════════════════════════════════════════╝
```

## If You DON'T See These Features:

### Check 1: Browser Cache
Press `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac) to hard refresh

### Check 2: Server Running
```bash
ps aux | grep uvicorn
```
Should show uvicorn process running

### Check 3: Check Server Logs
Look for any errors when starting the server

### Check 4: Verify File Changes
```bash
grep -n "detect_revisit_interval" clean_downloader.py
grep -n "downloadMode" clean_downloader.py
```
Both should return results

## Common Issues

### Issue: "Old interface still showing"
**Solution**: Hard refresh browser (Ctrl + Shift + R)

### Issue: "Server won't start"
**Solution**: 
```bash
# Kill any existing process
pkill -f uvicorn
# Activate venv
source venv/bin/activate
# Start fresh
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000 --reload
```

### Issue: "Changes not appearing"
**Solution**: Make sure you're using `--reload` flag with uvicorn

## Quick Verification Commands

```bash
# 1. Check if changes are in file
cd /home/varshapednekar/projects/gee-data-pipeline
grep "detect_revisit_interval" clean_downloader.py
grep "Download Mode" clean_downloader.py

# 2. Check server status
curl http://127.0.0.1:8000 | grep -i "GEE Data Pipeline"

# 3. Test compilation
python3 -m py_compile clean_downloader.py && echo "✓ Code is valid"
```
