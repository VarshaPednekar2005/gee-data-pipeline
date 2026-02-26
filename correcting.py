from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import ee
from typing import Dict, Optional, List, Tuple
import tempfile
import base64
import rasterio
import rasterio.mask
import requests
from shapely.geometry import shape
import os
from fastapi.responses import FileResponse
from pathlib import Path
