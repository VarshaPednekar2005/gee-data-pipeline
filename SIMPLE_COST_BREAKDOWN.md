# Simple Cost & Space Breakdown

## Two Separate Questions Answered

### Question 1: What does it cost to DOWNLOAD all 10 years of data?
### Question 2: What does it cost to STORE that data for 10 or 20 years?

---

## PART 1: Download Cost & Space (One-Time)

**Dataset**: Sentinel-2 (COPERNICUS/S2_SR_HARMONIZED)
**Duration**: 10.7 years (June 2015 - Feb 2026)

### Mumbai (600 km²)

| Method | Files | Total Size | Download Cost (One-Time) |
|--------|-------|------------|--------------------------|
| Individual (all tiles) | 3,124 | 156 GB | $3.12 |
| Time Series (per visit) | 781 | 39 GB | $0.78 |
| Monthly Composites | 128 | 9.6 GB | $0.13 |
| Annual Composites | 11 | 1.1 GB | $0.01 |

### Maharashtra (307,713 km²)

| Method | Files | Total Size | Download Cost (One-Time) |
|--------|-------|------------|--------------------------|
| Individual (all tiles) | 37,450 | 7.49 TB | $374.50 |
| Time Series (per visit) | 781 | 1.56 TB | $7.81 |
| Monthly Composites | 128 | 256 GB | $1.28 |
| Annual Composites | 11 | 33 GB | $0.11 |

### India (3,287,263 km²)

| Method | Files | Total Size | Download Cost (One-Time) |
|--------|-------|------------|--------------------------|
| Individual (all tiles) | 273,385 | 68.3 TB | $5,467.70 |
| Time Series (per visit) | 781 | 19.5 TB | $39.05 |
| Monthly Composites | 128 | 2.56 TB | $6.40 |
| Annual Composites | 11 | 275 GB | $0.55 |

---

## PART 2: Storage Cost (Ongoing)

**After downloading, how much does it cost to KEEP the data stored?**

### Storage Rate: $0.02/GB/month (Google Cloud Storage)

---

### Mumbai Storage Costs

#### Individual (all tiles): 156 GB
```
Monthly: 156 GB × $0.02 = $3.12/month
Year 1: $3.12 × 12 = $37.44
Year 10: $37.44 × 10 = $374.40
Year 20: $37.44 × 20 = $748.80
```

#### Time Series (per visit): 39 GB
```
Monthly: 39 GB × $0.02 = $0.78/month
Year 1: $0.78 × 12 = $9.36
Year 10: $9.36 × 10 = $93.60
Year 20: $9.36 × 20 = $187.20
```

#### Monthly Composites: 9.6 GB
```
Monthly: 9.6 GB × $0.02 = $0.19/month
Year 1: $0.19 × 12 = $2.28
Year 10: $2.28 × 10 = $22.80
Year 20: $2.28 × 20 = $45.60
```

#### Annual Composites: 1.1 GB
```
Monthly: 1.1 GB × $0.02 = $0.02/month
Year 1: $0.02 × 12 = $0.24
Year 10: $0.24 × 10 = $2.40
Year 20: $0.24 × 20 = $4.80
```

---

### Maharashtra Storage Costs

#### Individual (all tiles): 7.49 TB (7,490 GB)
```
Monthly: 7,490 GB × $0.02 = $149.80/month
Year 1: $149.80 × 12 = $1,797.60
Year 10: $1,797.60 × 10 = $17,976.00
Year 20: $1,797.60 × 20 = $35,952.00
```

#### Time Series (per visit): 1.56 TB (1,560 GB)
```
Monthly: 1,560 GB × $0.02 = $31.20/month
Year 1: $31.20 × 12 = $374.40
Year 10: $374.40 × 10 = $3,744.00
Year 20: $374.40 × 20 = $7,488.00
```

