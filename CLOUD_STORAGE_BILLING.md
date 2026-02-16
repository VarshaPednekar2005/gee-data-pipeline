# Cloud Storage Billing Explained

## How Cloud Storage Charges Work

### Google Cloud Storage (GCS) Billing Model

**Storage is charged PER DAY, billed MONTHLY**

```
Charge = (Data Size in GB) × (Days Stored) × (Daily Rate)
Daily Rate = Monthly Rate / 30 days
Monthly Rate = $0.02/GB/month
```

### Example: Maharashtra Data (256 GB)

#### If you store for 1 day:
```
256 GB × 1 day × ($0.02 / 30 days) = $0.17
```

#### If you store for 7 days:
```
256 GB × 7 days × ($0.02 / 30 days) = $1.19
```

#### If you store for 30 days (1 month):
```
256 GB × 30 days × ($0.02 / 30 days) = $5.12
```

#### If you store for 365 days (1 year):
```
256 GB × 12 months × $0.02 = $61.44
```

---

## There is NO "Free Storage Period"

**Important**: Cloud storage charges start **immediately** when you upload data.

### Timeline:
```
Day 1: Upload 256 GB → Charges start immediately
Day 2: Still stored → Charged for 2 days
Day 7: Still stored → Charged for 7 days
Day 30: Still stored → Charged for 30 days (billed at month end)
Day 31: Delete data → Charges stop
```

### Monthly Billing Cycle:
```
Upload: February 5, 2026
Delete: February 12, 2026
Storage Duration: 7 days
Bill Date: March 1, 2026
Amount: 256 GB × 7 days × ($0.02/30) = $1.19
```

---

## Google Cloud Storage Free Tier

### What's Actually Free:
```
Storage: First 5 GB/month FREE
Operations: 5,000 Class A operations/month FREE
Egress: 1 GB/month FREE (data transfer out)
```

### Example with Free Tier:

#### Scenario 1: Store 3 GB for 1 month
```
Size: 3 GB (under 5 GB free tier)
Cost: $0 (FREE)
```

#### Scenario 2: Store 10 GB for 1 month
```
Size: 10 GB
Free: 5 GB
Charged: 5 GB × $0.02 = $0.10/month
```

#### Scenario 3: Store 256 GB for 1 month
```
Size: 256 GB
Free: 5 GB
Charged: 251 GB × $0.02 = $5.02/month
```

---

## Google Drive Storage

### Free Tier:
```
Storage: 15 GB FREE (shared across Gmail, Drive, Photos)
Duration: Forever (as long as account is active)
Cost: $0
```

### If you exceed 15 GB:
```
Google One Plans:
- 100 GB: $1.99/month
- 200 GB: $2.99/month
- 2 TB: $9.99/month
```

### Example: This Pipeline Uses Google Drive

When you download large files (>5MB estimated), this pipeline exports to **Google Drive**:

```
Your Drive Space: 15 GB FREE
Maharashtra Monthly (256 GB): Exceeds free tier
Options:
1. Download and delete from Drive immediately (stays FREE)
2. Keep in Drive: Need Google One 2TB plan ($9.99/month)
```

**Recommended**: Download from Drive to your local computer, then delete from Drive to stay FREE.

---

## Realistic Storage Costs for This Pipeline

### Workflow 1: Download Immediately (RECOMMENDED - FREE)
```
Step 1: Pipeline exports to Google Drive (FREE 15GB)
Step 2: You download to local computer (same day)
Step 3: Delete from Google Drive (same day)
Step 4: Process locally, keep results only

Cost: $0 (stays within free tier)
```

### Workflow 2: Store in GCS Temporarily
```
Step 1: Pipeline exports to GCS bucket
Step 2: Store for 7 days while processing
Step 3: Delete after processing

Example (Maharashtra 256 GB):
Cost: 256 GB × 7 days × ($0.02/30) = $1.19
```

### Workflow 3: Store in GCS Long-Term
```
Step 1: Pipeline exports to GCS bucket
Step 2: Keep forever for archive

Example (Maharashtra 256 GB):
Month 1: $5.12
Month 2: $5.12
Month 12: $5.12
Year 1 Total: $61.44
Year 10 Total: $614.40
```

