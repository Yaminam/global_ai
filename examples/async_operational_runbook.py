"""
Async Processing System: Operational Runbook
Step-by-step procedures for common operational tasks
"""

# ============================================================================
# RUNBOOK 1: STARTING THE SYSTEM
# ============================================================================

RUNBOOK_STARTUP = """
PROCEDURE: Start Async Processing System

Duration: 5 minutes
Difficulty: Easy
Prerequisites: Server access, Python 3.10+, Dependencies installed

STEP 1: Verify System Prerequisites
  1.1. Check Python version:
       python --version  # Should be 3.10+
  
  1.2. Verify dependencies installed:
       pip list | grep -E 'flask|pandas|requests'
  
  1.3. Check disk space:
       df -h | grep storage  # Ensure > 10GB free

STEP 2: Configure Environment
  2.1. Set async processing parameters:
       export ASYNC_WORKERS=4
       export ASYNC_QUEUE_MAX_SIZE=1000
       export ASYNC_CHUNK_SIZE=10000
  
  2.2. Set storage configuration:
       export STORAGE_DIR=./storage
       export STORAGE_RETENTION_DAYS=30
  
  2.3. Set Flask environment:
       export FLASK_ENV=production
       export FLASK_DEBUG=0

STEP 3: Create Storage Directories
  3.1. Create storage structure:
       mkdir -p storage/{jobs,results,datasets,analytics,metadata}
  
  3.2. Verify permissions:
       chmod -R 755 storage/

STEP 4: Start Application
  4.1. Navigate to backend:
       cd backend
  
  4.2. Start Flask server:
       python app.py
       # Expected output: "Running on http://0.0.0.0:5000"

STEP 5: Verify System Health
  5.1. Check API health (from new terminal):
       curl http://localhost:5000/api/health
       # Expected: {"status": "healthy", ...}
  
  5.2. Check queue status:
       curl http://localhost:5000/api/async/queue/stats
       # Expected: {"queue_size": 0, "workers": 4, ...}
  
  5.3. Check storage:
       curl http://localhost:5000/api/storage/stats
       # Expected: {"total_jobs": 0, "total_results": 0, ...}

SUCCESS INDICATORS:
  ✓ Server running on port 5000
  ✓ Health check returns healthy
  ✓ Queue statistics show correct number of workers
  ✓ Storage statistics accessible
  ✓ No error messages in console output

TROUBLESHOOTING:
  Problem: "Address already in use"
  Solution: Kill process on port 5000
    lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

  Problem: "Module not found: flask"
  Solution: Install dependencies
    pip install -r requirements.txt

  Problem: "Permission denied on storage directory"
  Solution: Fix permissions
    sudo chmod -R 777 storage/
"""

# ============================================================================
# RUNBOOK 2: SUBMITTING AND MONITORING JOBS
# ============================================================================

