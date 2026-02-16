# GEE Data Pipeline: Cost Comparison Across All Datasets

## Overview
This pipeline provides access to **142+ Google Earth Engine datasets** with zero configuration. 

**Important**: This pipeline uses **GEE Non-Commercial (Free) Tier** which has usage limits. Compare actual costs below.

## Dataset Coverage

### Available Datasets (142+)
- **Optical**: Sentinel-2, Landsat 4-9, MODIS Terra/Aqua
- **Radar**: Sentinel-1, ALOS PALSAR
- **Climate**: CHIRPS, ERA5, GRIDMET, TerraClimate
- **Land Cover**: ESA WorldCover, MODIS Land Cover, Dynamic World
- **Elevation**: SRTM, ASTER GDEM, NASADEM
- **Ocean**: Sea Surface Temperature, Chlorophyll, Salinity
- **Atmospheric**: Aerosols, NO2, CO, Ozone
- **Vegetation**: NDVI, EVI, LAI, FPAR
- **Temperature**: Land/Sea Surface Temperature, Air Temperature
- **Precipitation**: Daily/Monthly rainfall, Snow cover
- **And 100+ more datasets**

## Cost Comparison: This Pipeline vs GEE Commercial

### This Pipeline Costs (Non-Commercial Free Tier)

**GEE Non-Commercial Tier**:
- ✅ **FREE** for research, education, non-profit
- ⚠️ **Usage Limits** (not publicly specified, but reasonable)
- ⚠️ **No commercial use** allowed
- ⚠️ **No SLA guarantees**
- Storage: 250 GB Cloud Storage assets (FREE)
- Compute: Limited concurrent tasks (FREE within limits)

**If You Exceed Free Tier or Need Commercial Use**:
- Must upgrade to GEE Commercial License ($500-$2,000/month base fee)
- OR pay per-use without subscription (not officially available)

**GCS Storage (Your exports)**:
- ✅ **FREE tier**: 5GB storage/month
- After 5GB: $0.02/GB/month
- Operations: 5,000 Class A operations/month FREE

**Google Drive (Alternative export)**:
- ✅ **FREE**: 15GB storage included
- After 15GB: $1.99/month for 100GB (Google One)

**Actual Costs for This Pipeline**:
- **Within free tiers**: $0/month
- **After free tier**: $0.02/GB/month (GCS only)
- **No base fees**: Unlike GEE Commercial

### GEE Commercial License Pricing

**Basic Plan**: $500/month ($6,000/year)
- 2 developer seats
- 20 concurrent API requests
- 8 concurrent batch exports
- Community support

**Professional Plan**: $2,000/month ($24,000/year)
- 5 developer seats
- 500 concurrent API requests
- 20 concurrent batch exports
- 99.5% uptime SLA
- Priority support

**Additional Usage Charges**:
- Compute: $0.40 per EECU-hour
- Storage: $0.026/GB/month
- Egress: $0.12/GB

### This Pipeline Costs

**Download Cost**: $0 (FREE - within GEE non-commercial limits)
**Storage Cost**: 
- First 5GB: $0 (FREE - GCS free tier)
- After 5GB: $0.02/GB/month (GCS Standard)
**Drive Alternative**: 
- First 15GB: $0 (FREE)
- After 15GB: $1.99/month for 100GB

**⚠️ Important Limitations**:
- GEE Free Tier is for **non-commercial use only**
- Usage limits apply (not publicly specified)
- If you exceed limits or need commercial use → Must pay GEE Commercial License

## Cost Examples by Dataset Type

**Note**: All costs assume you stay within GEE non-commercial free tier limits. Storage costs are for GCS (after 5GB free tier).

### High-Resolution Optical (Sentinel-2, Landsat)

| Region | Method | Size | This Pipeline (Storage Only) | GEE Basic | GEE Pro | Savings |
|--------|--------|------|------------------------------|-----------|---------|---------|
| City (600 km²) | Annual (10yr) | 1.1 GB | $0 (under 5GB) | $6,004 | $24,004 | ∞ |
| State (300k km²) | Annual (10yr) | 33 GB | $7/year | $6,131 | $24,131 | 876x |
| Country (3M km²) | Annual (10yr) | 275 GB | $65/year | $6,159 | $24,159 | 95x |

### Medium-Resolution (MODIS, 250m-1km)

| Region | Method | Size | This Pipeline (Storage Only) | GEE Basic | GEE Pro | Savings |
|--------|--------|------|------------------------------|-----------|---------|---------|
| City | Annual (20yr) | 500 MB | $0 (under 5GB) | $6,002 | $24,002 | ∞ |
| State | Annual (20yr) | 8 GB | $1/year | $6,020 | $24,020 | 6,020x |
| Country | Annual (20yr) | 80 GB | $18/year | $6,080 | $24,080 | 338x |