#### Monthly Composites: 256 GB
```
Monthly: 256 GB × $0.02 = $5.12/month
Year 1: $5.12 × 12 = $61.44
Year 10: $61.44 × 10 = $614.40
Year 20: $61.44 × 20 = $1,228.80
```

#### Annual Composites: 33 GB
```
Monthly: 33 GB × $0.02 = $0.66/month
Year 1: $0.66 × 12 = $7.92
Year 10: $7.92 × 10 = $79.20
Year 20: $7.92 × 20 = $158.40
```

---

### India Storage Costs

#### Individual (all tiles): 68.3 TB (68,300 GB)
```
Monthly: 68,300 GB × $0.02 = $1,366.00/month
Year 1: $1,366.00 × 12 = $16,392.00
Year 10: $16,392.00 × 10 = $163,920.00
Year 20: $16,392.00 × 20 = $327,840.00
```

#### Time Series (per visit): 19.5 TB (19,500 GB)
```
Monthly: 19,500 GB × $0.02 = $390.00/month
Year 1: $390.00 × 12 = $4,680.00
Year 10: $4,680.00 × 10 = $46,800.00
Year 20: $4,680.00 × 20 = $93,600.00
```

#### Monthly Composites: 2.56 TB (2,560 GB)
```
Monthly: 2,560 GB × $0.02 = $51.20/month
Year 1: $51.20 × 12 = $614.40
Year 10: $614.40 × 10 = $6,144.00
Year 20: $614.40 × 20 = $12,288.00
```

#### Annual Composites: 275 GB
```
Monthly: 275 GB × $0.02 = $5.50/month
Year 1: $5.50 × 12 = $66.00
Year 10: $66.00 × 10 = $660.00
Year 20: $66.00 × 20 = $1,320.00
```

---

## PART 3: Total Cost (Download + Storage)

### Mumbai - Total Cost

| Method | Size | Download | 10-Year Storage | 20-Year Storage | Total (10Y) | Total (20Y) |
|--------|------|----------|-----------------|-----------------|-------------|-------------|
| Individual | 156 GB | $3.12 | $374.40 | $748.80 | $377.52 | $751.92 |
| Time Series | 39 GB | $0.78 | $93.60 | $187.20 | $94.38 | $187.98 |
| Monthly | 9.6 GB | $0.13 | $22.80 | $45.60 | $22.93 | $45.73 |
| Annual | 1.1 GB | $0.01 | $2.40 | $4.80 | $2.41 | $4.81 |

### Maharashtra - Total Cost

| Method | Size | Download | 10-Year Storage | 20-Year Storage | Total (10Y) | Total (20Y) |
|--------|------|----------|-----------------|-----------------|-------------|-------------|
| Individual | 7.49 TB | $374.50 | $17,976.00 | $35,952.00 | $18,350.50 | $36,326.50 |
| Time Series | 1.56 TB | $7.81 | $3,744.00 | $7,488.00 | $3,751.81 | $7,495.81 |
| Monthly | 256 GB | $1.28 | $614.40 | $1,228.80 | $615.68 | $1,230.08 |
| Annual | 33 GB | $0.11 | $79.20 | $158.40 | $79.31 | $158.51 |

### India - Total Cost

| Method | Size | Download | 10-Year Storage | 20-Year Storage | Total (10Y) | Total (20Y) |
|--------|------|----------|-----------------|-----------------|-------------|-------------|
| Individual | 68.3 TB | $5,467.70 | $163,920.00 | $327,840.00 | $169,387.70 | $333,207.70 |
| Time Series | 19.5 TB | $39.05 | $46,800.00 | $93,600.00 | $46,839.05 | $93,639.05 |
| Monthly | 2.56 TB | $6.40 | $6,144.00 | $12,288.00 | $6,150.40 | $12,294.40 |
| Annual | 275 GB | $0.55 | $660.00 | $1,320.00 | $660.55 | $1,320.55 |

---

## Summary Tables

### Download Only (One-Time Cost)

