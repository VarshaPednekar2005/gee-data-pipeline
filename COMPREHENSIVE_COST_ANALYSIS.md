# Comprehensive Cost & Space Analysis: All GEE Datasets

## Part 1: Visualizations

### 1. Method Comparison Across Regions
![Method Comparison](images/method_comparison.png)

### 2. Cost Heatmap (Dataset × Method × Region)
![Cost Heatmap](images/cost_heatmap.png)

### 3. Storage Costs by Composite Method
![Storage Costs](images/storage_cost_bars.png)

### 4. Dataset-Specific Costs
![Dataset Comparison](images/dataset_comparison.png)

### Understanding Composite Methods

**1. Individual Images**: Every satellite pass stored separately
- **Pros**: Maximum temporal detail, no data loss
- **Cons**: Highest storage cost, most files to manage
- **Use case**: Detailed change detection, event analysis

**2. Time Series**: Organized temporal sequences
- **Pros**: Good temporal resolution, easier analysis
- **Cons**: Still high storage, complex processing
- **Use case**: Trend analysis, seasonal studies

**3. Monthly Composites**: One image per month (best pixel selection)
- **Pros**: Balanced cost/detail, cloud-free imagery
- **Cons**: Loses daily variations
- **Use case**: Monthly monitoring, agricultural cycles

**4. Annual Composites**: One image per year (best pixel selection)
- **Pros**: Lowest cost, long-term trends, minimal storage
- **Cons**: Loses seasonal variations
- **Use case**: Year-over-year comparison, land cover change

---

## Part 2: Sentinel-2 Detailed Analysis

### MUMBAI (600 km²) - Complete Historical Data (10.7 years)

| Method | Total Files | Total Size | Download Cost | Storage (1 Year) | Total (1 Year) |
|--------|-------------|------------|---------------|------------------|----------------|
| Individual Images | 3,124 images | 156 GB | $3.12 | $36/year | $39/year |
| Time Series (per visit) | 781 files | 39 GB | $0.78 | $8/year | $9/year |
| Monthly Composites | 128 files | 9.6 GB | $0.13 | $1/year | $1/year |
| Annual Composites | 11 files | 1.1 GB | $0.01 | $0 (under 5GB) | $0/year |

### MAHARASHTRA (307,713 km²) - Complete Historical Data (10.7 years)

| Method | Total Files | Total Size | Download Cost | Storage (1 Year) | Total (1 Year) |
|--------|-------------|------------|---------------|------------------|----------------|
| Individual Images | 37,450 images | 7.49 TB | $374.50 | $1,798/year | $2,173/year |
| Time Series (per visit) | 781 files | 1.56 TB | $7.81 | $374/year | $382/year |
| Monthly Composites | 128 files | 256 GB | $1.28 | $60/year | $61/year |
| Annual Composites | 11 files | 33 GB | $0.11 | $7/year | $7/year |

### INDIA (3,287,263 km²) - Complete Historical Data (10.7 years)

| Method | Total Files | Total Size | Download Cost | Storage (1 Year) | Total (1 Year) |
|--------|-------------|------------|---------------|------------------|----------------|
| Individual Images | 273,385 images | 68.3 TB | $5,467.70 | $16,392/year | $21,860/year |
| Time Series (per visit) | 781 files | 19.5 TB | $39.05 | $4,680/year | $4,719/year |
| Monthly Composites | 128 files | 2.56 TB | $6.40 | $614/year | $620/year |
| Annual Composites | 11 files | 275 GB | $0.55 | $66/year | $67/year |

---

## Part 3: Cost Comparison by Dataset Type

