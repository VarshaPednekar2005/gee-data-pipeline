#!/bin/bash
cd /home/varshapednekar/projects/gee-data-pipeline
source venv/bin/activate
uvicorn clean_downloader:app --host 127.0.0.1 --port 8000 --reload
