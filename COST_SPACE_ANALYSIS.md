# Sentinel-2 Cost & Space Analysis: Complete Historical Data

## Sentinel-2 Specifications

### Satellite Configuration
- **Satellites**: 2 (Sentinel-2A launched 2015, Sentinel-2B launched 2017)
- **Revisit Time**: 5 days (combined constellation)
- **Per Satellite**: 10-day revisit
- **Availability on GEE**: 
  - Sentinel-2A: June 2015 - Present
  - Sentinel-2B: March 2017 - Present
  - **Total Duration**: ~10.7 years (June 2015 to Feb 2026)

### Image Reality
- **Per Visit**: 1-5 tiles depending on region size
- **Per Year**: 73 visits × 2 satellites × tiles = **146-730 images/year**
- **Compression**: 50-100 MB per composite (with compression)

---

## MUMBAI (600 km²)

### Image Count Analysis
```
Area: 600 km²
Tiles per visit: 1-2 tiles
Satellites: 2
Revisit: 5 days

One Year (2025):
- Visits: 365 ÷ 5 = 73 visits
- Images: 73 × 2 satellites × 2 tiles = 292 images/year

Complete Historical (June 2015 - Feb 2026):
- Duration: 10.7 years
- Total Images: 292 × 10.7 = 3,124 images
```

### Storage & Cost: Complete Historical Data

#### Method 1: Individual Images (All 3,124 images)
```
Images: 3,124
Size per image: ~50 MB (compressed)
Total Size: 3,124 × 50 MB = 156 GB

Storage Cost (GCS):
- First 5GB: FREE
- Remaining 151GB: 151 × $0.02/GB/month = $3.02/month
- Annual: $36.24/year

Processing Cost: 3,124 × $0.001 = $3.12 (one-time)

```

#### Method 2: Monthly Composites (128 months)
```
Duration: 10.7 years = 128 months
Images: 128 composites
Size per composite: ~75 MB (median of ~24 images/month)
Total Size: 128 × 75 MB = 9.6 GB

Storage Cost (GCS):
- First 5GB: FREE
- Remaining 4.6GB: 4.6 × $0.02/GB/month = $0.09/month
- Annual: $1.08/year

Processing Cost: 128 × $0.001 = $0.13 (one-time)

```

#### Method 3: Annual Composites (11 years)
```
Duration: 10.7 years = 11 annual composites
Images: 11 composites
Size per composite: ~100 MB (median of ~292 images/year)
Total Size: 11 × 100 MB = 1.1 GB

Storage Cost: FREE (under 5GB free tier)
Processing Cost: 11 × $0.001 = $0.01 (one-time)

```

#### Method 4: Time Series Download (Individual files per visit)
```
Process: Downloads 1 file per 5-day visit for entire duration
Images: 73 visits/year × 10.7 years = 781 files
Size per file: ~50 MB (composite of 2 satellites × 2 tiles)
Total Size: 781 × 50 MB = 39 GB

Storage Cost (GCS):
- First 5GB: FREE
- Remaining 34GB: 34 × $0.02/GB/month = $0.68/month
- Annual: $8.16/year

Processing Cost: 781 × $0.001 = $0.78 (one-time)


Note: This is essentially the same as "Individual Downloads" but 
creates 1 composite per visit instead of storing all raw tiles.
```

---

## MAHARASHTRA (307,713 km²)

### Image Count Analysis
```
Area: 307,713 km²
Tiles per visit: 15-20 tiles (large state)
Satellites: 2
Revisit: 5 days

One Month (30 days):
- Visits: 30 ÷ 5 = 6 visits
- Images: 6 × 2 satellites × 18 tiles (avg) = 216 images/month
- observation: ~575 images/month ✓ (includes overlaps)

One Year (2025):
- Visits: 73
- Images: 73 × 2 × 18 = 2,628 images/year
- With overlaps: ~3,500 images/year

Complete Historical (June 2015 - Feb 2026):
- Duration: 10.7 years
- Total Images: 3,500 × 10.7 = 37,450 images
```

### Storage & Cost: Complete Historical Data

#### Method 1: Individual Images (All 37,450 images)
```
Images: 37,450
Size per image: ~200 MB (compressed, larger tiles)
Total Size: 37,450 × 200 MB = 7,490 GB (7.49 TB)

Storage Cost (GCS):
- Monthly: 7,490 × $0.02 = $149.80/month
- Annual: $1,797.60/year

Processing Cost: 37,450 × $0.01 = $374.50 (one-time)
```

#### Method 2: Monthly Composites (128 months)
```
Duration: 128 months
Images: 128 composites
Size per composite: ~2 GB (median of ~292 images/month)
Total Size: 128 × 2 GB = 256 GB

Storage Cost (GCS):
- Monthly: 256 × $0.02 = $5.12/month
- Annual: $61.44/year

Processing Cost: 128 × $0.01 = $1.28 (one-time)

```