RUNBOOK_JOB_SUBMISSION = """
PROCEDURE: Submit and Monitor Async Jobs

Duration: 15 minutes
Difficulty: Intermediate
Prerequisites: System running, test data available

STEP 1: Prepare Test Data File
  1.1. Create sample CSV (test_data.csv):
       name,age,salary,department
       John,28,50000,Engineering
       Jane,32,65000,Engineering
       Bob,25,45000,Sales
       Alice,35,75000,Management

STEP 2: Submit Processing Job
  2.1. Submit async processing job:
       curl -X POST http://localhost:5000/api/async/process \\
            -F "file=@test_data.csv" \\
            -d 'config={"filters": {"age": {"$gte": 30}}}'
       # Capture the job_id from response

  2.2. Save job ID for reference:
       JOB_ID="job-abc123"  # From response

STEP 3: Monitor Job Execution
  3.1. Check job status (immediately):
       curl http://localhost:5000/api/async/status/$JOB_ID
       # Should show "status": "queued"

  3.2. Wait 2-3 seconds, check again:
       curl http://localhost:5000/api/async/status/$JOB_ID
       # Should show "status": "processing" or "completed"

  3.3. Verify completion:
       curl http://localhost:5000/api/async/status/$JOB_ID
       # Should show "status": "completed"

STEP 4: Review Results
  4.1. Check result files exist:
       ls -la storage/results/
       # Should contain: {$JOB_ID}_processing.json

  4.2. View result summary (Python):
       import json
       with open(f'storage/results/{JOB_ID}_processing.json') as f:
           result = json.load(f)
           print(f"Input rows: {result['data']['input_rows']}")
           print(f"Output rows: {result['data']['output_rows']}")
           print(f"Duration: {result['data']['duration_seconds']}s")

STEP 5: Submit Multiple Jobs (Batch)
  5.1. Create script (batch_submit.py):
       import requests
       
       files = ['file1.csv', 'file2.csv', 'file3.csv']
       job_ids = []
       
       for filename in files:
           resp = requests.post(
               'http://localhost:5000/api/async/process',
               files={'file': open(filename, 'rb')}
           )
           job_ids.append(resp.json()['data']['job_id'])
       
       print(f"Submitted {len(job_ids)} jobs: {job_ids}")

  5.2. Run batch submission:
       python batch_submit.py

STEP 6: Monitor Queue
  6.1. Check queue statistics:
       curl http://localhost:5000/api/async/queue/stats | python -m json.tool

  6.2. List all active jobs:
       curl http://localhost:5000/api/async/jobs | python -m json.tool

SUCCESS INDICATORS:
  ✓ Job submitted with 202 Accepted response
  ✓ Job status transitions: queued → processing → completed
  ✓ Result files created in storage/results/
  ✓ Metrics updated in queue stats
  ✓ No error messages in application logs

PERFORMANCE EXPECTATIONS:
  - Job submission: < 100ms
  - Small file (< 1MB): 1-5 seconds processing
  - Medium file (1-10MB): 10-30 seconds processing
  - Large file (> 100MB): 1-5 minutes processing

TROUBLESHOOTING:
  Problem: Status stays "queued" indefinitely
  Solution: Check for worker crashes or exceptions
    Restart system: systemctl restart async-processor
    Check logs: tail -f logs/async_processing.log

  Problem: Job failed with error
  Solution: Review error details
    curl http://localhost:5000/api/async/status/$JOB_ID
    Check "error" field for detailed message
"""

# ============================================================================
# RUNBOOK 3: MANAGING STORAGE
# ============================================================================

RUNBOOK_STORAGE_MANAGEMENT = """
PROCEDURE: Manage Storage and Data Cleanup

Duration: Variable
Difficulty: Intermediate
Prerequisites: System running, admin access

STEP 1: Monitor Storage Usage
  1.1. Check storage statistics:
       curl http://localhost:5000/api/storage/stats | python -m json.tool

  1.2. Check disk usage:
       du -sh storage/
       du -sh storage/*/

  1.3. Get detailed breakdown:
       for dir in storage/*/; do \\
         echo "$dir: $(du -sh $dir | cut -f1)"; \\
       done

STEP 2: View Storage Content
  2.1. List all jobs:
       ls -lt storage/jobs/ | head -20

  2.2. View job metadata:
       cat storage/jobs/job-abc123.json | python -m json.tool

  2.3. List all results:
       ls -lt storage/results/ | head -20

  2.4. Find large result files:
       find storage/results/ -type f -size +100M

STEP 3: Manual Cleanup (if needed urgently)
  3.1. Remove old jobs (older than 60 days):
       find storage/jobs/ -type f -mtime +60 -delete

  3.2. Remove old results:
       find storage/results/ -type f -mtime +60 -delete

  3.3. Compress old files:
       find storage/ -type f -mtime +30 -exec gzip {} \\;

STEP 4: Automatic Cleanup Configuration
  4.1. Update config for automatic cleanup (config.py):
       STORAGE_RETENTION_DAYS = 30  # Clean up files older than 30 days

  4.2. The cleanup runs automatically on:
       - Every 1000 jobs processed
       - Application startup
       - Scheduled maintenance windows

  4.3. Force immediate cleanup (Django management or API):
       # Trigger via admin API (to be added)
       curl -X POST http://localhost:5000/api/admin/storage/cleanup

STEP 5: Archive Old Data
  5.1. Create archive directory:
       mkdir -p archives/$(date +%Y/%m)

  5.2. Archive jobs from 2 months ago:
       find storage/jobs/ -type f -mtime +60 \\
         -exec tar -czf archives/jobs_$(date +%Y%m%d).tar.gz {} \\;

  5.3. Verify archive:
       tar -tzf archives/jobs_*.tar.gz | head -10

  5.4. Delete original after verification:
       find storage/jobs/ -type f -mtime +60 -delete

STEP 6: Rebuild Indices
  6.1. Rebuild jobs index:
       python -c "
       from backend.services.data_storage import DataStorage
       storage = DataStorage()
       storage.rebuild_indices()
       print('Indices rebuilt')
       "

  6.2. Verify indices:
       cat storage/metadata/jobs_index.json | python -m json.tool | head -30

STEP 7: Export Data
  7.1. Export all jobs for backup:
       tar -czf backups/jobs_backup_$(date +%Y%m%d).tar.gz storage/jobs/

  7.2. Export specific results:
       cp storage/results/job-abc123_*.json backups/$(date +%Y%m%d)-abc123.json

  7.3. Create CSV export:
       python -c "
       import json
       import csv
       results = []
       for f in glob.glob('storage/results/*_processing.json'):
           with open(f) as fp:
               data = json.load(fp)
               results.append(data['data'])
       
       with open('export.csv', 'w') as f:
           writer = csv.DictWriter(f, fieldnames=['job_id', 'input_rows', 'output_rows'])
           writer.writerows(results)
       "

STORAGE CLEANUP SCHEDULE:
  Daily: Check storage usage (automated)
  Weekly: Review storage trends, archive if needed
  Monthly: Full cleanup of files older than 30 days
  Quarterly: Verify backups, test recovery procedures

RETENTION POLICY:
  ├── Active jobs (0-7 days): Keep all data
  ├── Recent jobs (7-30 days): Keep indexed metadata
  ├── Old jobs (30-90 days): Archive to cold storage
  └── Historical (90+ days): Delete or long-term archive

SUCCESS INDICATORS:
  ✓ Storage size stable or decreasing
  ✓ Indices valid and accessible
  ✓ No storage errors in logs
  ✓ Old files being cleaned up on schedule
  ✓ Archives verified and available

TROUBLESHOOTING:
  Problem: Storage growing too large
  Solution: Reduce STORAGE_RETENTION_DAYS and run cleanup
  
  Problem: Cleanup fails with permission error
  Solution: Check directory permissions: chmod 755 storage/
  
  Problem: Cannot find specific job data
  Solution: Check job_index: grep job_id storage/metadata/jobs_index.json
"""

