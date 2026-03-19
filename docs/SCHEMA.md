# JSON Storage Schema - Advanced Smart Data Processing Platform

## Overview
This document defines the JSON-based storage schemas for all data entities in the platform.

---

## 1. Dataset Schema

**File:** `/storage/datasets/metadata.json`

```json
{
  "datasets": [
    {
      "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-12345",
      "filename": "sales_data_q1_2026.csv",
      "file_path": "/storage/datasets/550e8400-e29b-41d4.csv",
      "file_size_bytes": 2048576,
      "file_type": "text/csv",
      "mime_type": "text/csv",
      "encoding": "utf-8",
      "dataset_name": "Sales Data Q1 2026",
      "description": "Quarterly sales data for Q1 2026",
      "category": "sales",
      "tags": ["quarterly", "sales", "2026", "q1"],
      "row_count": 5000,
      "column_count": 12,
      "columns": [
        {
          "index": 0,
          "name": "transaction_id",
          "data_type": "string",
          "nullable": false,
          "sample_values": ["TXN001", "TXN002"],
          "unique_count": 5000
        },
        {
          "index": 1,
          "name": "date",
          "data_type": "date",
          "format": "YYYY-MM-DD",
          "nullable": false,
          "sample_values": ["2026-01-01", "2026-03-31"]
        },
        {
          "index": 2,
          "name": "amount",
          "data_type": "number",
          "precision": 2,
          "nullable": false,
          "sample_values": [100.50, 2500.00],
          "statistics": {
            "min": 10.0,
            "max": 50000.0,
            "mean": 2500.5
          }
        },
        {
          "index": 3,
          "name": "category",
          "data_type": "string",
          "nullable": false,
          "enum": ["Electronics", "Clothing", "Food", "Books"],
          "unique_count": 4
        },
        {
          "index": 4,
          "name": "region",
          "data_type": "string",
          "nullable": true,
          "unique_count": 8
        }
      ],
      "has_header": true,
      "delimiter": ",",
      "quote_character": "\"",
      "created_at": "2026-03-18T08:30:00Z",
      "uploaded_at": "2026-03-18T08:30:00Z",
      "last_accessed": "2026-03-18T10:30:00Z",
      "status": "active",
      "is_public": false,
      "retention_days": 90,
      "checksum": "sha256:a1b2c3d4e5f6...",
      "metadata": {
        "source": "CRM System",
        "version": "1.0",
        "data_quality_score": 95
      }
    }
  ]
}
```

---

## 2. Validation Schema

**File:** `/storage/validated/validation-report.json`

```json
{
  "validations": [
    {
      "validation_id": "val-660e8400-e29b-41d4-a716-446655440001",
      "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-12345",
      "status": "passed",
      "overall_quality_score": 94.2,
      "total_rows": 5000,
      "valid_rows": 4970,
      "invalid_rows": 30,
      "skipped_rows": 0,
      "validation_rules": {
        "check_data_types": true,
        "check_missing_values": true,
        "check_duplicates": true,
        "check_outliers": false,
        "schema_validation": true,
        "custom_rules": []
      },
      "validation_results": {
        "data_type_validation": {
          "status": "passed",
          "errors": 0,
          "warnings": 0
        },
        "missing_values": {
          "status": "passed",
          "missing_percentage": 0.5,
          "columns_with_missing": [
            {
              "column": "region",
              "missing_count": 25,
              "missing_percentage": 0.5
            }
          ]
        },
        "duplicate_rows": {
          "status": "passed",
          "duplicate_count": 0,
          "duplicate_percentage": 0.0
        },
        "schema_validation": {
          "status": "passed",
          "expected_columns": 12,
          "actual_columns": 12,
          "column_mismatches": 0,
          "type_mismatches": 0
        }
      },
      "issues": [
        {
          "issue_id": "iss-001",
          "type": "missing_value",
          "severity": "warning",
          "column": "region",
          "rows_affected": 25,
          "row_indices": [45, 120, 234, 567],
          "message": "Column 'region' has 25 missing values (0.5%)",
          "suggestion": "Either fill missing values or exclude column from analysis"
        },
        {
          "issue_id": "iss-002",
          "type": "invalid_date_format",
          "severity": "error",
          "column": "date",
          "rows_affected": 5,
          "row_indices": [890, 1234, 2045, 3100, 4567],
          "invalid_values": ["2026/01/01", "01-03-2026"],
          "expected_format": "YYYY-MM-DD",
          "message": "5 rows have invalid date format",
          "suggestion": "Correct date format to YYYY-MM-DD"
        }
      ],
      "summary": {
        "passed": true,
        "error_count": 5,
        "warning_count": 25,
        "critical_issues": 0,
        "recommendation": "Data is suitable for processing with minor cleanup recommended"
      },
      "validation_duration_ms": 2500,
      "created_at": "2026-03-18T09:00:00Z",
      "completed_at": "2026-03-18T09:00:02.5Z"
    }
  ]
}
```

