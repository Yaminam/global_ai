# Data Flow Diagram - Advanced Smart Data Processing Platform

## 1. High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION LAYER                              │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ File Upload  │  │  Validation  │  │  Processing  │  │   Results    │  │
│  │   Form       │→ │   Display    │→ │   Monitor    │→ │ Visualization│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                  ↓                 ↓                  ↓          │
└─────────────────────────────────────────────────────────────────────────────┘
         │                  │                 │                  │
         ↓                  ↓                 ↓                  ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Flask Routes)                            │
│                                                                             │
│  POST /api/upload    POST /api/validate  POST /api/process GET /api/results│
└─────────────────────────────────────────────────────────────────────────────┘
         │                  │                 │                  │
         ↓                  ↓                 ↓                  ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BACKEND SERVICE LAYER                                 │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    File      │  │  Validation  │  │ Processor    │  │  Results     │  │
│  │   Service    │  │   Service    │  │  Service     │  │  Service     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                 │                  │          │
└─────────────────────────────────────────────────────────────────────────────┘
         │                  │                 │                  │
         ↓                  ↓                 ↓                  ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATA PROCESSING LAYER                                 │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Data Parsing │  │ Data Quality │  │ Aggregation  │  │ Analytics    │  │
│  │ & Ingestion  │→ │ Checks       │→ │ & Transform  │→ │ Calculation  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                 │                  │          │
└─────────────────────────────────────────────────────────────────────────────┘
         │                  │                 │                  │
         ↓                  ↓                 ↓                  ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATA STORAGE LAYER                                    │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Raw Data    │  │  Validation  │  │   Processed  │  │   Reports &  │  │
│  │   Files      │  │   Results    │  │   Data       │  │   Analytics  │  │
│  │ /datasets/   │  │ /validated/  │  │ /processed/  │  │ /results/    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                 │                  │          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Step-by-Step Data Flow

### Step 1: File Upload / Data Ingestion
```
User Browser               Backend                 Storage
    │                        │                       │
    │ POST /api/upload       │                       │
    │─────────────────────→  │                       │
    │  (CSV/JSON file)       │                       │
    │                        │ Parse file header     │
    │                        │ Extract metadata      │
    │                        │                       │
    │                        │ Generate file_id      │
    │                        │ Generate dataset_id   │
    │                        │                       │
    │                        │──────────────────────→│
    │                        │  Store raw file       │
    │                        │  /datasets/uuid.csv   │
    │                        │←──────────────────────│
    │                        │  Confirmation         │
    │  ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │                       │
    │  response + dataset_id │                       │
    │                        │                       │
```

**Data Structure Created:**
```json
{
  "file_id": "uuid-1",
  "dataset_id": "dataset-uuid-1",
  "filename": "sales_data.csv",
  "file_size": 1048576,
  "row_count": 5000,
  "columns": ["id", "date", "amount", "category"],
  "status": "uploaded",
  "timestamp": "2026-03-18T10:30:00Z"
}
```

---

### Step 2: Data Validation
```
User Browser               Backend                       Storage
    │                        │                           │
    │ POST /api/validate     │                           │
    │ {dataset_id}          │                           │
    │─────────────────────→  │                           │
    │                        │ Retrieve dataset          │
    │                        │─────────────────────────→ │
    │                        │←─────────────────────────│
    │                        │ Raw data loaded           │
    │                        │                           │
    │                        │ Apply validation rules:   │
    │                        │ • Check data types        │
    │                        │ • Detect missing values   │
    │                        │ • Find duplicates         │
    │                        │ • Schema validation       │
    │                        │                           │
    │                        │ Generate issues list      │
    │                        │ Categorize errors         │
    │                        │                           │
    │                        │─────────────────────────→ │
    │                        │ Store validation report   │
    │                        │ /validated/uuid.json      │
    │                        │←─────────────────────────│
    │  ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │                           │
    │  Validation response   │                           │
    │  (issues + summary)    │                           │
    │                        │                           │
```

**Validation Report Structure:**
```json
{
  "dataset_id": "dataset-uuid-1",
  "validation_id": "val-uuid-1",
  "status": "passed/failed",
  "total_rows": 5000,
  "valid_rows": 4950,
  "invalid_rows": 50,
  "issues": [
    {
      "type": "missing_value",
      "column": "date",
      "row_indices": [45, 120, 234],
      "severity": "warning"
    }
  ]
}
```

---