### Climate Data (CHIRPS, ERA5, Daily)

| Region | Method | Size | This Pipeline (Storage Only) | GEE Basic | GEE Pro | Savings |
|--------|--------|------|------------------------------|-----------|---------|---------|
| City | Monthly (40yr) | 2 GB | $0 (under 5GB) | $6,005 | $24,005 | ∞ |
| State | Monthly (40yr) | 15 GB | $2/year | $6,030 | $24,030 | 3,015x |
| Country | Monthly (40yr) | 120 GB | $28/year | $6,150 | $24,150 | 220x |

### Radar (Sentinel-1, SAR)

| Region | Method | Size | This Pipeline (Storage Only) | GEE Basic | GEE Pro | Savings |
|--------|--------|------|------------------------------|-----------|---------|---------|
| City | Annual (8yr) | 3 GB | $0 (under 5GB) | $6,008 | $24,008 | ∞ |
| State | Annual (8yr) | 40 GB | $8/year | $6,050 | $24,050 | 756x |
| Country | Annual (8yr) | 350 GB | $83/year | $6,185 | $24,185 | 75x |

### Static Datasets (Elevation, Land Cover)

| Dataset | Size | This Pipeline (Storage Only) | GEE Basic | GEE Pro | Savings |
|---------|------|------------------------------|-----------|---------|---------|
| City DEM | 50 MB | $0 (under 5GB) | $6,000 | $24,000 | ∞ |
| State DEM | 500 MB | $0 (under 5GB) | $6,001 | $24,001 | ∞ |
| Country DEM | 5 GB | $0 (at free tier limit) | $6,010 | $24,010 | ∞ |

## When to Use Each Option

### Use This Pipeline When:
✅ **Non-commercial use** (research, education, non-profit)  
✅ Downloading complete datasets for offline analysis  
✅ Need exact regional boundaries (no neighboring pixels)  
✅ Budget-conscious projects ($0-$100/year for storage only)  
✅ Small teams (1-3 developers)  
✅ One-time or periodic downloads  
✅ Local processing with QGIS/Python/R  
✅ Stay within GEE free tier usage limits  

### Use GEE Commercial When:
✅ **Commercial use required**  
✅ Exceed GEE free tier usage limits  
✅ Real-time cloud processing at scale  
✅ Statistical analysis only (no image downloads)  
✅ Enterprise with 5+ developers  
✅ Need 99.5% uptime SLA  
✅ Continuous automated workflows  
✅ Priority technical support required  

### Use GEE Free Tier (Cloud Processing) When:
✅ **Non-commercial** research/education  
✅ Statistical analysis in cloud (no downloads)  
✅ Stay within usage limits  
✅ **Cost: $0 (completely FREE)**  

**⚠️ Critical**: If your use case is commercial OR you exceed free tier limits, you MUST upgrade to GEE Commercial License.  

## Cost Breakdown by Use Case

**Note**: Assumes non-commercial use within GEE free tier. Only storage costs apply.

### Research Project (1 Year)
**Scenario**: Download 5 datasets, 3 regions, monthly composites

| Component | This Pipeline | GEE Basic | GEE Pro |
|-----------|---------------|-----------|---------|
| Base Fee | $0 | $6,000 | $24,000 |
| GEE Processing | $0 (free tier) | $0 | $0 |
| Storage (50 GB) | $11/year | $16/year | $16/year |
| **TOTAL** | **$11/year** | **$6,016/year** | **$24,016/year** |
| **Savings** | **-** | **547x** | **2,183x** |

### Commercial Monitoring (1 Year)
**Scenario**: 10 regions, weekly updates, 3 datasets

⚠️ **Commercial use = Must use GEE Commercial License**

| Component | This Pipeline | GEE Basic | GEE Pro |
|-----------|---------------|-----------|---------|
| Base Fee | N/A (not allowed) | $6,000 | $24,000 |
| GEE Processing | N/A | $0 | $0 |
| Storage (500 GB) | $118/year | $156/year | $156/year |
| **TOTAL** | **Not Allowed** | **$6,156/year** | **$24,156/year** |

**For commercial use, you MUST use GEE Commercial License.**

### Enterprise Multi-Project (1 Year)
**Scenario**: 50 regions, daily processing, 10 datasets

⚠️ **Commercial + High usage = Must use GEE Commercial License**

| Component | This Pipeline | GEE Basic | GEE Pro |
|-----------|---------------|-----------|---------|
| Base Fee | N/A (not allowed) | $6,000 | $24,000 |
| GEE Processing | N/A | $100 | $100 |
| Storage (5 TB) | $1,188/year | $1,560/year | $1,560/year |
| **TOTAL** | **Not Allowed** | **$7,660/year** | **$25,660/year** |