---

## 3. Processing Job Schema

**File:** `/storage/jobs/job-registry.json`

```json
{
  "jobs": [
    {
      "job_id": "job-770e8400-e29b-41d4-a716-446655440002",
      "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-12345",
      "job_name": "Q1 Sales Summary",
      "description": "Aggregate sales by category and region",
      "status": "completed",
      "status_history": [
        {
          "status": "queued",
          "timestamp": "2026-03-18T10:40:00Z",
          "message": "Job queued for processing"
        },
        {
          "status": "processing",
          "timestamp": "2026-03-18T10:41:00Z",
          "message": "Processing started"
        },
        {
          "status": "completed",
          "timestamp": "2026-03-18T10:42:30Z",
          "message": "Processing completed successfully"
        }
      ],
      "progress": {
        "percentage": 100,
        "current_step": "completed",
        "total_steps": 5,
        "current_row": 5000,
        "total_rows": 5000
      },
      "processing_config": {
        "transformations": [
          {
            "type": "filter",
            "conditions": {
              "amount": { "$gte": 100, "$lte": 50000 },
              "date": { "$gte": "2026-01-01", "$lte": "2026-03-31" }
            }
          },
          {
            "type": "normalize",
            "columns": ["amount"],
            "method": "min-max"
          },
          {
            "type": "aggregate",
            "group_by": ["category", "region"],
            "aggregations": {
              "amount": "sum",
              "transaction_id": "count"
            },
            "having": {
              "count": { "$gte": 10 }
            }
          },
          {
            "type": "sort",
            "columns": [
              { "column": "amount", "order": "desc" }
            ]
          }
        ],
        "output_format": "json",
        "include_metadata": true,
        "cache_result": true,
        "sample_output": false
      },
      "input_statistics": {
        "total_rows": 5000,
        "total_columns": 12,
        "file_size_mb": 2.05,
        "data_types": {
          "string": 4,
          "number": 5,
          "date": 2,
          "boolean": 1
        }
      },
      "output_statistics": {
        "output_rows": 1234,
        "output_columns": 4,
        "output_file_size_mb": 0.45,
        "compression_ratio": 4.56
      },
      "performance_metrics": {
        "total_duration_ms": 90000,
        "parsing_duration_ms": 5000,
        "filtering_duration_ms": 15000,
        "transformation_duration_ms": 45000,
        "aggregation_duration_ms": 20000,
        "rows_per_second": 55.56,
        "memory_peak_mb": 512
      },
      "result_file": {
        "file_id": "res-880e8400-e29b-41d4-a716-446655440003",
        "file_name": "job-770e8400-result.json",
        "file_path": "/storage/results/job-770e8400-result.json",
        "file_size_bytes": 450000,
        "format": "json",
        "checksum": "sha256:b2c3d4e5f6g7..."
      },
      "error_handling": {
        "error_count": 0,
        "warning_count": 2,
        "errors": [],
        "warnings": [
          {
            "type": "precision_loss",
            "message": "Some decimal values rounded to 2 places"
          }
        ]
      },
      "resource_allocation": {
        "processor_id": "worker-1",
        "assigned_threads": 4,
        "estimated_memory_mb": 512
      },
      "created_at": "2026-03-18T10:40:00Z",
      "started_at": "2026-03-18T10:41:00Z",
      "completed_at": "2026-03-18T10:42:30Z",
      "estimated_completion_time": "2026-03-18T10:42:30Z",
      "priority": "normal",
      "timeout_seconds": 3600,
      "retry_count": 0,
      "max_retries": 3,
      "tags": ["aggregation", "sales", "monthly"],
      "is_public": false,
      "cost_estimate": {
        "compute_credits": 2.5,
        "storage_gb": 0.45
      }
    }
  ]
}
```

