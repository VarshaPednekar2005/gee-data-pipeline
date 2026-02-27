#!/bin/bash
cd /home/varshapednekar/projects/gee-data-pipeline
source venv/bin/activate
uvicorn app.main:app --reload
