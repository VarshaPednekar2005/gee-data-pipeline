#!/bin/bash

echo "=== Testing New Features ==="
echo ""
echo "1. Kill any existing server..."
pkill -f "uvicorn.*clean_downloader" 2>/dev/null
sleep 1

echo "2. Starting server in background..."
cd /home/varshapednekar/projects/gee-data-pipeline
source venv/bin/activate
nohup uvicorn clean_downloader:app --host 127.0.0.1 --port 8000 --reload > server.log 2>&1 &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"
sleep 5

echo "3. Checking if server is running..."
if curl -s http://127.0.0.1:8000 > /dev/null; then
    echo "   ✓ Server is running"
else
    echo "   ✗ Server failed to start"
    cat server.log
    exit 1
fi

echo ""
echo "4. Checking for new features in HTML..."
if curl -s http://127.0.0.1:8000 | grep -q "Download Mode"; then
    echo "   ✓ Download Mode selector found in HTML"
else
    echo "   ✗ Download Mode selector NOT found"
fi

if curl -s http://127.0.0.1:8000 | grep -q "revisitDays"; then
    echo "   ✓ Revisit days field found in HTML"
else
    echo "   ✗ Revisit days field NOT found"
fi

echo ""
echo "5. Server is running at: http://127.0.0.1:8000"
echo "   Open in browser and check browser console (F12) for debug logs"
echo ""
echo "To stop server: kill $SERVER_PID"