| Region | Individual | Time Series | Monthly | Annual |
|--------|-----------|-------------|---------|--------|
| **Mumbai** | $3.12 (156 GB) | $0.78 (39 GB) | $0.13 (9.6 GB) | $0.01 (1.1 GB) |
| **Maharashtra** | $374.50 (7.49 TB) | $7.81 (1.56 TB) | $1.28 (256 GB) | $0.11 (33 GB) |
| **India** | $5,467.70 (68.3 TB) | $39.05 (19.5 TB) | $6.40 (2.56 TB) | $0.55 (275 GB) |

### 10-Year Storage Cost

| Region | Individual | Time Series | Monthly | Annual |
|--------|-----------|-------------|---------|--------|
| **Mumbai** | $374.40 | $93.60 | $22.80 | $2.40 |
| **Maharashtra** | $17,976.00 | $3,744.00 | $614.40 | $79.20 |
| **India** | $163,920.00 | $46,800.00 | $6,144.00 | $660.00 |

### 20-Year Storage Cost

| Region | Individual | Time Series | Monthly | Annual |
|--------|-----------|-------------|---------|--------|
| **Mumbai** | $748.80 | $187.20 | $45.60 | $4.80 |
| **Maharashtra** | $35,952.00 | $7,488.00 | $1,228.80 | $158.40 |
| **India** | $327,840.00 | $93,600.00 | $12,288.00 | $1,320.00 |

### Total Cost (Download + 10-Year Storage)

| Region | Individual | Time Series | Monthly | Annual |
|--------|-----------|-------------|---------|--------|
| **Mumbai** | $377.52 | $94.38 | $22.93 | $2.41 |
| **Maharashtra** | $18,350.50 | $3,751.81 | $615.68 | $79.31 |
| **India** | $169,387.70 | $46,839.05 | $6,150.40 | $660.55 |

### Total Cost (Download + 20-Year Storage)

| Region | Individual | Time Series | Monthly | Annual |
|--------|-----------|-------------|---------|--------|
| **Mumbai** | $751.92 | $187.98 | $45.73 | $4.81 |
| **Maharashtra** | $36,326.50 | $7,495.81 | $1,230.08 | $158.51 |
| **India** | $333,207.70 | $93,639.05 | $12,294.40 | $1,320.55 |

---

## Key Insights

### 1. Download Cost is Minimal
- Mumbai: $0.01 - $3.12 (one-time)
- Maharashtra: $0.11 - $374.50 (one-time)
- India: $0.55 - $5,467.70 (one-time)

### 2. Storage Cost Dominates Long-Term
- 10-year storage costs 100-1000x more than download
- 20-year storage costs 200-2000x more than download

### 3. Composites Save Massive Costs
**Maharashtra Example**:
- Individual: $18,350 (10 years)
- Monthly: $616 (10 years) - **30x cheaper**
- Annual: $79 (10 years) - **232x cheaper**

### 4. Storage Cost is Linear
- 10 years = X
- 20 years = 2X
- 30 years = 3X

### 5. Recommended Approach
**For most users**: Download monthly/annual composites, process, delete raw data
- Download: $0.11 - $6.40
- Keep processed results only (1% of size)
- Avoid long-term raw data storage

**For permanent archives**: Use annual composites
- Mumbai: $2.41 (10 years)
- Maharashtra: $79.31 (10 years)
- India: $660.55 (10 years)

---

## Comparison with GEE Commercial

### 10-Year Total Cost Comparison

| Region | This Pipeline (Annual) | GEE Free Tier | GEE Basic | GEE Professional |
|--------|------------------------|---------------|-----------|------------------|
| **Mumbai** | $2.41 | FREE | $60,000 | $240,000 |
| **Maharashtra** | $79.31 | $93 | $60,093 | $240,093 |
| **India** | $660.55 | $693 | $60,931 | $240,931 |

**Conclusion**: This pipeline with annual composites is the most cost-effective for downloading and storing complete historical data, unless you can use GEE Free Tier for statistical analysis only (no image downloads).