---

## 4. Processing Result Schema

**File:** `/storage/results/result-data.json`

```json
{
  "results": [
    {
      "result_id": "res-880e8400-e29b-41d4-a716-446655440003",
      "job_id": "job-770e8400-e29b-41d4-a716-446655440002",
      "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-12345",
      "result_type": "aggregated_data",
      "status": "available",
      "sample_preview": [
        {
          "category": "Electronics",
          "region": "North America",
          "total_amount": 125000.50,
          "transaction_count": 450,
          "avg_transaction": 277.78
        },
        {
          "category": "Clothing",
          "region": "Europe",
          "total_amount": 89000.25,
          "transaction_count": 320,
          "avg_transaction": 278.13
        },
        {
          "category": "Food",
          "region": "Asia",
          "total_amount": 45000.00,
          "transaction_count": 890,
          "avg_transaction": 50.56
        }
      ],
      "data_summary": {
        "total_result_rows": 1234,
        "columns": [
          {
            "name": "category",
            "type": "string",
            "unique_values": 4
          },
          {
            "name": "region",
            "type": "string",
            "unique_values": 8
          },
          {
            "name": "total_amount",
            "type": "number",
            "min": 1000.0,
            "max": 250000.0,
            "sum": 5000000.0,
            "mean": 4054.26
          },
          {
            "name": "transaction_count",
            "type": "integer",
            "min": 10,
            "max": 2000,
            "sum": 123456
          }
        ]
      },
      "column_statistics": {
        "total_amount": {
          "min": 1000.0,
          "max": 250000.0,
          "mean": 4054.26,
          "median": 2500.0,
          "std_dev": 18000.50,
          "variance": 324018000,
          "skewness": 2.34
        },
        "transaction_count": {
          "min": 10,
          "max": 2000,
          "mean": 100.12,
          "median": 85.0
        }
      },
      "export_formats": {
        "json": {
          "file_path": "/storage/results/job-uuid-result.json",
          "file_size_bytes": 450000
        },
        "csv": {
          "file_path": "/storage/results/job-uuid-result.csv",
          "file_size_bytes": 380000
        },
        "excel": {
          "file_path": "/storage/results/job-uuid-result.xlsx",
          "file_size_bytes": 520000
        }
      },
      "data_quality": {
        "completeness": 99.5,
        "accuracy": 98.2,
        "consistency": 99.8,
        "validity": 100.0,
        "overall_score": 99.4
      },
      "metadata": {
        "creation_timestamp": "2026-03-18T10:42:30Z",
        "data_version": "1.0",
        "source_dataset_version": "1.0",
        "processing_date": "2026-03-18",
        "generated_by": "worker-1",
        "data_freshness_hours": 0
      },
      "access_control": {
        "owner_id": "user-12345",
        "is_public": false,
        "shared_with": ["user-67890", "team-analytics"],
        "access_level": "owner"
      },
      "retention": {
        "retention_days": 30,
        "auto_delete": true,
        "delete_scheduled_at": "2026-04-17T10:42:30Z"
      }
    }
  ]
}
```

