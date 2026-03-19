"""
Async Processing and Data Storage: Deployment and Operational Guide
Complete reference for running, monitoring, and scaling the system
"""

# ============================================================================
# SECTION 1: QUICK START
# ============================================================================

QUICK_START_STEPS = """
1. Install Dependencies (if not already done):
   pip install flask pandas requests python-dotenv openpyxl

2. Set Environment Variables:
   export ASYNC_WORKERS=4
   export STORAGE_DIR=./storage
   export STORAGE_RETENTION_DAYS=30

3. Start the Backend Server:
   cd backend
   python app.py

4. Test Async API:
   curl -X POST http://localhost:5000/api/async/process \
        -F "file=@test_data.csv" \
        -d 'config={"filters": {"age": {"$gte": 18}}}'

5. Check Job Status:
   curl http://localhost:5000/api/async/status/{job_id}

6. Monitor Queue:
   curl http://localhost:5000/api/async/queue/stats
"""

# ============================================================================
# SECTION 2: DOCKER DEPLOYMENT
# ============================================================================

DOCKERFILE = """
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose port
EXPOSE 5000

# Set environment
ENV FLASK_APP=backend/app.py
ENV ASYNC_WORKERS=4
ENV STORAGE_DIR=/app/storage

# Run application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
"""

DOCKER_COMPOSE = """
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./storage:/app/storage
      - ./uploads:/app/uploads
    environment:
      - FLASK_ENV=production
      - ASYNC_WORKERS=8
      - STORAGE_DIR=/app/storage
      - STORAGE_RETENTION_DAYS=30
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add Nginx reverse proxy
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
"""

# ============================================================================
# SECTION 3: KUBERNETES DEPLOYMENT
# ============================================================================

KUBERNETES_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: async-processor
  labels:
    app: async-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: async-processor
  template:
    metadata:
      labels:
        app: async-processor
    spec:
      containers:
      - name: async-processor
        image: your-registry/async-processor:latest
        ports:
        - containerPort: 5000
        env:
        - name: ASYNC_WORKERS
          value: "8"
        - name: STORAGE_DIR
          value: /data/storage
        - name: STORAGE_RETENTION_DAYS
          value: "90"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: storage
          mountPath: /data/storage
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: async-storage-pvc

---

apiVersion: v1
kind: Service
metadata:
  name: async-processor-service
spec:
  selector:
    app: async-processor
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: async-storage-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
"""

# ============================================================================
# SECTION 4: PERFORMANCE TUNING
# ============================================================================

PERFORMANCE_TUNING = {
    "worker_pool_sizing": {
        "description": "Configure number of worker threads based on workload",
        "formula": "ASYNC_WORKERS = (2 * CPU_CORES) for CPU-bound, or (4 * CPU_CORES) for I/O-bound",
        "examples": {
            "4_core_system": {
                "cpu_bound": 8,
                "io_bound": 16,
                "balanced": 12
            },
            "8_core_system": {
                "cpu_bound": 16,
                "io_bound": 32,
                "balanced": 24
            },
            "16_core_system": {
                "cpu_bound": 32,
                "io_bound": 64,
                "balanced": 48
            }
        }
    },
    "chunk_size_optimization": {
        "description": "Configure processing chunk size for memory efficiency",
        "considerations": {
            "small_chunks": "More memory overhead, more context switches (use: < 5M rows)",
            "medium_chunks": "Balanced performance (use: 5M-50M rows)",
            "large_chunks": "Better performance, more memory (use: > 50M rows)"
        },
        "recommendations": {
            "available_memory_2gb": 5000,
            "available_memory_4gb": 10000,
            "available_memory_8gb": 25000,
            "available_memory_16gb": 50000,
            "available_memory_32gb": 100000
        }
    },
    "queue_size_optimization": {
        "description": "Configure maximum queue size",
        "factors": [
            "Available memory",
            "Average job size",
            "Expected peak load",
            "Acceptable queue latency"
        ],
        "formula": "MAX_QUEUE_SIZE = (AVAILABLE_MEMORY / AVG_JOB_SIZE) * 0.8",
        "examples": {
            "small_server": 500,
            "medium_server": 2000,
            "large_server": 5000,
            "high_performance": 10000
        }
    },
    "storage_optimization": {
        "ssd_requirements": "Store on SSD for 10x faster I/O",
        "compression": "Enable gzip for storage (reduces size ~70%)",
        "archival": "Move jobs older than RETENTION_DAYS to cold storage",
        "indexing": "Enable indices for fast job lookups",
        "partitioning": "Organize by date: storage/2026/03/18/jobs/"
    }
}

# ============================================================================
# SECTION 5: MONITORING AND OBSERVABILITY
# ============================================================================

MONITORING_SETUP = {
    "prometheus_metrics": """
# Prometheus metrics endpoint example
# Add to /api/metrics

async_jobs_total{status="completed"} 1250
async_jobs_total{status="failed"} 3
async_jobs_total{status="queued"} 12
async_queue_size 12
async_worker_count 8
async_processing_duration_seconds_bucket{le="1"} 150
async_processing_duration_seconds_bucket{le="10"} 1200
async_processing_duration_seconds_bucket{le="100"} 1248

storage_jobs_count 1250
storage_results_count 1200
storage_size_bytes 52428800
storage_cleanup_last_run 1710755400
""",
    
    "grafana_dashboard": """
Panels to create:
1. Queue Size Over Time (gauge + line chart)
2. Jobs Per Status (pie chart)
3. Processing Duration Distribution (histogram)
4. Worker Utilization (line chart)
5. Storage Usage (multi-series line chart)
6. Error Rate (line chart)
7. Throughput (jobs/sec - bar chart)
8. Queue Latency (p50, p95, p99)
9. Storage Cleanup Schedule (table)
10. System Health Status (stat)
""",
    
    "logging_setup": """
