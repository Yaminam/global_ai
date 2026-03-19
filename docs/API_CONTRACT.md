# API Contract - Advanced Smart Data Processing Platform

## Base URL
```
http://localhost:5000/api
```

---

## Endpoints

### 1. Upload Endpoint
**Upload data files for processing**

```http
POST /api/upload
```

**Request:**
```
Content-Type: multipart/form-data

{
  "file": <binary_file>,
  "dataset_name": "string (required)",
  "description": "string (optional)",
  "category": "string (optional)" // e.g., "sales", "users", "metrics"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "dataset_id": "uuid-string",
    "filename": "data.csv",
    "file_size": 1048576,
    "dataset_name": "Sales Data Q1",
    "status": "uploaded",
    "upload_timestamp": "2026-03-18T10:30:00Z",
    "row_count": 5000,
    "columns": ["id", "date", "amount", "category"],
    "mime_type": "text/csv"
  },
  "message": "File uploaded successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid file format",
  "details": "Supported formats: CSV, JSON, XLSX"
}
```

---

### 2. Validate Endpoint
**Validate uploaded dataset against rules**

```http
POST /api/validate
```

**Request:**
```json
{
  "dataset_id": "uuid-string",
  "validation_rules": {
    "missing_values_threshold": 10,
    "duplicate_rows_check": true,
    "data_type_validation": true,
    "schema_validation": {
      "id": "integer",
      "date": "date",
      "amount": "number"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "dataset_id": "uuid-string",
    "validation_id": "uuid-string",
    "status": "passed",
    "total_rows": 5000,
    "valid_rows": 4950,
    "invalid_rows": 50,
    "issues": [
      {
        "type": "missing_value",
        "column": "date",
        "row_indices": [45, 120, 234],
        "count": 3,
        "severity": "warning"
      },
      {
        "type": "invalid_date_format",
        "column": "date",
        "row_indices": [567, 890],
        "expected_format": "YYYY-MM-DD",
        "severity": "error"
      }
    ],
    "validation_timestamp": "2026-03-18T10:35:00Z",
    "duration_ms": 1500
  },
  "message": "Validation completed with 2 issues found"
}
```

---

### 3. Process Endpoint
**Start data processing job**

```http
POST /api/process
```

**Request:**
```json
{
  "dataset_id": "uuid-string",
  "processing_config": {
    "transformations": [
      {
        "type": "normalize",
        "columns": ["amount"],
        "method": "min-max"
      },
      {
        "type": "aggregate",
        "group_by": ["category"],
        "aggregations": {
          "amount": "sum",
          "id": "count"
        }
      }
    ],
    "filters": {
      "amount": { "$gte": 100, "$lte": 10000 },
      "date": { "$gte": "2026-01-01" }
    },
    "output_format": "json"
  }
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "dataset_id": "uuid-string",
    "status": "queued",
    "created_at": "2026-03-18T10:40:00Z",
    "estimated_duration_seconds": 30,
    "priority": "normal"
  },
  "message": "Processing job created. Poll /api/status/{job_id} for updates"
}
```

---

### 4. Results Endpoint
**Retrieve processing results**

```http
GET /api/results/{job_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "dataset_id": "uuid-string",
    "status": "completed",
    "processed_rows": 4850,
    "output_rows": 1234,
    "result_file_path": "/storage/results/result-uuid.json",
    "result_preview": [
      { "category": "Electronics", "total_amount": 125000, "order_count": 450 },
      { "category": "Clothing", "total_amount": 89000, "order_count": 320 },
      { "category": "Food", "total_amount": 45000, "order_count": 890 }
    ],
    "column_statistics": {
      "amount": {
        "min": 100,
        "max": 9999,
        "mean": 2500.5,
        "median": 2000,
        "std_dev": 1800.25
      }
    },
    "processing_time_ms": 2400,
    "completed_at": "2026-03-18T10:42:30Z"
  },
  "message": "Results ready for download"
}
```