---

## 5. Analytics Schema

**File:** `/storage/analytics/analytics-report.json`

```json
{
  "analytics": [
    {
      "analytics_id": "ana-990e8400-e29b-41d4-a716-446655440004",
      "job_id": "job-770e8400-e29b-41d4-a716-446655440002",
      "result_id": "res-880e8400-e29b-41d4-a716-446655440003",
      "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-12345",
      "analysis_type": "comprehensive",
      "generated_at": "2026-03-18T10:45:00Z",
      "statistical_analysis": {
        "summary_statistics": {
          "total_records": 1234,
          "total_values": 4936,
          "null_count": 0,
          "null_percentage": 0.0,
          "unique_values": 1200,
          "cardinality": 0.97
        },
        "descriptive_stats": {
          "amount": {
            "count": 1234,
            "mean": 4054.26,
            "median": 2500.0,
            "mode": 2200.0,
            "std_dev": 18000.50,
            "variance": 324018000.25,
            "min": 1000.0,
            "max": 250000.0,
            "range": 249000.0,
            "q1": 1500.0,
            "q3": 5000.0,
            "iqr": 3500.0,
            "skewness": 2.34,
            "kurtosis": 8.92
          }
        },
        "correlations": {
          "matrix": [
            {
              "variable_1": "amount",
              "variable_2": "transaction_count",
              "pearson_r": 0.72,
              "p_value": 0.0001,
              "spearman_rho": 0.73
            }
          ]
        },
        "distributions": {
          "amount": {
            "distribution_type": "lognormal",
            "goodness_of_fit": 0.95,
            "transformed": "log(amount)",
            "histogram": {
              "bins": 10,
              "counts": [100, 150, 200, 250, 200, 150, 100, 50, 25, 9]
            }
          }
        }
      },
      "anomaly_detection": {
        "method": "isolation_forest",
        "contamination": 0.05,
        "total_records_analyzed": 1234,
        "anomalies_detected": 15,
        "anomaly_percentage": 1.22,
        "confidence_threshold": 0.9,
        "anomalous_records": [
          {
            "index": 45,
            "anomaly_score": 0.92,
            "anomaly_type": "univariate_outlier",
            "affected_columns": ["amount"],
            "reason": "Amount is 5.2 standard deviations above mean",
            "record": {
              "category": "Electronics",
              "region": "North America",
              "amount": 250000.0,
              "transaction_count": 2000
            }
          },
          {
            "index": 123,
            "anomaly_score": 0.88,
            "anomaly_type": "multivariate_outlier",
            "affected_columns": ["amount", "transaction_count"],
            "reason": "Unusual combination of high amount and low count",
            "record": {
              "category": "Books",
              "region": "South America",
              "amount": 100000.0,
              "transaction_count": 5
            }
          }
        ]
      },
      "trend_analysis": {
        "time_period": "Q1 2026",
        "trend_detection_method": "linear_regression",
        "overall_trend": "upward",
        "trend_strength": 0.82,
        "growth_rate_percent": 5.2,
        "growth_rate_monthly": 1.68,
        "trend_by_category": [
          {
            "category": "Electronics",
            "trend": "upward",
            "growth_rate": 7.5,
            "r_squared": 0.89
          },
          {
            "category": "Clothing",
            "trend": "stable",
            "growth_rate": 0.2,
            "r_squared": 0.12
          },
          {
            "category": "Food",
            "trend": "downward",
            "growth_rate": -2.1,
            "r_squared": 0.73
          }
        ],
        "seasonality": {
          "detected": true,
          "period_days": 7,
          "strength": 0.45
        },
        "forecast": {
          "next_period": {
            "forecasted_amount": 127500.0,
            "confidence_interval_lower": 105000.0,
            "confidence_interval_upper": 150000.0,
            "confidence_level": 0.95,
            "confidence_percentage": 95
          },
          "method": "exponential_smoothing",
          "rmse": 15000.25
        }
      },
      "insights": {
        "key_insights": [
          {
            "rank": 1,
            "insight": "Sales trending upward at 5.2% growth rate",
            "impact": "high",
            "actionable": true,
            "recommendation": "Increase inventory for trending categories"
          },
          {
            "rank": 2,
            "insight": "15 anomalous transactions detected (1.22%)",
            "impact": "medium",
            "actionable": true,
            "recommendation": "Investigate high-value outlier transactions"
          },
          {
            "rank": 3,
            "insight": "Electronics category driving 38% of revenue growth",
            "impact": "high",
            "actionable": true,
            "recommendation": "Focus marketing efforts on Electronics"
          },
          {
            "rank": 4,
            "insight": "Strong weekly seasonality pattern detected (period: 7 days)",
            "impact": "medium",
            "actionable": true,
            "recommendation": "Adjust staffing and inventory for weekly peaks"
          }
        ],
        "business_metrics": {
          "revenue_total": 5000000.0,
          "average_transaction": 4054.26,
          "median_transaction": 2500.0,
          "top_category": "Electronics",
          "top_region": "North America"
        }
      },
      "performance": {
        "analysis_duration_ms": 8000,
        "records_analyzed": 1234,
        "analysis_speed_records_per_second": 154.25,
        "memory_used_mb": 256
      },
      "quality_metrics": {
        "data_completeness": 100.0,
        "analysis_confidence": 95.0,
        "statistical_significance": 0.99
      },
      "export_format": "json",
      "is_public": false
    }
  ]
}
```