# ============================================================================
# RUNBOOK 4: PERFORMANCE TUNING
# ============================================================================

RUNBOOK_PERFORMANCE_TUNING = """
PROCEDURE: Tune Async Processing Performance

Duration: 30+ minutes
Difficulty: Advanced
Prerequisites: Performance monitoring in place, baseline established

STEP 1: Establish Performance Baseline
  1.1. Collect metrics over 24 hours:
       - Average queue size
       - Average processing time
       - Jobs completed per hour
       - CPU and memory usage patterns
       - Storage growth rate

  1.2. Document baseline:
       echo "Queue Size: 5 jobs avg, peak 20"
       echo "Processing Time: 15 seconds avg"
       echo "Throughput: 240 jobs/day"
       echo "CPU: 45% avg, 85% peak"
       echo "Memory: 800MB avg, 1.2GB peak"

STEP 2: Identify Performance Issues
  2.1. Check queue depth:
       curl http://localhost:5000/api/async/queue/stats | grep queue_size

  2.2. If queue_size > 20 consistently:
       Problem: Workers can't keep up
       Action: Go to STEP 4 (optimize workers)

  2.3. Check processing time:
       curl http://localhost:5000/api/async/jobs | grep processing_time

  2.4. If processing_time > 30 seconds for small files:
       Problem: Processing inefficiency
       Action: Go to STEP 5 (optimize processing)

STEP 3: Adjust Worker Pool
  3.1. Increase workers for I/O-bound workloads:
       Current: ASYNC_WORKERS=4
       Proposed: ASYNC_WORKERS=8 or 12
       Formula: (2 * CPU_CORES) for CPU-bound
                (4 * CPU_CORES) for I/O-bound

  3.2. Update configuration (backend/config.py):
       ASYNC_WORKERS = 8

  3.3. Restart application:
       systemctl restart async-processor

  3.4. Verify workers started:
       curl http://localhost:5000/api/async/queue/stats | grep workers

  3.5. Monitor impact:
       # Run test load and compare metrics
       ab -n 100 -c 10 http://localhost:5000/api/health

STEP 4: Optimize Chunk Size
  4.1. Current chunk size too small? (CPU usage high):
       Let ASYNC_CHUNK_SIZE = 10000 currently
       Try: ASYNC_CHUNK_SIZE = 50000

  4.2. Current chunk size too large? (Memory usage high):
       Let ASYNC_CHUNK_SIZE = 100000 currently
       Try: ASYNC_CHUNK_SIZE = 25000

  4.3. Update configuration:
       ASYNC_CHUNK_SIZE = 50000

  4.4. Restart and test:
       systemctl restart async-processor

  4.5. Measure improvement:
       Watch for: Processing time decrease, memory reduction

STEP 5: Monitor and Record
  5.1. Run sustained load test (30 minutes):
       while true; do
         curl -X POST http://localhost:5000/api/async/process \\
              -F "file=@test_data.csv" &
         sleep 2
       done

  5.2. Record metrics:
       - Every 5 minutes: queue stats, processing times, errors
       - CPU and memory usage (top command)
       - Storage growth

  5.3. Compare to baseline:
       If queue_size reduced: ✓ Improvement achieved
       If processing_time reduced: ✓ Improvement achieved
       If errors increased: Revert changes and retry

STEP 6: Fine-Tune Queue Size Limits
  6.1. Current max: ASYNC_QUEUE_MAX_SIZE=1000
       If queue fills up: Increase to 2000
       If memory high: Decrease to 500

  6.2. Calculate optimal:
       Optimal = Peak_Load * Average_Job_Duration * 0.8
       Example: 10 jobs/sec * 15 sec/job * 0.8 = 120 queue size

  6.3. Apply and test

STEP 7: Profile Processing Code
  7.1. Enable profiling (backend/services/async_processor.py):
       import cProfile
       import pstats
       
       pr = cProfile.Profile()
       pr.enable()
       # ... processing code ...
       pr.disable()
       
       ps = pstats.Stats(pr)
       ps.sort_stats('cumulative')
       ps.print_stats(20)  # Top 20 functions by time

  7.2. Run profile and analyze:
       python -m cProfile -s cumtime app.py > profile.txt

  7.3. Identify bottlenecks:
       - Look for functions with high cumulative time
       - Consider optimization strategies:
         * Vectorization (use pandas/numpy)
         * Caching (memoization)
         * Parallelization (within single job)

FINAL TUNING CHECKLIST:
  [ ] Baseline metrics documented
  [ ] Worker pool optimized for workload type
  [ ] Chunk size optimal for memory/speed tradeoff
  [ ] Queue size handles peak load
  [ ] No error spikes after changes
  [ ] Processing time meets SLA
  [ ] CPU/Memory within acceptable ranges
  [ ] Storage growth rate acceptable
  [ ] All metrics documented for future reference

PERFORMANCE TARGETS:
  Target Queue Size: < 10 during normal, < 50 during peak
  Target Processing Time: < 10 seconds per small job
  Target Error Rate: < 0.1%
  Target CPU Usage: 40-70% optimal
  Target Memory Usage: 70-80% of allocated
"""