**Response (202 Accepted - Still Processing):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "status": "processing",
    "progress_percentage": 65,
    "estimated_remaining_seconds": 15
  },
  "message": "Job still processing..."
}
```

---

### 5. Analytics Endpoint
**Get advanced analytics and insights**

```http
GET /api/analytics/{job_id}
```

**Query Parameters:**
```
?analysis_type=statistical,anomaly,trend
&confidence_level=0.95
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "analytics_id": "uuid-string",
    "generated_at": "2026-03-18T10:45:00Z",
    "statistical_analysis": {
      "summary": {
        "total_records": 4850,
        "unique_values": 1234,
        "null_percentage": 0.5
      },
      "distributions": {
        "amount": {
          "type": "normal",
          "skewness": 0.25,
          "kurtosis": -0.5
        }
      }
    },
    "anomaly_detection": {
      "anomalies_found": 15,
      "anomaly_percentage": 0.31,
      "anomalous_records": [
        {
          "row_index": 456,
          "anomaly_score": 0.92,
          "reason": "amount is 5 standard deviations from mean",
          "values": { "id": 5001, "amount": 50000 }
        }
      ]
    },
    "trend_analysis": {
      "trend_direction": "upward",
      "growth_rate": 5.2,
      "forecast_next_period": 127500,
      "confidence": 0.87
    },
    "insights": [
      "Sales trending upward at 5.2% growth",
      "15 anomalous transactions detected (0.31%)",
      "Electronics category leads with 38% of revenue"
    ]
  },
  "message": "Analytics generated successfully"
}
```

---

### 6. Status Endpoint
**Check job status without retrieving results**

```http
GET /api/status/{job_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "dataset_id": "uuid-string",
    "status": "completed",
    "progress_percentage": 100,
    "created_at": "2026-03-18T10:40:00Z",
    "started_at": "2026-03-18T10:41:00Z",
    "completed_at": "2026-03-18T10:42:30Z",
    "duration_ms": 90000,
    "input_rows": 5000,
    "processed_rows": 4850,
    "error_rows": 150,
    "output_rows": 1234
  }
}
```

---

### 7. Delete Job Endpoint
**Cancel or delete a processing job**

```http
DELETE /api/jobs/{job_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "status": "cancelled",
    "deleted_at": "2026-03-18T10:50:00Z"
  },
  "message": "Job cancelled and cleaned up"
}
```

---

## Common Response Headers

```
Content-Type: application/json
X-Request-ID: uuid-string
X-Response-Time-Ms: 125
X-API-Version: 1.0
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request",
  "details": "Missing required field: dataset_id",
  "error_code": "INVALID_REQUEST"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Unauthorized",
  "details": "Missing or invalid API key",
  "error_code": "UNAUTHORIZED"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Resource not found",
  "details": "Job ID 'invalid-id' does not exist",
  "error_code": "NOT_FOUND"
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "details": "Maximum 100 requests per minute",
  "retry_after_seconds": 45,
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "details": "An unexpected error occurred",
  "error_code": "INTERNAL_ERROR",
  "request_id": "uuid-string"
}
```

---

## Request/Response Formats

### Supported Content Types
- `application/json` - Standard JSON
- `multipart/form-data` - File uploads
- `application/x-www-form-urlencoded` - Form submissions

### Data Types
- `string` - Text
- `integer` - Whole numbers
- `number` - Decimal numbers
- `boolean` - true/false
- `date` - ISO 8601 format (YYYY-MM-DD)
- `timestamp` - ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- `uuid` - UUID v4

---

## Rate Limiting

- **Free Tier:** 100 requests/minute
- **Premium Tier:** 1000 requests/minute
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Authentication

Include API key in header:
```
Authorization: Bearer YOUR_API_KEY
```

Or as query parameter:
```
?api_key=YOUR_API_KEY
```

---

## Pagination

For list endpoints:
```
?page=1&limit=50&sort=created_at&order=desc
```

Response includes:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_records": 1250,
    "total_pages": 25
  }
}
```