### Mumbai (600 km²) - Annual Composites

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 11 | 1.1 GB | $0/year | $6,000 | $24,000 | ∞ |
| Landsat 8/9 | 10 years | 11 | 800 MB | $0/year | $6,000 | $24,000 | ∞ |
| Landsat 7 | 20 years | 21 | 1.5 GB | $0/year | $6,000 | $24,000 | ∞ |
| Landsat 4-5 | 30 years | 31 | 2.2 GB | $0/year | $6,000 | $24,000 | ∞ |
| MODIS | 24 years | 25 | 500 MB | $0/year | $6,000 | $24,000 | ∞ |
| Sentinel-1 | 10 years | 11 | 2 GB | $0/year | $6,000 | $24,000 | ∞ |
| CHIRPS | 43 years | 44 | 1.8 GB | $0/year | $6,000 | $24,000 | ∞ |
| ERA5 | 74 years | 75 | 3.5 GB | $0/year | $6,000 | $24,000 | ∞ |
| Land Cover | 5 years | 6 | 300 MB | $0/year | $6,000 | $24,000 | ∞ |
| DEM (Static) | One-time | 1 | 50 MB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **236** | **13.8 GB** | **$0/year** | **$6,000** | **$24,000** | **∞** |

### Maharashtra (307,713 km²) - Annual Composites

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 11 | 33 GB | $7/year | $6,000 | $24,000 | 857x |
| Landsat 8/9 | 10 years | 11 | 25 GB | $5/year | $6,000 | $24,000 | 1,200x |
| Landsat 7 | 20 years | 21 | 45 GB | $10/year | $6,000 | $24,000 | 600x |
| Landsat 4-5 | 30 years | 31 | 65 GB | $14/year | $6,000 | $24,000 | 429x |
| MODIS | 24 years | 25 | 12 GB | $2/year | $6,000 | $24,000 | 3,000x |
| Sentinel-1 | 10 years | 11 | 40 GB | $8/year | $6,000 | $24,000 | 750x |
| CHIRPS | 43 years | 44 | 20 GB | $4/year | $6,000 | $24,000 | 1,500x |
| ERA5 | 74 years | 75 | 35 GB | $7/year | $6,000 | $24,000 | 857x |
| Land Cover | 5 years | 6 | 8 GB | $1/year | $6,000 | $24,000 | 6,000x |
| DEM (Static) | One-time | 1 | 500 MB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **236** | **283 GB** | **$58/year** | **$6,000** | **$24,000** | **103x** |

### India (3,287,263 km²) - Annual Composites

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 11 | 275 GB | $67/year | $6,000 | $24,000 | 90x |
| Landsat 8/9 | 10 years | 11 | 210 GB | $49/year | $6,000 | $24,000 | 122x |
| Landsat 7 | 20 years | 21 | 380 GB | $90/year | $6,000 | $24,000 | 67x |
| Landsat 4-5 | 30 years | 31 | 550 GB | $131/year | $6,000 | $24,000 | 46x |
| MODIS | 24 years | 25 | 100 GB | $23/year | $6,000 | $24,000 | 261x |
| Sentinel-1 | 10 years | 11 | 350 GB | $83/year | $6,000 | $24,000 | 72x |
| CHIRPS | 43 years | 44 | 180 GB | $42/year | $6,000 | $24,000 | 143x |
| ERA5 | 74 years | 75 | 300 GB | $71/year | $6,000 | $24,000 | 85x |
| Land Cover | 5 years | 6 | 65 GB | $14/year | $6,000 | $24,000 | 429x |
| DEM (Static) | One-time | 1 | 5 GB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **236** | **2.4 TB** | **$569/year** | **$6,000** | **$24,000** | **11x** |

---

## Part 4: Monthly Composites Comparison

### Mumbai (600 km²) - Monthly Composites

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 128 | 9.6 GB | $1/year | $6,000 | $24,000 | 6,000x |
| Landsat 8/9 | 10 years | 120 | 7 GB | $0/year | $6,000 | $24,000 | ∞ |
| MODIS | 24 years | 288 | 6 GB | $0/year | $6,000 | $24,000 | ∞ |
| Sentinel-1 | 10 years | 120 | 18 GB | $3/year | $6,000 | $24,000 | 2,000x |
| CHIRPS | 43 years | 516 | 20 GB | $4/year | $6,000 | $24,000 | 1,500x |
| **ALL DATASETS** | **-** | **1,172** | **60 GB** | **$13/year** | **$6,000** | **$24,000** | **462x** |