---

## 6. File Upload Metadata Schema

**File:** `/storage/uploads/upload-registry.json`

```json
{
  "uploads": [
    {
      "upload_id": "upl-aa0e8400-e29b-41d4-a716-446655440005",
      "file_id": "file-bb0e8400-e29b-41d4-a716-446655440006",
      "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-12345",
      "filename": "sales_data_q1_2026.csv",
      "original_filename": "Sales Data Q1 2026.csv",
      "file_size_bytes": 2048576,
      "mime_type": "text/csv",
      "status": "completed",
      "upload_progress": {
        "current_bytes": 2048576,
        "total_bytes": 2048576,
        "percentage": 100,
        "speed_mbps": 5.12,
        "estimated_time_remaining_seconds": 0
      },
      "upload_method": "file_input",
      "client_ip": "192.168.1.100",
      "browser_info": "Chrome 89.0",
      "storage_path": "/storage/datasets/550e8400-e29b-41d4.csv",
      "checksum": {
        "algorithm": "sha256",
        "value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
      },
      "integrity_verified": true,
      "virus_scan": {
        "scanned": true,
        "status": "clean",
        "scanner": "ClamAV",
        "scan_timestamp": "2026-03-18T08:30:30Z"
      },
      "created_at": "2026-03-18T08:30:00Z",
      "completed_at": "2026-03-18T08:30:25Z",
      "duration_seconds": 25,
      "retry_count": 0,
      "error_history": []
    }
  ]
}
```

---

## 7. User Session Schema

**File:** `/storage/sessions/session-registry.json`

