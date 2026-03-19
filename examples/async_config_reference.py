"""
Configuration examples for async processing and data storage
"""

# Example 1: Minimal async configuration (development)
MINIMAL_CONFIG = """
# Async Processing
ASYNC_WORKERS=2
ASYNC_QUEUE_MAX_SIZE=500
ASYNC_CHUNK_SIZE=5000

# Data Storage
STORAGE_DIR=./storage
STORAGE_RETENTION_DAYS=7
STORAGE_INDEX_ENABLED=True
"""

# Example 2: Production async configuration
PRODUCTION_CONFIG = """
# Async Processing
ASYNC_WORKERS=8
ASYNC_QUEUE_MAX_SIZE=2000
ASYNC_CHUNK_SIZE=50000

# Data Storage
STORAGE_DIR=/data/storage
STORAGE_RETENTION_DAYS=90
STORAGE_INDEX_ENABLED=True

# File Upload
MAX_FILE_SIZE_MB=1024
ALLOWED_EXTENSIONS=csv,json,xlsx,xls,parquet

# Processing
JOB_TIMEOUT_MINUTES=120
MAX_BATCH_SIZE=100000
"""

# Example 3: High-performance async configuration
HIGH_PERFORMANCE_CONFIG = """
# Async Processing
ASYNC_WORKERS=16
ASYNC_QUEUE_MAX_SIZE=5000
ASYNC_CHUNK_SIZE=100000

# Data Storage
STORAGE_DIR=/fast_storage/processing
STORAGE_RETENTION_DAYS=180
STORAGE_INDEX_ENABLED=True

# Processing
JOB_TIMEOUT_MINUTES=300
MAX_BATCH_SIZE=500000
ENABLE_STREAMING=True
"""

# Example 4: API request for async processing with various configurations
API_REQUEST_EXAMPLES = {
    "simple_filter": {
        "file_path": "uploads/data.csv",
        "config": {
            "filters": {
                "age": {"$gte": 18}
            }
        },
        "async": True
    },
    "complex_pipeline": {
        "file_path": "uploads/employees.csv",
        "config": {
            "filters": {
                "department": "Engineering",
                "salary": {"$gte": 50000, "$lte": 150000}
            },
            "transformations": [
                {
                    "type": "normalize",
                    "columns": ["salary", "bonus"]
                },
                {
                    "type": "drop_columns",
                    "columns": ["internal_id", "temp_notes"]
                }
            ],
            "sorting": {
                "salary": "desc",
                "hire_date": "asc"
            }
        },
        "async": True
    },
    "large_dataset": {
        "file_path": "uploads/transactions_large.csv",
        "config": {
            "filters": {
                "amount": {"$gt": 100},
                "status": {"$in": ["completed", "processing"]}
            }
        },
        "async": True,
        "dataset_id": "dataset-transactions-2026"
    }
}

# Example 5: Storage structure and data organization
STORAGE_STRUCTURE = {
    "storage/": {
        "jobs/": {
            "job-12345.json": "Complete job metadata and execution details",
            "job-67890.json": "Another job's metadata"
        },
        "results/": {
            "job-12345_processing.json": "Processing results with data preview",
            "job-12345_validation.json": "Validation results if run separately",
            "job-67890_analytics.json": "Analytics results"
        },
        "datasets/": {
            "dataset-sales-2026.json": "Dataset metadata and lineage",
            "dataset-customers.json": "Customer dataset metadata"
        },
        "analytics/": {
            "job-67890_analytics.json": "Detailed analytics output",
            "job-54321_analytics.json": "Another analytics result"
        },
        "metadata/": {
            "jobs_index.json": "Index of all jobs for quick lookup",
            "datasets_index.json": "Index of all datasets",
            "results_index.json": "Index of all results"
        }
    }
}

# Example 6: Monitoring and statistics endpoints
MONITORING_ENDPOINTS = {
    "health_check": {
        "method": "GET",
        "url": "/api/health",
        "response": {
            "status": "healthy",
            "timestamp": "2026-03-18T10:30:00",
            "version": "1.0.0",
            "environment": "production"
        }
    },
    "async_stats": {
        "method": "GET",
        "url": "/api/async/stats",
        "response": {
            "active_jobs": 5,
            "queue_stats": {
                "queue_size": 12,
                "workers": 8,
                "running": True,
                "processed": 1250,
                "failed": 3,
                "total": 1253
            },
            "storage_stats": {
                "total_jobs": 1253,
                "total_results": 1200,
                "total_datasets": 85,
                "total_analytics": 450,
                "storage_path": "./storage"
            }
        }
    },
    "queue_status": {
        "method": "GET",
        "url": "/api/async/queue",
        "response": {
            "queue_size": 12,
            "stats": {
                "queue_size": 12,
                "workers": 8,
                "running": True,
                "processed": 1250,
                "failed": 3,
                "total": 1253
            },
            "timestamp": "2026-03-18T10:30:00"
        }
    },
    "active_jobs": {
        "method": "GET",
        "url": "/api/async/jobs",
        "response": {
            "total": 5,
            "jobs": [
                {
                    "job_id": "job-abc123",
                    "status": "queued",
                    "submitted_at": "2026-03-18T10:25:00",
                    "file_path": "uploads/data.csv"
                },
                {
                    "job_id": "job-def456",
                    "status": "completed",
                    "submitted_at": "2026-03-18T10:20:00",
                    "completed_at": "2026-03-18T10:23:00",
                    "file_path": "uploads/large.csv"
                }
            ]
        }
    }
}

# Example 7: Response codes for async operations
HTTP_STATUS_CODES = {
    "202_accepted": {
        "description": "Job successfully queued for async processing",
        "example": {
            "data": {
                "job_id": "job-123456",
                "status": "queued",
                "queue_size": 5,
                "check_status_at": "/api/async/status/job-123456"
            },
            "message": "Job queued for processing"
        }
    },
    "200_ok": {
        "description": "Request successful (for sync operations or status checks)",
        "example": {
            "data": {
                "job_id": "job-123456",
                "status": "completed",
                "submitted_at": "2026-03-18T10:20:00",
                "completed_at": "2026-03-18T10:25:00"
            },
            "message": "Job status retrieved"
        }
    },
    "404_not_found": {
        "description": "Job not found",
        "example": {
            "error": "Job not found",
            "details": "Job job-nonexistent not found",
            "error_code": "JOB_NOT_FOUND",
            "status_code": 404
        }
    },
    "503_service_unavailable": {
        "description": "Queue is full or workers unavailable",
        "example": {
            "error": "Failed to queue job",
            "details": "Processing queue is full or unavailable",
            "error_code": "QUEUE_FULL",
            "status_code": 503
        }
    }
}

if __name__ == "__main__":
    print("Async Processing Configuration Examples")
    print("="*50)
    print("\n1. Minimal Configuration (Development):")
    print(MINIMAL_CONFIG)
    print("\n2. Production Configuration:")
    print(PRODUCTION_CONFIG)
    print("\n3. High-Performance Configuration:")
    print(HIGH_PERFORMANCE_CONFIG)