### Maharashtra (307,713 km²) - Monthly Composites

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 128 | 256 GB | $61/year | $6,000 | $24,000 | 98x |
| Landsat 8/9 | 10 years | 120 | 190 GB | $44/year | $6,000 | $24,000 | 136x |
| MODIS | 24 years | 288 | 140 GB | $32/year | $6,000 | $24,000 | 188x |
| Sentinel-1 | 10 years | 120 | 380 GB | $90/year | $6,000 | $24,000 | 67x |
| CHIRPS | 43 years | 516 | 220 GB | $52/year | $6,000 | $24,000 | 115x |
| **ALL DATASETS** | **-** | **1,172** | **1.2 TB** | **$279/year** | **$6,000** | **$24,000** | **22x** |

### India (3,287,263 km²) - Monthly Composites

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 128 | 2.56 TB | $620/year | $6,000 | $24,000 | 10x |
| Landsat 8/9 | 10 years | 120 | 1.9 TB | $456/year | $6,000 | $24,000 | 13x |
| MODIS | 24 years | 288 | 1.4 TB | $336/year | $6,000 | $24,000 | 18x |
| Sentinel-1 | 10 years | 120 | 3.8 TB | $912/year | $6,000 | $24,000 | 7x |
| CHIRPS | 43 years | 516 | 2.2 TB | $528/year | $6,000 | $24,000 | 11x |
| **ALL DATASETS** | **-** | **1,172** | **12 TB** | **$2,852/year** | **$6,000** | **$24,000** | **2x** |

---

## Part 5: Time Series Composites Comparison

### Mumbai (600 km²) - Time Series

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 781 | 39 GB | $9/year | $6,000 | $24,000 | 667x |
| Landsat 8/9 | 10 years | 650 | 30 GB | $6/year | $6,000 | $24,000 | 1,000x |
| Landsat 7 | 20 years | 1,200 | 55 GB | $12/year | $6,000 | $24,000 | 500x |
| Landsat 4-5 | 30 years | 1,800 | 82 GB | $18/year | $6,000 | $24,000 | 333x |
| MODIS | 24 years | 2,400 | 50 GB | $11/year | $6,000 | $24,000 | 545x |
| Sentinel-1 | 10 years | 650 | 95 GB | $21/year | $6,000 | $24,000 | 286x |
| CHIRPS | 43 years | 3,200 | 130 GB | $29/year | $6,000 | $24,000 | 207x |
| ERA5 | 74 years | 5,500 | 260 GB | $58/year | $6,000 | $24,000 | 103x |
| Land Cover | 5 years | 300 | 18 GB | $3/year | $6,000 | $24,000 | 2,000x |
| DEM (Static) | One-time | 1 | 50 MB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **16,482** | **759 GB** | **$167/year** | **$6,000** | **$24,000** | **36x** |

### Maharashtra (307,713 km²) - Time Series

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 781 | 1.56 TB | $382/year | $6,000 | $24,000 | 16x |
| Landsat 8/9 | 10 years | 650 | 1.2 TB | $288/year | $6,000 | $24,000 | 21x |
| Landsat 7 | 20 years | 1,200 | 2.1 TB | $504/year | $6,000 | $24,000 | 12x |
| Landsat 4-5 | 30 years | 1,800 | 3.2 TB | $768/year | $6,000 | $24,000 | 8x |
| MODIS | 24 years | 2,400 | 1.4 TB | $336/year | $6,000 | $24,000 | 18x |
| Sentinel-1 | 10 years | 650 | 3.8 TB | $912/year | $6,000 | $24,000 | 7x |
| CHIRPS | 43 years | 3,200 | 5.2 TB | $1,248/year | $6,000 | $24,000 | 5x |
| ERA5 | 74 years | 5,500 | 10.4 TB | $2,496/year | $6,000 | $24,000 | 2x |
| Land Cover | 5 years | 300 | 720 GB | $173/year | $6,000 | $24,000 | 35x |
| DEM (Static) | One-time | 1 | 500 MB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **16,482** | **30 TB** | **$7,107/year** | **$6,000** | **$24,000** | **GEE Basic 0.8x (cheaper), GEE Pro 3.4x** |