```json
{
  "sessions": [
    {
      "session_id": "sess-cc0e8400-e29b-41d4-a716-446655440007",
      "user_id": "user-12345",
      "user_email": "user@example.com",
      "created_at": "2026-03-18T08:00:00Z",
      "last_activity": "2026-03-18T10:50:00Z",
      "expires_at": "2026-03-18T22:00:00Z",
      "session_duration_minutes": 170,
      "ip_address": "192.168.1.100",
      "browser": "Chrome",
      "os": "Windows 10",
      "device_type": "desktop",
      "actions_log": [
        {
          "action": "upload",
          "timestamp": "2026-03-18T08:30:00Z",
          "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
          "details": "Uploaded sales data"
        },
        {
          "action": "validate",
          "timestamp": "2026-03-18T09:00:00Z",
          "dataset_id": "ds-550e8400-e29b-41d4-a716-446655440000",
          "details": "Validation completed"
        },
        {
          "action": "process",
          "timestamp": "2026-03-18T10:40:00Z",
          "job_id": "job-770e8400-e29b-41d4-a716-446655440002",
          "details": "Processing job started"
        }
      ],
      "status": "active"
    }
  ]
}
```

---

## 8. Configuration Schema

**File:** `/backend/config.json`

```json
{
  "app": {
    "name": "Advanced Smart Data Processing & Analytics Platform",
    "version": "1.0.0",
    "environment": "development",
    "debug": true,
    "host": "localhost",
    "port": 5000,
    "base_url": "http://localhost:5000"
  },
  "database": {
    "type": "json",
    "path": "./storage",
    "backup_enabled": true,
    "backup_interval_hours": 24,
    "retention_days": 90
  },
  "storage": {
    "root_directory": "./storage",
    "max_file_size_mb": 1024,
    "allowed_file_types": ["csv", "json", "xlsx", "xls", "parquet"],
    "upload_chunks_enabled": true,
    "chunk_size_mb": 10,
    "temp_directory": "./storage/temp",
    "cleanup_temp_interval_hours": 6
  },
  "processing": {
    "max_workers": 4,
    "max_queue_size": 1000,
    "job_timeout_minutes": 60,
    "max_retries": 3,
    "retry_delay_seconds": 10,
    "enable_async": true,
    "enable_streaming": true,
    "default_batch_size": 10000
  },
  "security": {
    "enable_cors": true,
    "cors_origins": ["http://localhost:3000", "http://localhost:5000"],
    "rate_limit_enabled": true,
    "rate_limit_requests": 100,
    "rate_limit_window_minutes": 1,
    "api_key_required": false,
    "require_auth": false
  },
  "analytics": {
    "enable_anomaly_detection": true,
    "anomaly_method": "isolation_forest",
    "anomaly_contamination": 0.05,
    "enable_trend_analysis": true,
    "enable_forecasting": true,
    "forecast_periods": 12
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "directory": "./logs",
    "max_file_size_mb": 100,
    "backup_count": 5,
    "console_output": true
  },
  "cache": {
    "enabled": true,
    "type": "memory",
    "ttl_hours": 24,
    "max_cache_entries": 1000
  }
}
```

---

## Schema Relations Diagram

```
┌──────────────┐
│   Dataset    │ (1)
└──────┬───────┘
       │ 1:N
       │
       ├─→ ┌──────────────┐
       │   │  Validation  │
       │   └──────────────┘
       │
       ├─→ ┌──────────────┐
       │   │    Upload    │
       │   └──────────────┘
       │
       └─→ ┌──────────────┐
           │     Job      │ (1)
           └──────┬───────┘
                  │ 1:1
                  │
                  ├─→ ┌──────────────┐
                  │   │    Result    │
                  │   └──────────────┘
                  │
                  └─→ ┌──────────────┐
                      │  Analytics   │
                      └──────────────┘
```

---

## Key Design Features

1. **Immutability:** Historical records preserved with status tracking
2. **Traceability:** Complete audit trail with timestamps
3. **Scalability:** Hierarchical structure supports growth
4. **Flexibility:** JSON allows schema evolution
5. **Performance:** Indexed metadata for quick lookups
6. **Integrity:** Checksums and validation data included
7. **Retention:** Configurable data lifecycle management

All schemas follow these principles:
- IDs are UUID v4
- Timestamps are ISO 8601 format
- Numeric precision specified
- Enum values predefined
- Nullable fields explicitly marked
- Statistics calculated and stored
