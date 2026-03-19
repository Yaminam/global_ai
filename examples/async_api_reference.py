"""
Async Processing System: Complete API Reference Guide
Quick reference for all endpoints, parameters, and responses
"""

# ============================================================================
# SECTION 1: ENDPOINT SUMMARY
# ============================================================================

ENDPOINT_SUMMARY = """
BASE URL: http://localhost:5000/api

ASYNC JOB ENDPOINTS:
  POST   /async/process          - Submit file for processing
  POST   /async/validate         - Submit file for validation
  POST   /async/analytics        - Submit file for analytics
  GET    /async/status/{job_id}  - Get job status and results
  GET    /async/jobs             - List all active jobs
  GET    /async/queue/stats      - Get queue statistics

STORAGE ENDPOINTS:
  GET    /storage/stats          - Get storage statistics
  
HEALTH CHECK:
  GET    /health                 - System health status
  GET    /info                   - API information
"""

# ============================================================================
# SECTION 2: DETAILED ENDPOINT DOCUMENTATION
# ============================================================================

ENDPOINT_DOCUMENTATION = {
    "POST /api/async/process": {
        "description": "Submit a file for asynchronous processing",
        "method": "POST",
        "path": "/api/async/process",
        "content_type": "multipart/form-data",
        
        "parameters": {
            "file": {
                "type": "file (required)",
                "description": "CSV, JSON, or Excel file to process"
            },
            "config": {
                "type": "JSON string (optional)",
                "description": "Processing configuration",
                "example": """
{
    "filters": {
        "age": {"$gte": 18, "$lte": 65},
        "status": {"$in": ["active", "pending"]}
    },
    "transformations": [
        {
            "type": "normalize",
            "columns": ["salary", "bonus"]
        },
        {
            "type": "drop_columns",
            "columns": ["internal_id", "temp_field"]
        }
    ],
    "sorting": {
        "salary": "desc",
        "hire_date": "asc"
    }
}
"""
            }
        },
        
        "response": {
            "status_code": 202,
            "content_type": "application/json",
            "body": """
{
    "data": {
        "job_id": "job-abc123def456",
        "status": "queued",
        "submitted_at": "2026-03-18T10:30:45Z",
        "queue_position": 5,
        "check_status_at": "/api/async/status/job-abc123def456"
    },
    "message": "Job queued for processing"
}
"""
        },
        
        "error_responses": {
            "400": "Bad request (invalid file or config)",
            "413": "File too large",
            "503": "Queue full or workers unavailable"
        },
        
        "examples": {
            "curl": """
curl -X POST http://localhost:5000/api/async/process \\
  -F "file=@data.csv" \\
  -d 'config={"filters": {"age": {"$gte": 18}}}'
""",
            "python": """
import requests

files = {'file': open('data.csv', 'rb')}
config = {"filters": {"age": {"$gte": 18}}}
data = {'config': json.dumps(config)}

response = requests.post(
    'http://localhost:5000/api/async/process',
    files=files,
    data=data
)
job_id = response.json()['data']['job_id']
"""
        }
    },
    
    "POST /api/async/validate": {
        "description": "Validate file format and data quality",
        "method": "POST",
        "path": "/api/async/validate",
        "content_type": "multipart/form-data",
        
        "parameters": {
            "file": {
                "type": "file (required)",
                "description": "File to validate"
            },
            "config": {
                "type": "JSON string (optional)",
                "description": "Validation rules",
                "example": """
{
    "columns": {
        "email": {"type": "email", "required": true},
        "age": {"type": "integer", "min": 0, "max": 150}
    }
}
"""
            }
        },
        
        "response": {
            "status_code": 202,
            "body": "Same structure as /async/process"
        }
    },
    
    "POST /api/async/analytics": {
        "description": "Run analytics on file",
        "method": "POST",
        "path": "/api/async/analytics",
        "content_type": "multipart/form-data",
        
        "parameters": {
            "file": {
                "type": "file (required)",
                "description": "Data file for analytics"
            }
        },
        
        "response": {
            "status_code": 202,
            "body": "Same structure as /async/process"
        }
    },
    
    "GET /api/async/status/{job_id}": {
        "description": "Get job status and results",
        "method": "GET",
        "path": "/api/async/status/{job_id}",
        
        "parameters": {
            "job_id": {
                "type": "string (required)",
                "description": "Job ID from submission response"
            }
        },
        
        "response": {
            "status_code": 200,
            "body": """
{
    "data": {
        "job_id": "job-abc123",
        "status": "completed",
        "submitted_at": "2026-03-18T10:30:45Z",
        "started_at": "2026-03-18T10:30:47Z",
        "completed_at": "2026-03-18T10:31:02Z",
        "duration_seconds": 15,
        "input_rows": 10000,
        "output_rows": 9500,
        "data_preview": [[header], [row1], [row2]],
        "statistics": {
            "column_name": {
                "type": "numeric",
                "min": 0,
                "max": 100000,
                "mean": 45000,
                "median": 40000
            }
        },
        "processing_steps": [
            {
                "step": "filter",
                "timestamp": "2026-03-18T10:30:48Z",
                "rows_before": 10000,
                "rows_after": 9500
            }
        ]
    },
    "message": "Job completed successfully"
}
"""
        },
        
        "status_values": {
            "queued": "Waiting to be processed",
            "processing": "Currently being processed",
            "completed": "Successfully completed",
            "failed": "Processing failed",
            "cancelled": "Job was cancelled"
        },
        
        "error_responses": {
            "404": "Job not found"
        }
    },
    
    "GET /api/async/jobs": {
        "description": "List all active jobs",
        "method": "GET",
        "path": "/api/async/jobs",
        
        "response": {
            "status_code": 200,
            "body": """
{
    "data": {
        "total": 3,
        "jobs": [
            {
                "job_id": "job-abc123",
                "status": "completed",
                "submitted_at": "2026-03-18T10:25:00Z",
                "file_path": "uploads/data1.csv"
            },
            {
                "job_id": "job-def456",
                "status": "processing",
                "submitted_at": "2026-03-18T10:28:00Z",
                "file_path": "uploads/data2.csv"
            },
            {
                "job_id": "job-ghi789",
                "status": "queued",
                "submitted_at": "2026-03-18T10:30:00Z",
                "file_path": "uploads/data3.csv"
            }
        ]
    },
    "message": "Retrieved active jobs"
}
"""
        }
    },
    
    "GET /api/async/queue/stats": {
        "description": "Get queue and worker statistics",
        "method": "GET",
        "path": "/api/async/queue/stats",
        
        "response": {
            "status_code": 200,
            "body": """
{
    "data": {
        "stats": {
            "queue_size": 5,
            "workers": 8,
            "running": true,
            "processed": 1250,
            "failed": 3,
            "total": 1253
        },
        "timestamp": "2026-03-18T10:30:00Z"
    },
    "message": "Queue statistics retrieved"
}
"""
        }
    },
    
    "GET /api/storage/stats": {
        "description": "Get storage usage statistics",
        "method": "GET",
        "path": "/api/storage/stats",
        
        "response": {
            "status_code": 200,
            "body": """
{
    "data": {
        "total_jobs": 1250,
        "total_results": 1200,
        "total_datasets": 85,
        "total_analytics": 450,
        "total_size_bytes": 52428800,
        "storage_path": "./storage",
        "storage_breakdown": {
            "jobs": "10.5 MB",
            "results": "32.2 MB",
            "datasets": "5.1 MB",
            "analytics": "4.7 MB",
            "metadata": "0.4 MB"
        }
    },
    "message": "Storage statistics retrieved"
}
"""
        }
    }
}

