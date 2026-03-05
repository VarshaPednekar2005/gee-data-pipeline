FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for rasterio/geospatial
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# GEE Authentication Note:
# Credentials are mounted at runtime via docker-compose volume:
# ~/.config/earthengine:/root/.config/earthengine
# The container will automatically find and use these credentials

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]