#### Method 3: Annual Composites (11 years)
```
Duration: 11 years
Images: 11 composites
Size per composite: ~3 GB (median of ~3,500 images/year)
Total Size: 11 × 3 GB = 33 GB

Storage Cost (GCS):
- Monthly: 33 × $0.02 = $0.66/month
- Annual: $7.92/year
- 10-year storage: $79.20

Processing Cost: 11 × $0.01 = $0.11 (one-time)
```

#### Method 4: Time Series Download (Individual files per visit)
```
Process: Downloads 1 file per 5-day visit for entire duration
Images: 73 visits/year × 10.7 years = 781 files
Size per file: ~2 GB (composite of 2 satellites × 18 tiles)
Total Size: 781 × 2 GB = 1,562 GB (1.56 TB)

Storage Cost (GCS):
- Monthly: 1,562 × $0.02 = $31.24/month
- Annual: $374.88/year

Processing Cost: 781 × $0.01 = $7.81 (one-time)
```

---

## INDIA (3,287,263 km²)

### Image Count Analysis
```
Area: 3,287,263 km²
Tiles per visit: 150-200 tiles (entire country)
Satellites: 2
Revisit: 5 days

One Year (2025):
- Visits: 73
- Images: 73 × 2 × 175 tiles (avg) = 25,550 images/year

Complete Historical (June 2015 - Feb 2026):
- Duration: 10.7 years
- Total Images: 25,550 × 10.7 = 273,385 images
```

### Storage & Cost: Complete Historical Data

#### Method 1: Individual Images (All 273,385 images)
```
Images: 273,385
Size per image: ~250 MB (compressed)
Total Size: 273,385 × 250 MB = 68,346 GB (68.3 TB)

Storage Cost (GCS):
- Monthly: 68,346 × $0.02 = $1,366.92/month
- Annual: $16,403.04/year

Processing Cost: 273,385 × $0.02 = $5,467.70 (one-time)
```

#### Method 2: Monthly Composites (128 months)
```
Duration: 128 months
Images: 128 composites
Size per composite: ~20 GB (median of ~2,129 images/month)
Total Size: 128 × 20 GB = 2,560 GB (2.56 TB)

Storage Cost (GCS):
- Monthly: 2,560 × $0.02 = $51.20/month
- Annual: $614.40/year
- 10-year storage: $6,144.00

Processing Cost: 128 × $0.05 = $6.40 (one-time)
```

#### Method 3: Annual Composites (11 years)
```
Duration: 11 years
Images: 11 composites
Size per composite: ~25 GB (median of ~25,550 images/year)
Total Size: 11 × 25 GB = 275 GB

Storage Cost (GCS):
- Monthly: 275 × $0.02 = $5.50/month
- Annual: $66.00/year

Processing Cost: 11 × $0.05 = $0.55 (one-time)
```

#### Method 4: Time Series Download (Individual files per visit)
```
Process: Downloads 1 file per 5-day visit for entire duration
Images: 73 visits/year × 10.7 years = 781 files
Size per file: ~25 GB (composite of 2 satellites × 175 tiles)
Total Size: 781 × 25 GB = 19,525 GB (19.5 TB)

Storage Cost (GCS):
- Monthly: 19,525 × $0.02 = $390.50/month
- Annual: $4,686.00/year

Processing Cost: 781 × $0.05 = $39.05 (one-time)

Note: This is essentially the same as "Individual Downloads" but 
creates 1 composite per visit instead of storing all raw tiles.
```

---

## Complete Historical Data Summary (June 2015 - Feb 2026)

**Total Duration**: 10.7 years of Sentinel-2 data available on Google Earth Engine

---

### PART 1: Download Cost for ALL 10 Years (One-Time)

This is what it costs to download the COMPLETE 10.7 years of historical data ONCE.

#### Mumbai (600 km²)

| Method | Total Files | Total Size | Download Cost |
|--------|-------------|------------|---------------|
| Individual (all tiles) | 3,124 images | 156 GB | **$3.12** |
| Time Series (per visit) | 781 files | 39 GB | **$0.78** |
| Monthly Composites | 128 files | 9.6 GB | **$0.13** |
| Annual Composites | 11 files | 1.1 GB | **$0.01** |

#### Maharashtra (307,713 km²)

| Method | Total Files | Total Size | Download Cost |
|--------|-------------|------------|---------------|
| Individual (all tiles) | 37,450 images | 7.49 TB | **$374.50** |
| Time Series (per visit) | 781 files | 1.56 TB | **$7.81** |
| Monthly Composites | 128 files | 256 GB | **$1.28** |
| Annual Composites | 11 files | 33 GB | **$0.11** |