# ============================================================================
# SECTION 3: REQUEST/RESPONSE EXAMPLES
# ============================================================================

REQUEST_EXAMPLES = {
    "simple_filter": {
        "method": "POST",
        "endpoint": "/api/async/process",
        "body": """
curl -X POST http://localhost:5000/api/async/process \\
  -F "file=@data.csv" \\
  -d 'config={"filters": {"age": {"$gte": 18}}}'
"""
    },
    
    "complex_transformation": {
        "method": "POST",
        "endpoint": "/api/async/process",
        "body": """
curl -X POST http://localhost:5000/api/async/process \\
  -F "file=@employees.csv" \\
  -d 'config={
    "filters": {
      "department": "Engineering",
      "salary": {"$gte": 50000}
    },
    "transformations": [
      {"type": "normalize", "columns": ["salary", "bonus"]},
      {"type": "drop_columns", "columns": ["internal_id"]}
    ],
    "sorting": {"salary": "desc"}
  }'
"""
    },
    
    "validation_request": {
        "method": "POST",
        "endpoint": "/api/async/validate",
        "body": """
curl -X POST http://localhost:5000/api/async/validate \\
  -F "file=@data.csv" \\
  -d 'config={
    "columns": {
      "email": {"type": "email", "required": true},
      "age": {"type": "integer", "min": 0, "max": 150}
    }
  }'
"""
    }
}