### India (3,287,263 km²) - Time Series

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 781 | 19.5 TB | $4,719/year | $6,000 | $24,000 | 1.3x |
| Landsat 8/9 | 10 years | 650 | 15 TB | $3,600/year | $6,000 | $24,000 | 1.7x |
| Landsat 7 | 20 years | 1,200 | 27 TB | $6,480/year | $6,000 | $24,000 | GEE cheaper |
| Landsat 4-5 | 30 years | 1,800 | 40.5 TB | $9,720/year | $6,000 | $24,000 | GEE cheaper |
| MODIS | 24 years | 2,400 | 18 TB | $4,320/year | $6,000 | $24,000 | 1.4x |
| Sentinel-1 | 10 years | 650 | 48.75 TB | $11,700/year | $6,000 | $24,000 | GEE cheaper |
| CHIRPS | 43 years | 3,200 | 65 TB | $15,600/year | $6,000 | $24,000 | GEE cheaper |
| ERA5 | 74 years | 5,500 | 130 TB | $31,200/year | $6,000 | $24,000 | GEE cheaper |
| Land Cover | 5 years | 300 | 9 TB | $2,160/year | $6,000 | $24,000 | 2.8x |
| DEM (Static) | One-time | 1 | 5 GB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **16,482** | **373 TB** | **$89,499/year** | **$6,000** | **$24,000** | **GEE is 4-15x cheaper (not recommended)** |

---

## Part 6: Individual Composites Comparison

### Mumbai (600 km²) - Individual Images

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 3,124 | 156 GB | $39/year | $6,000 | $24,000 | 154x |
| Landsat 8/9 | 10 years | 2,600 | 120 GB | $27/year | $6,000 | $24,000 | 222x |
| Landsat 7 | 20 years | 4,800 | 220 GB | $50/year | $6,000 | $24,000 | 120x |
| Landsat 4-5 | 30 years | 7,200 | 330 GB | $75/year | $6,000 | $24,000 | 80x |
| MODIS | 24 years | 9,600 | 200 GB | $45/year | $6,000 | $24,000 | 133x |
| Sentinel-1 | 10 years | 2,600 | 380 GB | $86/year | $6,000 | $24,000 | 70x |
| CHIRPS | 43 years | 12,800 | 520 GB | $118/year | $6,000 | $24,000 | 51x |
| ERA5 | 74 years | 22,000 | 1,040 GB | $236/year | $6,000 | $24,000 | 25x |
| Land Cover | 5 years | 1,200 | 72 GB | $16/year | $6,000 | $24,000 | 375x |
| DEM (Static) | One-time | 1 | 50 MB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **65,925** | **3,038 GB** | **$692/year** | **$6,000** | **$24,000** | **9x (Basic), 35x (Pro)** |

### Maharashtra (307,713 km²) - Individual Images

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 37,450 | 7.49 TB | $2,173/year | $6,000 | $24,000 | 3x |
| Landsat 8/9 | 10 years | 31,200 | 5.76 TB | $1,382/year | $6,000 | $24,000 | 4x |
| Landsat 7 | 20 years | 57,600 | 10.56 TB | $2,534/year | $6,000 | $24,000 | 2x |
| Landsat 4-5 | 30 years | 86,400 | 15.84 TB | $3,802/year | $6,000 | $24,000 | 1.6x |
| MODIS | 24 years | 115,200 | 9.6 TB | $2,304/year | $6,000 | $24,000 | 3x |
| Sentinel-1 | 10 years | 31,200 | 45.76 TB | $10,982/year | $6,000 | $24,000 | GEE cheaper |
| CHIRPS | 43 years | 153,600 | 62.4 TB | $14,976/year | $6,000 | $24,000 | GEE cheaper |
| ERA5 | 74 years | 264,000 | 124.8 TB | $29,952/year | $6,000 | $24,000 | GEE cheaper |
| Land Cover | 5 years | 14,400 | 8.64 TB | $2,074/year | $6,000 | $24,000 | 3x |
| DEM (Static) | One-time | 1 | 500 MB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **791,051** | **290 TB** | **$70,179/year** | **$6,000** | **$24,000** | **GEE is 3-12x cheaper** |