**For enterprise/commercial use, you MUST use GEE Commercial License.**

## Dataset-Specific Considerations

### High-Frequency Datasets (Daily)
- **Sentinel-2**: 5-day revisit → 73 images/year
- **Landsat 8/9**: 16-day revisit → 23 images/year
- **MODIS**: Daily → 365 images/year
- **CHIRPS**: Daily precipitation → 365 images/year

**Recommendation**: Use monthly/annual composites to reduce size 10-30x

### Long Historical Archives
- **Landsat**: 1984-present (40+ years)
- **MODIS**: 2000-present (24+ years)
- **CHIRPS**: 1981-present (43+ years)
- **ERA5**: 1950-present (74+ years)

**Recommendation**: Download annual composites for complete history

### Large Spatial Coverage
- **Global datasets**: Use country/continent boundaries
- **Continental**: Use state/province boundaries
- **Regional**: Use city/district boundaries

**Recommendation**: Smaller regions = faster downloads + lower costs

## Storage Optimization Tips

### Reduce Storage Costs by 10-100x:
1. **Use Composites**: Monthly/annual instead of individual images
2. **Delete After Processing**: Download → Process → Delete source
3. **Compress Data**: LZW compression (3-5x smaller)
4. **Select Bands**: Download only needed bands (e.g., RGB instead of all 13)
5. **Temporal Filtering**: Download specific date ranges, not entire archive

### Example Savings:
| Method | Size | Cost/Year | Savings |
|--------|------|-----------|---------|
| All individual images | 7.5 TB | $1,800 | - |
| Monthly composites | 256 GB | $61 | 30x |
| Annual composites | 33 GB | $8 | 225x |
| Selected bands only | 11 GB | $3 | 600x |

## Key Advantages of This Pipeline

### Cost Efficiency
- **No base fees**: Pay only for what you use
- **No minimum commitment**: Start/stop anytime
- **Predictable costs**: Calculate exact costs before download

### Data Control
- **Offline access**: No internet needed after download
- **Exact boundaries**: Perfect regional clipping
- **Original data**: Preserved metadata and values
- **Local processing**: Use any tool (QGIS, Python, R, MATLAB)

### Flexibility
- **142+ datasets**: Works with ANY GEE dataset
- **Zero configuration**: Auto-detects all parameters
- **Custom regions**: Countries, states, cities, or custom polygons
- **Any time range**: Historical archives to near real-time

## Conclusion

### Cost Comparison Summary (Non-Commercial Use Only)

**This Pipeline**:
- GEE Processing: **$0** (free tier)
- Storage: **$0-$100/year** (depends on data size)
- Total: **$0-$100/year** for most research projects

**GEE Commercial**:
- Base Fee: **$6,000-$24,000/year**
- Plus usage charges
- Total: **$6,000+/year**

**Savings**: **60-∞x cheaper** for non-commercial research

### Important Limitations

**This Pipeline Requires**:
- ⚠️ **Non-commercial use only** (research, education, non-profit)
- ⚠️ **Stay within GEE free tier limits** (not publicly specified)
- ⚠️ **No SLA guarantees**
- ⚠️ **Community support only**

**If You Need Commercial Use**:
- You MUST upgrade to GEE Commercial License ($6,000-$24,000/year)
- This pipeline cannot be used for commercial purposes

**If You Exceed Free Tier**:
- You MUST upgrade to GEE Commercial License
- OR reduce usage to stay within limits

### When This Pipeline Saves Most Money
✅ **Non-commercial** research/education projects  
✅ Downloading complete image datasets  
✅ Offline analysis requirements  
✅ Budget-conscious academic projects  
✅ Small research teams  
✅ Periodic (not continuous) processing  
✅ Stay within free tier limits  

### When GEE Commercial Is Required
✅ **Any commercial use**  
✅ Exceed GEE free tier usage limits  
✅ Enterprise with 5+ developers  
✅ Need 99.5% uptime SLA  
✅ Continuous automated workflows  
✅ Priority technical support  

---

**Bottom Line**: 

For **non-commercial research** downloading satellite imagery:
- This pipeline: **$0-$100/year** (storage only)
- GEE Commercial: **$6,000-$24,000/year** (base fee + usage)
- **Savings: 60-∞x**

For **commercial use**:
- This pipeline: **Not allowed**
- GEE Commercial: **Required** ($6,000-$24,000/year)

**Your actual costs with this pipeline**:
- GEE processing: $0 (free tier)
- GCS storage: $0 for first 5GB, then $0.02/GB/month
- Google Drive: $0 for first 15GB, then $1.99/month for 100GB
- **Total: $0-$100/year for typical research use**