# Configure structured logging in backend/config.py

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(timestamp)s %(level)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/async_processing.log',
            'maxBytes': 104857600,
            'backupCount': 10,
            'formatter': 'json'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'loggers': {
        'backend.services.async_queue': {'level': 'DEBUG'},
        'backend.services.data_storage': {'level': 'INFO'},
        'backend.services.async_processor': {'level': 'DEBUG'},
    }
}
"""
}

# ============================================================================
# SECTION 6: TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = {
    "queue_is_full": {
        "symptom": "Getting 503 Service Unavailable responses",
        "causes": [
            "ASYNC_QUEUE_MAX_SIZE too small",
            "ASYNC_WORKERS too few for workload",
            "Jobs taking longer than expected",
            "Memory leak in processing"
        ],
        "solutions": [
            "Increase ASYNC_QUEUE_MAX_SIZE",
            "Increase ASYNC_WORKERS",
            "Reduce ASYNC_CHUNK_SIZE",
            "Optimize processing logic",
            "Add more servers (scale horizontally)"
        ]
    },
    "jobs_stuck_in_queue": {
        "symptom": "Jobs remain 'queued' status indefinitely",
        "causes": [
            "Workers crashed or not running",
            "Exception in processing code",
            "Deadlock in queue system",
            "File not accessible"
        ],
        "solutions": [
            "Check worker logs for exceptions",
            "Verify file permissions and paths",
            "Restart the application",
            "Check disk space",
            "Monitor system resources (CPU, memory)"
        ]
    },
    "storage_disk_full": {
        "symptom": "Cannot save results, 'No space left' errors",
        "causes": [
            "Large datasets accumulating",
            "STORAGE_RETENTION_DAYS too high",
            "Cleanup job not running",
            "Old archived data not cleaned"
        ],
        "solutions": [
            "Reduce STORAGE_RETENTION_DAYS",
            "Manually run storage cleanup",
            "Archive old data to external storage",
            "Add more disk space",
            "Enable result compression"
        ]
    },
    "memory_pressure": {
        "symptom": "High memory usage, slow processing, OOM errors",
        "causes": [
            "ASYNC_WORKERS too high",
            "ASYNC_CHUNK_SIZE too large",
            "Memory leaks in processing code",
            "Large files being fully loaded"
        ],
        "solutions": [
            "Reduce ASYNC_WORKERS",
            "Reduce ASYNC_CHUNK_SIZE",
            "Enable streaming processing",
            "Add swap space",
            "Profile code for memory leaks"
        ]
    },
    "job_processing_slow": {
        "symptom": "Jobs taking much longer than expected",
        "causes": [
            "CPU oversubscribed",
            "Disk I/O bottleneck",
            "Complex transformations",
            "Large file size",
            "Network latency for uploads"
        ],
        "solutions": [
            "Check CPU usage: if high, reduce ASYNC_WORKERS",
            "Check disk speed: use SSD if not already",
            "Optimize transformation logic",
            "Split large files before upload",
            "Verify network connectivity"
        ]
    }
}

# ============================================================================
# SECTION 7: BACKUP AND RECOVERY
# ============================================================================

BACKUP_STRATEGY = """
Automated Daily Backup:
  0 2 * * * /usr/bin/tar -czf /backups/storage_$(date +%Y%m%d_%H%M%S).tar.gz /app/storage

Recovery Procedure:
  1. Stop the application: systemctl stop async-processor
  2. Extract backup: tar -xzf /backups/storage_YYYYMMDD_HHMMSS.tar.gz -C /app/
  3. Verify storage: ls -la /app/storage/
  4. Start application: systemctl start async-processor
  5. Verify: curl http://localhost:5000/api/health

Archive Old Data (Monthly):
  find /app/storage -type f -mtime +90 -exec gzip {} \\;
  mv /app/storage/**/*.gz /archive/storage_$(date +%Y%m)/

Disaster Recovery:
  1. If data corrupted, restore from backup
  2. If database locked, check for stale workers: ps aux | grep python
  3. If indices corrupted, rebuild: python scripts/rebuild_indices.py
"""

# ============================================================================
# SECTION 8: PRODUCTION CHECKLIST
# ============================================================================

PRODUCTION_CHECKLIST = """
Pre-Deployment:
  [ ] All tests passing (pytest backend/tests/)
  [ ] Code reviewed and merged
  [ ] Configuration reviewed for security
  [ ] Database backups configured
  [ ] Monitoring and alerting set up
  [ ] Load testing completed
  [ ] Disaster recovery plan documented
  [ ] SSL/TLS certificates installed
  [ ] API authentication configured
  [ ] Rate limiting configured
  [ ] CORS settings reviewed

Deployment:
  [ ] Health checks passing
  [ ] Storage directories created
  [ ] Permissions verified (777 on storage dir)
  [ ] Logs rotating properly
  [ ] Metrics being collected
  [ ] Backup jobs scheduled
  [ ] Cleanup jobs scheduled

Post-Deployment:
  [ ] Monitoring dashboard live
  [ ] Alerts configured and tested
  [ ] Team trained on runbooks
  [ ] Documentation updated
  [ ] On-call rotation established
  [ ] Performance baseline established

Ongoing:
  [ ] Daily: Monitor queue size and job completion
  [ ] Weekly: Review error logs and performance metrics
  [ ] Monthly: Review storage usage and retention policy
  [ ] Quarterly: Test disaster recovery procedures
"""

if __name__ == "__main__":
    print("Async Processing: Deployment and Operational Guide")
    print("="*60)
    print("\nQuick Start:")
    print(QUICK_START_STEPS)
