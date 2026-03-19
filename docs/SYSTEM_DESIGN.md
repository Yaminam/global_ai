# System Architecture Diagram

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (Frontend)                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                        Web Browser                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │  Upload UI  │  │  Validation  │  │  Results &   │           │  │
│  │  │             │  │   Display    │  │   Analytics  │           │  │
│  │  └─────────────┘  └──────────────┘  └──────────────┘           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↕ (HTTP/REST)                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER (Nginx/Reverse Proxy)              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  • Request Routing                                              │  │
│  │  • Load Balancing                                               │  │
│  │  • SSL/TLS Termination                                          │  │
│  │  • Rate Limiting                                                │  │
│  │  • Compression (gzip)                                           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↕                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (Flask Backend)                    │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Upload     │  │  Validation  │  │  Processing  │  │  Results   │ │
│  │   Routes     │→ │   Routes     │→ │   Routes     │→ │   Routes   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Business Logic Layer (Services)                     │  │
│  │                                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │ File Service │  │Validation    │  │ Processor    │           │  │
│  │  │              │  │ Service      │  │ Service      │           │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                 DATA PROCESSING LAYER (Analytics Engine)                │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Statistical │  │   Anomaly    │  │    Trend     │  │   Report   │ │
│  │  Analysis    │  │  Detection   │  │  Analysis    │  │  Generator │ │
│  │ (NumPy/Stats)│  │ (Scikit-Learn)│ │ (Forecast)   │  │ (Jinja2)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                              ↓                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     DATA LAYER & STORAGE                                │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  JSON File   │  │  SQLite DB   │  │  Redis Cache │  │   Cloud    │ │
│  │  Storage     │  │  (Metadata)  │  │  (Optional)  │  │  Storage   │ │
│  │  /files      │  │   /data.db   │  │              │  │   (S3)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Directories:                                                     │  │
│  │ ├── /storage/datasets/    → Raw uploaded files                 │  │
│  │ ├── /storage/processed/   → Transformed data                   │  │
│  │ ├── /storage/results/     → Final results                      │  │
│  │ └── /storage/cache/       → Temporary cache files              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Through Layers

```
1. USER UPLOADS FILE
   └─→ Frontend (HTML/JS)
       └─→ POST /api/upload
           └─→ Nginx (Route)
               └─→ Flask app.py
                   └─→ upload_routes.py
                       └─→ file_service.py
                           └─→ Storage: /datasets/file.csv

2. VALIDATION PHASE
   └─→ GET /api/validate/{dataset_id}
       └─→ Nginx
           └─→ Flask
               └─→ validation_routes.py
                   └─→ validation_service.py
                       └─→ Load from storage
                           └─→ Apply validation rules
                               └─→ Store: /validated/report.json

3. PROCESSING PHASE
   └─→ POST /api/process
       └─→ Flask
           └─→ processing_routes.py
               └─→ processor_service.py
                   └─→ Queue job
                       └─→ Worker processes:
                           ├─→ Load data (streaming)
                           ├─→ Apply transformations
                           ├─→ Aggregate data
                           └─→ Store: /results/output.json

4. ANALYTICS PHASE
   └─→ GET /api/analytics/{job_id}
       └─→ Flask
           └─→ analytics_routes.py
               └─→ Analytics processors:
                   ├─→ statistical.py → Calculate stats
                   ├─→ anomaly_detection.py → Find outliers
                   └─→ trend_analysis.py → Forecast trends
                       └─→ Store: /analytics/report.json

5. RESULTS DISPLAY
   └─→ GET /api/results/{job_id}
       └─→ Flask retrieves from storage
           └─→ Frontend renders in dashboard
                └─→ User visualizes data
```

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Components                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ main.js         ← Orchestrates everything               │  │
│  │   ├→ uploader.js   ← Handles file uploads              │  │
│  │   ├→ api.js        ← API communication                 │  │
│  │   ├→ validator.js  ← Client-side validation            │  │
│  │   ├→ dashboard.js  ← UI management                     │  │
│  │   └→ charts.js     ← Data visualization                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP REST API
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Components                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ app.py          ← Flask application                     │  │
│  │   ├→ routes/                                            │  │
│  │   │   ├→ upload.py                                      │  │
│  │   │   ├→ validation.py                                  │  │
│  │   │   ├→ processing.py                                  │  │
│  │   │   ├→ results.py                                     │  │
│  │   │   └→ analytics.py                                   │  │
│  │   │                                                      │  │
│  │   ├→ services/                                          │  │
│  │   │   ├→ file_service.py                                │  │
│  │   │   ├→ validation_service.py                          │  │
│  │   │   ├→ processor_service.py                           │  │
│  │   │   └→ cache_service.py                               │  │
│  │   │                                                      │  │
│  │   ├→ models/                                            │  │
│  │   │   ├→ dataset.py                                     │  │
│  │   │   ├→ job.py                                         │  │
│  │   │   └→ result.py                                      │  │
│  │   │                                                      │  │
│  │   └→ utils/                                             │  │
│  │       ├→ logger.py                                      │  │
│  │       ├→ decorators.py                                  │  │
│  │       └→ validators.py                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Data Flow
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Analytics & Processing                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ analytics/                                               │  │
│  │   ├→ processors/              ← Heavy computation        │  │
│  │   │   ├→ statistical.py        ← NumPy/Pandas            │  │
│  │   │   ├→ anomaly_detection.py  ← Scikit-learn            │  │
│  │   │   └→ aggregation.py        ← Data transformation     │  │
│  │   │                                                      │  │
│  │   └→ reports/                 ← Generate output          │  │
│  │       ├→ generator.py          ← Create reports          │  │
│  │       └→ export.py             ← Multiple formats        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Read/Write
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Storage Layer                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Datasets      (raw files)                               │  │
│  │ Validations   (validation results)                       │  │
│  │ Processed     (transformed data)                         │  │
│  │ Results       (output data)                              │  │
│  │ Analytics     (report data)                              │  │
│  │ Cache         (temporary data)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Processing Pipeline