### Step 3: Data Processing
```
User Browser               Backend                        Processing Queue
    │                        │                               │
    │ POST /api/process      │                               │
    │ {dataset_id, config}  │                               │
    │─────────────────────→  │                               │
    │                        │ Create job record             │
    │                        │ (job_id, status: queued)      │
    │                        │                               │
    │                        │────────────────────────────→ │
    │ ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │ Enqueue job                   │
    │ Response: job_id       │←────────────────────────────│
    │                        │ Confirmation                  │
    │                        │                               │
    │ Poll: GET /api/status/ │                               │
    │ {job_id}              │                               │
    │─────────────────────→  │ [Background Processing]      │
    │                        │                               │
    │  ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │ Load raw data                │
    │  {progress: 0%}        │ Apply transformations:       │
    │                        │ • Normalize columns          │
    │                        │ • Filter rows                │
    │                        │ • Aggregate data             │
    │                        │ • Sort/Group results         │
    │                        │                              │
    │                        │ Update job status (50%)      │
    │  (poll again)          │                              │
    │─────────────────────→  │                              │
    │ ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │                              │
    │  {progress: 50%}       │ Store processed data         │
    │                        │                              │
    │  (poll again)          │ Complete job (100%)          │
    │─────────────────────→  │                              │
    │  ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │                              │
    │  {status: completed}   │                              │
    │                        │                              │
```

**Job Record:**
```json
{
  "job_id": "job-uuid-1",
  "dataset_id": "dataset-uuid-1",
  "status": "processing",
  "progress_percentage": 50,
  "input_rows": 5000,
  "processed_rows": 2500,
  "output_rows": 1234,
  "created_at": "2026-03-18T10:40:00Z",
  "started_at": "2026-03-18T10:41:00Z",
  "estimated_completion_time": "2026-03-18T10:42:30Z"
}
```

---

### Step 4: Analytics Processing
```
User Browser               Backend                    Analytics Engine
    ├─────────────────────→│                               │
    │ GET /api/analytics/  │                               │
    │ {job_id}            │                               │
    │                        │ Retrieve processed data       │
    │                        │────────────────────────────→ │
    │                        │ Calculate statistics          │
    │                        │ • Mean, median, std dev       │
    │                        │ • Distribution analysis       │
    │                        │ • Correlation matrix          │
    │                        │                               │
    │                        │ Detect anomalies              │
    │                        │ • Z-score analysis            │
    │                        │ • Isolation Forest            │
    │                        │                               │
    │                        │ Trend analysis                │
    │                        │ • Time series decomposition   │
    │                        │ • Forecast next values        │
    │                        │                               │
    │                        │←──────────────────────────────│
    │                        │ Return analytics results      │
    │  ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │                              │
    │  Analytics response    │                              │
    │  (insights + charts)   │                              │
    │                        │                              │
```

**Analytics Output Structure:**
```json
{
  "job_id": "job-uuid-1",
  "analytics_id": "analytics-uuid-1",
  "generated_at": "2026-03-18T10:45:00Z",
  "statistical_analysis": {
    "summary": {...},
    "distributions": {...},
    "correlations": {...}
  },
  "anomaly_detection": {
    "anomalies_found": 15,
    "anomalous_records": [...]
  },
  "trend_analysis": {
    "trend_direction": "upward",
    "growth_rate": 5.2,
    "forecast": {...}
  },
  "insights": ["...", "..."]
}
```

---

### Step 5: Results Retrieval & Visualization
```
User Browser               Backend                      Storage
    │                        │                           │
    │ GET /api/results/      │                           │
    │ {job_id}              │                           │
    │────────────────────→   │ Retrieve result file      │
    │                        │──────────────────────────→│
    │                        │←──────────────────────────│
    │                        │ Processed data loaded      │
    │ ← ─ ─ ─ ─ ─ ─ ─ ─ ─  │ (with pagination)        │
    │ Results JSON           │                           │
    │ (preview + metadata)   │                           │
    │                        │                           │
    │ Visualize in frontend: │                           │
    │ Charts, tables, etc.   │                           │
    │                        │                           │
```

---

## 3. Data Model Relationships