---

## How to Minimize Storage Costs

### Strategy 1: Use Google Drive Free Tier
```
1. Export to Google Drive (FREE up to 15GB)
2. Download immediately to local computer
3. Delete from Drive same day
4. Process locally

Cost: $0
Limitation: Files must be <15GB or download in batches
```

### Strategy 2: Use GCS with Auto-Delete
```
1. Export to GCS bucket
2. Set lifecycle policy: Delete after 7 days
3. Download within 7 days
4. Automatic cleanup

Cost: ~$0.17 - $1.19 per download (7 days storage)
Benefit: Automatic cleanup, no manual deletion needed
```

### Strategy 3: Process in GEE, Export Results Only
```
1. Process in Google Earth Engine (FREE)
2. Export only statistics/results (small files)
3. Never download raw satellite images

Cost: $0 (FREE tier)
Limitation: Requires programming (Python/JavaScript)
```

---

## GCS Lifecycle Policy Example

### Auto-Delete After 7 Days:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 7}
      }
    ]
  }
}
```

### How to Set Up:
```bash
# Create lifecycle policy file
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 7}
      }
    ]
  }
}
EOF

# Apply to bucket
gsutil lifecycle set lifecycle.json gs://your-bucket-name
```

### Result:
- Files automatically deleted after 7 days
- No manual cleanup needed
- Pay only for 7 days of storage
- Maharashtra 256 GB: $1.19 per download

---

## Billing Timeline Examples

### Example 1: Quick Download (1 day)
```
Feb 5: Upload 256 GB to GCS
Feb 5: Download to local computer (same day)
Feb 5: Delete from GCS
Feb 28: Billing cycle ends
Mar 1: Charged for 1 day = $0.17
```

### Example 2: Weekly Processing (7 days)
```
Feb 5: Upload 256 GB to GCS
Feb 12: Finish processing, delete from GCS
Feb 28: Billing cycle ends
Mar 1: Charged for 7 days = $1.19
```

### Example 3: Monthly Storage (30 days)
```
Feb 5: Upload 256 GB to GCS
Mar 5: Delete from GCS (30 days later)
Mar 31: Billing cycle ends
Apr 1: Charged for 30 days = $5.12
```

### Example 4: Forgot to Delete (365 days)
```
Feb 5, 2026: Upload 256 GB to GCS
Feb 5, 2027: Finally delete (1 year later)
Monthly bills: $5.12 × 12 = $61.44
Total: $61.44 (ouch!)
```

---

## Cost Comparison: Different Storage Durations

| Data Size | 1 Day | 7 Days | 30 Days | 365 Days |
|-----------|-------|--------|---------|----------|
| **10 GB** | $0.01 | $0.05 | $0.20 | $2.40 |
| **100 GB** | $0.07 | $0.47 | $2.00 | $24.00 |
| **256 GB** (Maharashtra) | $0.17 | $1.19 | $5.12 | $61.44 |
| **1 TB** | $0.67 | $4.69 | $20.00 | $240.00 |
| **2.56 TB** (India) | $1.71 | $11.99 | $51.20 | $614.40 |

---

## Answer to Your Question

**"How long does cloud store my data before next charges?"**

**Answer**: There is **NO free storage period**. Charges start **immediately** when you upload data and continue **every day** until you delete it.

**Billing**:
- Charged **per day** based on data size
- Billed **monthly** at end of billing cycle
- First **5 GB is FREE** on GCS
- First **15 GB is FREE** on Google Drive

**To minimize costs**:
1. Download immediately (same day) = ~$0.17 for 256 GB
2. Delete within 7 days = ~$1.19 for 256 GB
3. Use Google Drive free tier (15 GB) and download immediately = $0
4. Set auto-delete lifecycle policy = automatic cleanup

**Recommended for this pipeline**:
- Small files (<15 GB): Use Google Drive, download immediately, delete = **FREE**
- Large files (>15 GB): Use GCS, download within 7 days, delete = **$0.17 - $11.99**
- Never forget to delete: Set 7-day auto-delete policy = **automatic + cheap**

**The longer you store, the more you pay. Delete as soon as you've downloaded and processed the data.**