### India (3,287,263 km²) - Individual Images

| Dataset Type | Duration | Files | Size | This Pipeline | GEE Basic | GEE Pro | Savings |
|--------------|----------|-------|------|---------------|-----------|---------|---------|
| Sentinel-2 | 10 years | 273,385 | 68.3 TB | $21,860/year | $6,000 | $24,000 | GEE cheaper |
| Landsat 8/9 | 10 years | 228,000 | 52.5 TB | $12,600/year | $6,000 | $24,000 | GEE cheaper |
| Landsat 7 | 20 years | 420,000 | 96.6 TB | $23,184/year | $6,000 | $24,000 | GEE cheaper |
| Landsat 4-5 | 30 years | 630,000 | 145 TB | $34,800/year | $6,000 | $24,000 | GEE cheaper |
| MODIS | 24 years | 840,000 | 87.6 TB | $21,024/year | $6,000 | $24,000 | GEE cheaper |
| Sentinel-1 | 10 years | 228,000 | 418 TB | $100,320/year | $6,000 | $24,000 | GEE cheaper |
| CHIRPS | 43 years | 1,120,000 | 570 TB | $136,800/year | $6,000 | $24,000 | GEE cheaper |
| ERA5 | 74 years | 1,927,000 | 1,140 TB | $273,600/year | $6,000 | $24,000 | GEE cheaper |
| Land Cover | 5 years | 105,000 | 78.75 TB | $18,900/year | $6,000 | $24,000 | GEE cheaper |
| DEM (Static) | One-time | 1 | 5 GB | $0/year | $6,000 | $24,000 | ∞ |
| **ALL DATASETS** | **-** | **5,771,386** | **2,656 TB** | **$643,088/year** | **$6,000** | **$24,000** | **GEE is 27-107x cheaper** |

---

## Part 7: Cost Summary by Method

### All Methods Cost Comparison

| Region | Method | Files | Storage | Annual Cost | vs GEE Basic | vs GEE Pro |
|--------|--------|-------|---------|-------------|--------------|------------|
| **Mumbai** | Annual | 236 | 13.8 GB | $0 | ∞ | ∞ |
| **Mumbai** | Monthly | 1,172 | 60 GB | $13 | 462x | 1,846x |
| **Mumbai** | Time Series | 16,482 | 759 GB | $167 | 36x | 144x |
| **Mumbai** | Individual | 65,925 | 3.04 TB | $692 | 9x | 35x |
| **Maharashtra** | Annual | 236 | 283 GB | $58 | 103x | 414x |
| **Maharashtra** | Monthly | 1,172 | 1.2 TB | $279 | 22x | 86x |
| **Maharashtra** | Time Series | 16,482 | 30 TB | $7,107 | GEE cheaper | 3.4x |
| **Maharashtra** | Individual | 791,051 | 290 TB | $70,179 | GEE cheaper | GEE cheaper |
| **India** | Annual | 236 | 2.4 TB | $569 | 11x | 42x |
| **India** | Monthly | 1,172 | 12 TB | $2,852 | 2x | 8x |
| **India** | Time Series | 16,482 | 373 TB | $89,499 | GEE cheaper | GEE cheaper |
| **India** | Individual | 5,771,386 | 2,656 TB | $643,088 | GEE cheaper | GEE cheaper |

---