#### India (3,287,263 km²)

| Method | Total Files | Total Size | Download Cost |
|--------|-------------|------------|---------------|
| Individual (all tiles) | 273,385 images | 68.3 TB | **$5,467.70** |
| Time Series (per visit) | 781 files | 19.5 TB | **$39.05** |
| Monthly Composites | 128 files | 2.56 TB | **$6.40** |
| Annual Composites | 11 files | 275 GB | **$0.55** |

---

### PART 2: Storage Cost (Ongoing After Download)

After downloading all 10 years of data, this is what it costs to KEEP it stored.

#### Mumbai Storage Costs

| Method | Size | 1 Month | 5 Months | 1 Year |
|--------|------|---------|----------|--------|
| Individual | 156 GB | $3.12 | $15.60 | $37.44 |
| Time Series | 39 GB | $0.78 | $3.90 | $9.36 |
| Monthly | 9.6 GB | $0.19 | $0.95 | $2.28 |
| Annual | 1.1 GB | $0.02 | $0.10 | $0.24 |

#### Maharashtra Storage Costs

| Method | Size | 1 Month | 5 Months | 1 Year |
|--------|------|---------|----------|--------|
| Individual | 7.49 TB | $149.80 | $749.00 | $1,797.60 |
| Time Series | 1.56 TB | $31.20 | $156.00 | $374.40 |
| Monthly | 256 GB | $5.12 | $25.60 | $61.44 |
| Annual | 33 GB | $0.66 | $3.30 | $7.92 |

#### India Storage Costs

| Method | Size | 1 Month | 5 Months | 1 Year |
|--------|------|---------|----------|--------|
| Individual | 68.3 TB | $1,366.00 | $6,830.00 | $16,392.00 |
| Time Series | 19.5 TB | $390.00 | $1,950.00 | $4,680.00 |
| Monthly | 2.56 TB | $51.20 | $256.00 | $614.40 |
| Annual | 275 GB | $5.50 | $27.50 | $66.00 |

---

### PART 3: Total Cost (Download + Storage)

#### Mumbai - Total Cost

| Method | Size | Download | +1 Month | +5 Months | +1 Year |
|--------|------|----------|----------|-----------|---------|
| Individual | 156 GB | $3.12 | $6.24 | $18.72 | $40.56 |
| Time Series | 39 GB | $0.78 | $1.56 | $4.68 | $10.14 |
| Monthly | 9.6 GB | $0.13 | $0.32 | $1.08 | $2.41 |
| Annual | 1.1 GB | $0.01 | $0.03 | $0.11 | $0.25 |

#### Maharashtra - Total Cost

| Method | Size | Download | +1 Month | +5 Months | +1 Year |
|--------|------|----------|----------|-----------|---------|
| Individual | 7.49 TB | $374.50 | $524.30 | $1,123.50 | $2,172.10 |
| Time Series | 1.56 TB | $7.81 | $39.01 | $163.81 | $382.21 |
| Monthly | 256 GB | $1.28 | $6.40 | $26.88 | $62.72 |
| Annual | 33 GB | $0.11 | $0.77 | $3.41 | $8.03 |

#### India - Total Cost

| Method | Size | Download | +1 Month | +5 Months | +1 Year |
|--------|------|----------|----------|-----------|---------|
| Individual | 68.3 TB | $5,467.70 | $6,833.70 | $12,297.70 | $21,859.70 |
| Time Series | 19.5 TB | $39.05 | $429.05 | $1,989.05 | $4,719.05 |
| Monthly | 2.56 TB | $6.40 | $57.60 | $262.40 | $620.80 |
| Annual | 275 GB | $0.55 | $6.05 | $28.05 | $66.55 |

---

## Google Earth Engine Commercial License Comparison

### GEE Pricing Tiers

#### 1. Free Tier (Non-Commercial)
- **Cost**: $0/month
- **Use Cases**: Research, education, non-profit
- **Limits**: 
  - Reasonable usage limits (not publicly specified)
  - No SLA guarantees
  - Community support only
- **Storage**: 250 GB Cloud Storage assets
- **Compute**: Limited concurrent tasks

#### 2. Commercial License
**Pricing**: Two tiers available

**Basic Plan**: $500/month ($6,000/year)
- 2 developer seats
- 20 concurrent high-volume API requests
- 8 concurrent batch export tasks
- Community support

**Professional Plan**: $2,000/month ($24,000/year)
- 5 developer seats
- 500 concurrent high-volume API requests
- 20 concurrent batch export tasks
- 99.5% uptime SLA
- Priority technical support

**Additional Usage Charges**:
```
Compute: $0.40 per EECU-hour (batch processing)
Storage: $0.026/GB/month (30% more than GCS)
Egress: $0.12/GB (data transfer out)
```