```
INPUT
  ↓
┌─────────────────────────┐
│  FILE PARSING           │
│  ├─ Read headers        │
│  ├─ Detect data types   │
│  └─ Extract metadata    │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  DATA VALIDATION        │
│  ├─ Type checking       │
│  ├─ Null detection      │
│  ├─ Duplicate removal   │
│  └─ Schema validation   │
└────────┬────────────────┘
         │ ✓ PASS → Continue
         │ ✗ FAIL → Report & Stop
         ↓
┌─────────────────────────┐
│  TRANSFORMATION         │
│  ├─ Filtering           │
│  ├─ Normalization       │
│  ├─ Aggregation         │
│  └─ Sorting             │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  ANALYTICS              │
│  ├─ Statistical calc    │
│  ├─ Anomaly detection   │
│  ├─ Trend analysis      │
│  └─ Report generation   │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  STORAGE & EXPORT       │
│  ├─ JSON format         │
│  ├─ CSV format          │
│  ├─ Excel export        │
│  └─ PDF report          │
└────────┬────────────────┘
         ↓
OUTPUT
```

---

## Scalability Architecture

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │   (HAProxy)     │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ↓                ↓                ↓
        ┌───────┐        ┌───────┐        ┌───────┐
        │ App 1 │        │ App 2 │        │ App 3 │
        │Flask  │        │Flask  │        │Flask  │
        │ w: 4  │        │ w: 4  │        │ w: 4  │
        └───┬───┘        └───┬───┘        └───┬───┘
            │                │                │
            └────────────────┼────────────────┘
                             │
            ┌────────────────┼────────────────┐
            ↓                ↓                ↓
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │  Redis    │   │  S3       │   │ PostgreSQL│
        │  Cache    │   │  Storage  │   │  Database │
        └───────────┘   └───────────┘   └───────────┘
```

---

## Security Layers

```
┌─────────────────────────────────────────────────┐
│         Browser / User Device                   │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│         HTTPS/TLS Layer                         │
│  • Encryption in transit                        │
│  • Certificate authentication                   │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│       WAF & DDoS Protection                      │
│  • Cloudflare / AWS Shield                      │
│  • Rate limiting                                │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│       Nginx Reverse Proxy                       │
│  • SSL termination                              │
│  • Request filtering                            │
│  • CORS validation                              │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│       API Authentication Layer                  │
│  • API key validation                           │
│  • JWT token verification                       │
│  • Session management                          │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│       Application-Level Security                │
│  • Input validation                             │
│  • SQL injection prevention                     │
│  • XSS prevention                               │
│  • CSRF protection                              │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│       Data Encryption Layer                     │
│  • Database encryption                          │
│  • File encryption at rest                      │
│  • Backup encryption                            │
└─────────────────────────────────────────────────┘
```

---

**Last Updated:** March 18, 2026