# ============================================================================
# SECTION 4: FILTER OPERATORS REFERENCE
# ============================================================================

FILTER_OPERATORS = {
    "$eq": {
        "description": "Equal to",
        "example": '{"status": {"$eq": "active"}}',
        "python_equivalent": "value == 'active'"
    },
    
    "$ne": {
        "description": "Not equal to",
        "example": '{"status": {"$ne": "inactive"}}',
        "python_equivalent": "value != 'inactive'"
    },
    
    "$gt": {
        "description": "Greater than",
        "example": '{"age": {"$gt": 18}}',
        "python_equivalent": "value > 18"
    },
    
    "$gte": {
        "description": "Greater than or equal to",
        "example": '{"age": {"$gte": 18}}',
        "python_equivalent": "value >= 18"
    },
    
    "$lt": {
        "description": "Less than",
        "example": '{"age": {"$lt": 65}}',
        "python_equivalent": "value < 65"
    },
    
    "$lte": {
        "description": "Less than or equal to",
        "example": '{"age": {"$lte": 65}}',
        "python_equivalent": "value <= 65"
    },
    
    "$in": {
        "description": "In list",
        "example": '{"status": {"$in": ["active", "pending"]}}',
        "python_equivalent": "value in ['active', 'pending']"
    }
}

# ============================================================================
# SECTION 5: CONFIGURATION PARAMETERS
# ============================================================================

CONFIGURATION_REFERENCE = {
    "ASYNC_WORKERS": {
        "description": "Number of worker threads",
        "type": "integer",
        "default": 4,
        "range": "1-32",
        "recommendation": "(2 * CPU_CORES) for CPU-bound, (4 * CPU_CORES) for I/O-bound"
    },
    
    "ASYNC_QUEUE_MAX_SIZE": {
        "description": "Maximum number of jobs in queue",
        "type": "integer",
        "default": 1000,
        "range": "10-10000",
        "recommendation": "(peak_load * avg_job_duration) * 0.8"
    },
    
    "ASYNC_CHUNK_SIZE": {
        "description": "Chunk size for large dataset processing",
        "type": "integer",
        "default": 10000,
        "range": "1000-100000",
        "recommendation": "Adjust based on available memory"
    },
    
    "STORAGE_DIR": {
        "description": "Directory for persistent storage",
        "type": "string",
        "default": "./storage",
        "recommendation": "Use SSD with at least 100GB free"
    },
    
    "STORAGE_RETENTION_DAYS": {
        "description": "Number of days to keep old data",
        "type": "integer",
        "default": 30,
        "range": "1-365",
        "recommendation": "30 for development, 90 for production"
    },
    
    "STORAGE_INDEX_ENABLED": {
        "description": "Enable index optimization",
        "type": "boolean",
        "default": True,
        "recommendation": "Always enabled for fast lookups"
    }
}

# ============================================================================
# SECTION 6: ERROR CODES AND TROUBLESHOOTING
# ============================================================================