# ============================================================================
# RUNBOOK 5: EMERGENCY PROCEDURES
# ============================================================================

RUNBOOK_EMERGENCY = """
PROCEDURE: Emergency Response Procedures

EMERGENCY 1: Queue Full (503 Errors)
  Priority: High
  Impact: New jobs being rejected
  
  Immediate Actions:
    1. Check queue: curl .../api/async/queue/stats
    2. Current queue_size: 1200/1000 (example)
    3. Identify blocked worker: check logs
    4. Temporary Solution (30 seconds):
       - Increase memory limits
       - Reduce incoming request rate at load balancer
    5. Permanent Solution:
       - Increase ASYNC_WORKERS from 4 to 8
       - Increase ASYNC_QUEUE_MAX_SIZE from 1000 to 2000
       - Add instances (scale horizontally)

EMERGENCY 2: Worker Process Crash
  Priority: Critical
  Impact: Jobs stuck in 'processing'
  
  Recovery Steps:
    1. Check running processes: ps aux | grep python
    2. Identify dead workers: Count should equal ASYNC_WORKERS
    3. Kill Flask process: pkill -f 'python app.py'
    4. Wait 5 seconds for graceful shutdown
    5. Review logs: tail -100 logs/async_processing.log
    6. Fix issue (if identifiable):
       - Out of memory: No → See EMERGENCY 8
       - File permission: Yes → Fix and retry
       - Code error: Yes → Revert last deployment
    7. Restart: cd backend && python app.py
    8. Verify recovery: curl .../api/health

EMERGENCY 3: Disk Full
  Priority: Critical
  Impact: Cannot save new results, system unstable
  
  Immediate Actions:
    1. Check disk: df -h
    2. Identify large files: du -sh storage/*
    3. Temporary: Delete old archives
       find storage/ -mtime +90 -delete
    4. Check needed space: du -sh storage/ total bytes needed
    5. Permanent:
       - Increase storage device
       - Move to larger volume
       - Add external storage

EMERGENCY 4: Memory Leak
  Priority: High
  Impact: Gradual slowdown, eventual OOM crash
  
  Detection:
    1. Memory growing while queue empty: top -p <pid>
    2. Memory doesn't decrease after job completion
    3. Pattern: 100MB → 200MB → 300MB over hours
    
  Response:
    1. Enable daily restart (temporary):
       0 2 * * * systemctl restart async-processor
    2. Enable memory profiling:
       python -m memory_profiler app.py
    3. Investigate code:
       Look for growing data structures, unreleased resources
    4. Implement fix:
       Add cleanup code, close file handles, clear caches

EMERGENCY 5: Network Disconnection
  Priority: Medium
  Impact: Clients can't reach API
  
  Check Connectivity:
    1. Server itself running: ps aux | grep python
    2. Port open: netstat -an | grep 5000
    3. Network accessible: ping server_ip
    4. Firewall rules: sudo iptables -L | grep 5000
    
  Solutions:
    1. Restart network: systemctl restart network
    2. Restart application: systemctl restart async-processor
    3. Check load balancer: Is traffic being routed?

EMERGENCY 6: Data Corruption
  Priority: Critical
  Impact: Loss of job history and results
  
  Immediate:
    1. Stop accepting new jobs (redirect to backup system)
    2. Create snapshot: tar -czf backup_$(date +%s).tar.gz storage/
    3. Don't delete originals yet
    
  Recovery Options:
    Option 1 - Restore from backup (if available):
      rm -rf storage && tar -xzf backup_date.tar.gz
    
    Option 2 - Rebuild indices:
      python scripts/rebuild_indices.py
    
    Option 3 - Partial recovery:
      Copy uncorrupted files from snapshot
    
    Option 4 - Start fresh:
      If too corrupted, clear storage and restart

EMERGENCY 7: CPU Maxed Out
  Priority: High
  Impact: System unresponsive, slow processing
  
  Immediate Diagnosis:
    1. top command: Find CPU-heavy processes
    2. Check if expected (large job processing): Normal
    3. Check if unexpected: Investigate
    
  If Legitimate Work:
    1. Reduce incoming load temporarily
    2. Increase available CPU resources
    3. Optimize queries/processing logic
    
  If Runaway Process:
    1. Kill problematic worker: kill -9 <pid>
    2. Check logs for infinite loops
    3. Revert recent code changes
    4. Restart: systemctl restart async-processor

EMERGENCY 8: Out of Memory
  Priority: Critical
  Impact: Process crashes, data loss risk
  
  Immediate:
    1. Check memory: free -h
    2. Kill non-essential services
    3. Reduce ASYNC_WORKERS temporarily: export ASYNC_WORKERS=1
    4. Restart Flask with reduced workers
    
  Investigation:
    1. Identify memory hog: ps aux --sort=-%mem | head
    2. Check for leaks: Memory usage pattern over time
    3. Review recent changes: What code changed?
    4. Test with smaller file size
    
  Long-term Solution:
    1. Add more RAM to server
    2. Reduce ASYNC_CHUNK_SIZE for memory efficiency
    3. Optimize data structures
    4. Consider distributed processing

RECOVERY CHECKLIST:
  [ ] Immediate action taken (stop bleeding)
  [ ] Root cause identified
  [ ] Temporary workaround in place
  [ ] Permanent fix implemented/deployed
  [ ] Verification that issue resolved
  [ ] Monitoring set up to catch recurrence
  [ ] Post-incident review scheduled
  [ ] Documentation updated

ESCALATION CONTACTS:
  - Level 1: On-call engineer (contact info)
  - Level 2: System architect (contact info)
  - Level 3: VP Engineering (contact info)
  - Critical: All hands (declare incident, page team)
"""

if __name__ == "__main__":
    print("Async Processing: Operational Runbook")
    print("="*60)
    print("\nAvailable Runbooks:")
    print("1. RUNBOOK_STARTUP")
    print("2. RUNBOOK_JOB_SUBMISSION")
    print("3. RUNBOOK_STORAGE_MANAGEMENT")
    print("4. RUNBOOK_PERFORMANCE_TUNING")
    print("5. RUNBOOK_EMERGENCY")