```
┌──────────────────┐
│    Dataset       │
├──────────────────┤
│ dataset_id (PK)  │
│ filename         │
│ file_size        │
│ row_count        │
│ columns[]        │
│ created_at       │
└────────┬─────────┘
         │ 1:N
         │
         ├─→ ┌──────────────────────┐
         │   │   Validation        │
         │   ├──────────────────────┤
         │   │ validation_id (PK)  │
         │   │ dataset_id (FK)     │
         │   │ status              │
         │   │ issues[]            │
         │   │ created_at          │
         │   └──────────────────────┘
         │
         ├─→ ┌──────────────────────┐
         │   │   Processing Job    │
         │   ├──────────────────────┤
         │   │ job_id (PK)         │
         │   │ dataset_id (FK)     │
         │   │ status              │
         │   │ progress            │
         │   │ config              │
         │   │ created_at          │
         │   └──────────┬───────────┘
         │              │ 1:N
         │              │
         │              └─→ ┌──────────────────┐
         │                  │ Process Result   │
         │                  ├──────────────────┤
         │                  │ result_id (PK)   │
         │                  │ job_id (FK)      │
         │                  │ output_data[]    │
         │                  │ created_at       │
         │                  └──────────────────┘
         │
         └─→ ┌──────────────────────┐
             │    Analytics        │
             ├──────────────────────┤
             │ analytics_id (PK)   │
             │ job_id (FK)         │
             │ statistical_data    │
             │ anomalies[]         │
             │ trends              │
             │ insights[]          │
             │ created_at          │
             └──────────────────────┘
```

---

## 4. Concurrent Processing Flow

```
Multiple users submitting jobs simultaneously:

User 1    User 2    User 3
   │        │         │
   │        │         │
   POST upload         │
   │────→ [Queue]      │
   │        │          │
   │        POST upload│
   │        │────→ [Queue]
   │        │          │
   │        │          POST upload
   │        │          │────→ [Queue]
   │        │          │
   │        │  [Concurrent Processing]
   │        │
   [Worker 1]  [Worker 2]  [Worker 3]
   │        │         │
   └─────────────────→ [Result Store]
           │
        Storage
```

---

## 5. Error Handling & Recovery Flow

```
Processing Job
     │
     ↓
[Validation Check]
     │
     ├─→ [PASS] → Continue processing
     │
     └─→ [FAIL] → Log error
                    │
                    ↓
                [Send Error Response]
                    │
                    ├─→ Update job status: "failed"
                    │
                    ├─→ Store error details
                    │
                    └─→ Notify user via API

File Processing
     │
     ├─→ [Timeout] → Retry logic (max 3 retries)
     │                  │
     │                  ├─→ Success → Continue
     │                  └─→ Failure → Fail job
     │
     ├─→ [Memory Error] → Log & fallback to streaming
     │
     └─→ [I/O Error] → Store partial results & retry
```

---

## 6. Data Persistence Strategy

```
┌─────────────────────────────────────────────────────┐
│              FILE SYSTEM STRUCTURE                  │
│                                                     │
├─────────────────────────────────────────────────────┤
│ storage/                                            │
│ ├── /datasets/               → Raw uploaded files   │
│ │   ├── uuid-1.csv           → User data            │
│ │   └── uuid-2.json          → User data            │
│ │                                                   │
│ ├── /validated/              → Validation results   │
│ │   ├── uuid-1-validation.json                     │
│ │   └── uuid-2-validation.json                     │
│ │                                                   │
│ ├── /processed/              → Transformed data     │
│ │   ├── job-uuid-1-output.json                     │
│ │   └── job-uuid-2-output.csv                      │
│ │                                                   │
│ ├── /results/                → Final results        │
│ │   ├── job-uuid-1-results.json                    │
│ │   └── job-uuid-1-results.csv                     │
│ │                                                   │
│ ├── /analytics/              → Analytics reports    │
│ │   ├── job-uuid-1-analytics.json                  │
│ │   └── job-uuid-1-report.pdf                      │
│ │                                                   │
│ └── /cache/                  → Temporary cache      │
│     ├── cache-data-*.tmp                           │
│     └── buffer-*.tmp                               │
│                                                     │
├─────────────────────────────────────────────────────┤
│     METADATA DATABASE (SQLite/JSON)                 │
│                                                     │
│ ├── datasets.json            → Dataset metadata     │
│ ├── validations.json         → Validation records   │
│ ├── jobs.json                → Processing jobs      │
│ ├── results.json             → Result references    │
│ └── analytics.json           → Analytics metadata   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 7. Performance Optimization Flow

```
Request comes in
     │
     ├─→ [Check Cache] ─→ Cache HIT → Return cached response
     │
     └─→ Cache MISS
            │
            ├─→ [Check if in processing queue]
            │   (another user submitted same analysis)
            │
            └─→ [Execute processing]
                   │
                   ├─→ Load data in chunks (streaming)
                   │   (Don't load entire file in memory)
                   │
                   ├─→ Apply transformations incrementally
                   │
                   ├─→ Cache results for 24 hours
                   │
                   └─→ Return response & store metadata
```

This comprehensive data flow ensures:
- ✅ Data integrity and validation
- ✅ Efficient processing
- ✅ Reliable error handling
- ✅ Scalable architecture
- ✅ User-friendly async operations