**Note**: Monthly subscription + usage charges apply

---

## Cost Comparison: This Pipeline vs GEE Commercial

### Scenario 1: Mumbai (Complete Historical Data)

#### This Pipeline (Download & Store 1 Year)
```
Method: Monthly Composites (128 files, 9.6 GB)
Download Cost: $0.13
Storage (1 year): $2.28
TOTAL: $2.41
```

#### GEE Commercial Basic Plan (Process in Cloud)
```
Approach: Compute statistics/indices in GEE, export only results
Base Fee: $500/month × 12 months = $6,000
Compute: ~10 EECU-hours × $0.40 = $4
Storage: Results only (~1 GB) × $0.026/month × 12 = $0.31
Export: 1 GB × $0.12 = $0.12
TOTAL: $6,004.43

⚠️ 2,491x more expensive than this pipeline
```

#### GEE Commercial Professional Plan
```
Base Fee: $2,000/month × 12 months = $24,000
Compute: $4
Storage: $0.31
Export: $0.12
TOTAL: $24,004.43

⚠️ 9,961x more expensive than this pipeline
```

#### GEE Free Tier (Process in Cloud)
```
Approach: Same as commercial, but free tier
Cost: $0 (FREE)
Limitation: Must be non-commercial use

TOTAL: FREE
```

---

### Scenario 2: Maharashtra (Complete Historical Data)

#### This Pipeline (Download & Store 1 Year)
```
Method: Monthly Composites (128 files, 256 GB)
Download Cost: $1.28
Storage (1 year): $61.44
TOTAL: $62.72
```

#### GEE Commercial Basic Plan (Process in Cloud)
```
Approach: Compute monthly composites in GEE, export results
Base Fee: $500/month × 12 months = $6,000
Compute: ~50 EECU-hours × $0.40 = $20
Storage: 256 GB × $0.026/month × 12 = $79.87
Export: 256 GB × $0.12 = $30.72
TOTAL: $6,130.59

⚠️ 98x more expensive than this pipeline
```

#### GEE Commercial Professional Plan
```
Base Fee: $2,000/month × 12 months = $24,000
Compute: $20
Storage: $79.87
Export: $30.72
TOTAL: $24,130.59

⚠️ 385x more expensive than this pipeline
```

#### GEE Free Tier (Process in Cloud)
```
Approach: Same as commercial, but free tier
Storage: 256 GB × $0.02/month × 12 = $61.44
Export: 256 GB × $0.12 = $30.72
TOTAL: $92.16

Note: Slightly more expensive than this pipeline due to egress fees
```

---

### Scenario 3: India (Complete Historical Data)

#### This Pipeline (Download & Store 1 Year)
```
Method: Annual Composites (11 files, 275 GB)
Download Cost: $0.55
Storage (1 year): $66.00
TOTAL: $66.55
```

#### GEE Commercial Basic Plan (Process in Cloud)
```
Approach: Compute annual composites in GEE, export results
Base Fee: $500/month × 12 months = $6,000
Compute: ~100 EECU-hours × $0.40 = $40
Storage: 275 GB × $0.026/month × 12 = $85.80
Export: 275 GB × $0.12 = $33.00
TOTAL: $6,158.80

⚠️ 93x more expensive than this pipeline
```

#### GEE Commercial Professional Plan
```
Base Fee: $2,000/month × 12 months = $24,000
Compute: $40
Storage: $85.80
Export: $33.00
TOTAL: $24,158.80

⚠️ 363x more expensive than this pipeline
```

#### GEE Free Tier (Process in Cloud)
```
Approach: Same as commercial, but free tier
Storage: 275 GB × $0.02/month × 12 = $66.00
Export: 275 GB × $0.12 = $33.00
TOTAL: $99.00

Note: Slightly more expensive than this pipeline due to egress fees
```

---

### Scenario 4: Statistical Analysis Only (No Image Downloads)

#### This Pipeline
```
Not applicable - pipeline is designed for image downloads
```

#### GEE Commercial Basic Plan
```
Approach: Compute NDVI trends, statistics, charts in GEE
Base Fee: $500/month × 12 months = $6,000
Compute: ~20 EECU-hours × $0.40 = $8
Export: Statistics only (~100 MB) × $0.12 = $0.01
TOTAL: $6,008.01

⚠️ Only makes sense for enterprise with many projects
```

#### GEE Commercial Professional Plan
```
Base Fee: $2,000/month × 12 months = $24,000
Compute: $8
Export: $0.01
TOTAL: $24,008.01

⚠️ Only for large enterprises
```

#### GEE Free Tier
```
Approach: Same as commercial, but free tier
Export: Statistics only (~100 MB) = $0.01
TOTAL: $0.01 (essentially FREE)

✅ Best option for statistical analysis
```

---