ERROR_CODES = {
    "202": {
        "status": "Accepted",
        "meaning": "Job successfully queued",
        "action": "Query status endpoint to monitor progress"
    },
    
    "200": {
        "status": "OK",
        "meaning": "Request successful",
        "action": "Process response as normal"
    },
    
    "400": {
        "status": "Bad Request",
        "meaning": "Invalid file or configuration",
        "causes": [
            "File not provided",
            "Invalid configuration JSON",
            "Unsupported file format"
        ],
        "solutions": [
            "Check file is attached",
            "Validate configuration JSON",
            "Try CSV, JSON, or Excel format"
        ]
    },
    
    "404": {
        "status": "Not Found",
        "meaning": "Job does not exist",
        "causes": [
            "Job ID is incorrect",
            "Job was deleted or expired",
            "Job expired per STORAGE_RETENTION_DAYS"
        ],
        "solutions": [
            "Verify job_id from submission response",
            "Check recent jobs: GET /api/async/jobs"
        ]
    },
    
    "413": {
        "status": "Payload Too Large",
        "meaning": "File exceeds maximum size",
        "causes": [
            "File larger than MAX_FILE_SIZE_MB",
            "Default limit is often 1GB"
        ],
        "solutions": [
            "Split large file into chunks",
            "Increase MAX_FILE_SIZE_MB in config",
            "Compress file before upload"
        ]
    },
    
    "503": {
        "status": "Service Unavailable",
        "meaning": "Queue full or workers not available",
        "causes": [
            "Too many jobs in queue",
            "Workers crashed or not running",
            "Memory or CPU exhausted"
        ],
        "solutions": [
            "Retry after delay (exponential backoff)",
            "Increase ASYNC_WORKERS",
            "Monitor system resources",
            "Restart application if needed"
        ]
    }
}

# ============================================================================
# SECTION 7: PERFORMANCE BENCHMARK REFERENCE
# ============================================================================

PERFORMANCE_BENCHMARKS = {
    "job_submission": {
        "small_file_100kb": "10-50ms",
        "medium_file_10mb": "50-200ms",
        "large_file_100mb": "200-500ms",
        "p95": "100ms typical"
    },
    
    "job_processing": {
        "simple_filter_100k_rows": "2-5 seconds",
        "complex_transform_100k_rows": "5-10 seconds",
        "analytics_100k_rows": "3-8 seconds",
        "large_file_10m_rows": "30-120 seconds"
    },
    
    "throughput": {
        "small_jobs": "100-200 jobs/minute",
        "medium_jobs": "50-100 jobs/minute",
        "large_jobs": "10-25 jobs/minute"
    },
    
    "resource_usage": {
        "idle_memory": "200-300 MB",
        "active_memory": "800MB-2GB per job",
        "idle_cpu": "< 5%",
        "active_cpu": "40-80% with 8 workers"
    },
    
    "storage": {
        "per_job_metadata": "5-20 KB",
        "per_1m_rows_results": "10-50 MB",
        "index_overhead": "< 1%"
    }
}

# ============================================================================
# SECTION 8: QUICK START COMMAND REFERENCE
# ============================================================================

QUICK_REFERENCE = """
SUBMISSION:
  curl -X POST http://localhost:5000/api/async/process \\
       -F "file=@data.csv"

CHECK STATUS:
  curl http://localhost:5000/api/async/status/{job_id}

LIST JOBS:
  curl http://localhost:5000/api/async/jobs

QUEUE STATS:
  curl http://localhost:5000/api/async/queue/stats

STORAGE STATS:
  curl http://localhost:5000/api/storage/stats

PYTHON EXAMPLE:
  import requests
  files = {'file': open('data.csv', 'rb')}
  r = requests.post('http://localhost:5000/api/async/process', files=files)
  job_id = r.json()['data']['job_id']
"""

if __name__ == "__main__":
    print("Async Processing System: API Reference")
    print("="*60)
    print(ENDPOINT_SUMMARY)
    print("\nAvailable reference sections:")
    print("- ENDPOINT_DOCUMENTATION")
    print("- REQUEST_EXAMPLES")
    print("- FILTER_OPERATORS")
    print("- CONFIGURATION_REFERENCE")
    print("- ERROR_CODES")
    print("- PERFORMANCE_BENCHMARKS")
    print("- QUICK_REFERENCE")
