"""
Async Processing Integration Examples: Real-World Scenarios
Complete examples showing best practices, error handling, and production patterns
"""

# ============================================================================
# EXAMPLE 1: SIMPLE FILE UPLOAD AND PROCESSING
# ============================================================================

EXAMPLE_SIMPLE_UPLOAD = """
import requests
import json
import time

def process_file_simple(filepath):
    '''
    Upload and process a single file asynchronously
    Returns the job_id for tracking
    '''
    
    # Upload file
    with open(filepath, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            'http://localhost:5000/api/async/process',
            files=files
        )
    
    if response.status_code == 202:
        job_data = response.json()['data']
        job_id = job_data['job_id']
        print(f"Job queued: {job_id}")
        print(f"Queue position: {job_data['queue_position']}")
        return job_id
    else:
        print(f"Error: {response.text}")
        return None

def wait_for_completion(job_id, timeout=300):
    '''
    Poll job status until completion
    Timeout in seconds
    '''
    start_time = time.time()
    
    while True:
        response = requests.get(
            f'http://localhost:5000/api/async/status/{job_id}'
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            status = data['status']
            
            print(f"Status: {status}")
            
            if status == 'completed':
                return data
            elif status == 'failed':
                print(f"Error: {data.get('error')}")
                return None
        
        # Check timeout
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for job {job_id}")
            return None
        
        # Wait before next check
        time.sleep(2)

# Usage
if __name__ == "__main__":
    job_id = process_file_simple("test_data.csv")
    if job_id:
        result = wait_for_completion(job_id)
        if result:
            print("\\nResults:")
            print(f"Input rows: {result['input_rows']}")
            print(f"Output rows: {result['output_rows']}")
            print(f"Processing time: {result['duration_seconds']}s")
"""

# ============================================================================
# EXAMPLE 2: BATCH PROCESSING WITH MONITORING
# ============================================================================

EXAMPLE_BATCH_PROCESSING = """
import requests
import json
import time
from datetime import datetime
from typing import List, Dict

class BatchProcessor:
    '''Handle multiple file processing jobs with monitoring'''
    
    def __init__(self, api_base='http://localhost:5000'):
        self.api_base = api_base
        self.jobs = {}
    
    def submit_batch(self, filepaths: List[str], 
                     config: Dict = None) -> List[str]:
        '''
        Submit multiple files for processing
        Returns list of job IDs
        '''
        job_ids = []
        
        for filepath in filepaths:
            try:
                with open(filepath, 'rb') as f:
                    files = {'file': f}
                    data = {}
                    if config:
                        data['config'] = json.dumps(config)
                    
                    response = requests.post(
                        f'{self.api_base}/api/async/process',
                        files=files,
                        data=data
                    )
                
                if response.status_code == 202:
                    job_id = response.json()['data']['job_id']
                    job_ids.append(job_id)
                    self.jobs[job_id] = {
                        'filepath': filepath,
                        'submitted': datetime.now(),
                        'status': 'queued'
                    }
                    print(f"✓ Submitted: {filepath} (ID: {job_id})")
                else:
                    print(f"✗ Failed: {filepath} - {response.text}")
            
            except Exception as e:
                print(f"✗ Error: {filepath} - {str(e)}")
        
        return job_ids
    
    def monitor_batch(self, job_ids: List[str], 
                      poll_interval: int = 2,
                      timeout: int = 300) -> Dict:
        '''
        Monitor all jobs until complete
        Returns summary of results
        '''
        start_time = time.time()
        completed = 0
        failed = 0
        
        while True:
            # Check all jobs
            all_done = True
            for job_id in job_ids:
                status = self.get_job_status(job_id)
                
                if status in ['completed', 'failed']:
                    if self.jobs[job_id]['status'] != status:
                        self.jobs[job_id]['status'] = status
                        if status == 'completed':
                            completed += 1
                        else:
                            failed += 1
                else:
                    all_done = False
            
            # Print progress
            print(f"Progress: {completed + failed}/{len(job_ids)} "
                  f"(✓ {completed}, ✗ {failed})")
            
            if all_done:
                break
            
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"Timeout: {len(job_ids) - completed - failed} jobs still running")
                break
            
            time.sleep(poll_interval)
        
        return {
            'total': len(job_ids),
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / len(job_ids)) * 100 if job_ids else 0
        }
    
    def get_job_status(self, job_id: str) -> str:
        '''Get current status of a job'''
        response = requests.get(
            f'{self.api_base}/api/async/status/{job_id}'
        )
        if response.status_code == 200:
            return response.json()['data']['status']
        return 'error'
    
    def get_results(self, job_id: str) -> Dict:
        '''Get detailed results for a job'''
        response = requests.get(
            f'{self.api_base}/api/async/status/{job_id}'
        )
        if response.status_code == 200:
            return response.json()['data']
        return None

# Usage example
if __name__ == "__main__":
    processor = BatchProcessor()
    
    # Submit batch
    files = ['file1.csv', 'file2.csv', 'file3.csv', 'file4.csv', 'file5.csv']
    config = {'filters': {'amount': {'$gte': 100}}}
    
    job_ids = processor.submit_batch(files, config)
    print(f"\\nSubmitted {len(job_ids)} jobs\\n")
    
    # Monitor
    summary = processor.monitor_batch(job_ids, timeout=600)
    print(f"\\nBatch Summary:")
    print(f"Total: {summary['total']}")
    print(f"Completed: {summary['completed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
"""

# ============================================================================
# EXAMPLE 3: ERROR HANDLING AND RETRY LOGIC
# ============================================================================

EXAMPLE_ERROR_HANDLING = """
import requests
import time
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class RobustAsyncClient:
    '''Async client with comprehensive error handling and retry logic'''
    
    def __init__(self, api_base='http://localhost:5000', 
                 max_retries=3, retry_delay=2):
        self.api_base = api_base
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AsyncClient/1.0'
        })
    
    def submit_with_retry(self, filepath: str, 
                         config: Dict = None) -> Optional[str]:
        '''
        Submit file with automatic retry on transient failures
        Returns job_id or None if all retries exhausted
        '''
        for attempt in range(self.max_retries):
            try:
                with open(filepath, 'rb') as f:
                    files = {'file': f}
                    data = {}
                    if config:
                        data['config'] = json.dumps(config)
                    
                    response = self.session.post(
                        f'{self.api_base}/api/async/process',
                        files=files,
                        data=data,
                        timeout=10
                    )
                
                if response.status_code == 202:
                    job_id = response.json()['data']['job_id']
                    logger.info(f"Job submitted: {job_id}")
                    return job_id
                
                elif response.status_code == 503:
                    logger.warning(f"Queue full (attempt {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))
                        continue
                
                elif response.status_code in [400, 404]:
                    logger.error(f"Client error: {response.text}")
                    return None
                
                else:
                    logger.error(f"Server error: {response.status_code}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
            
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * 2)
                    continue
            
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return None
        
        logger.error(f"Failed after {self.max_retries} retries")
        return None
    
    def get_status_safe(self, job_id: str) -> Optional[Dict]:
        '''
        Get job status with error handling
        Returns status dict or None on error
        '''
        try:
            response = requests.get(
                f'{self.api_base}/api/async/status/{job_id}',
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()['data']
            
            elif response.status_code == 404:
                logger.warning(f"Job not found: {job_id}")
                return None
            
            else:
                logger.error(f"Error: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None
    
    def wait_with_backoff(self, job_id: str, 
                         max_wait: int = 300) -> Optional[Dict]:
        '''
        Wait for job completion with exponential backoff for polling
        Reduces server load as job execution progresses
        '''
        start_time = time.time()
        poll_interval = 1  # Start with 1 second
        max_poll_interval = 10
        
        while True:
            status = self.get_status_safe(job_id)
            
            if status is None:
                return None
            
            if status['status'] in ['completed', 'failed']:
                return status
            
            # Check timeout
            if time.time() - start_time > max_wait:
                logger.error(f"Timeout waiting for {job_id}")
                return None
            
            # Exponential backoff for polling
            logger.debug(f"Polling every {poll_interval}s")
            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, max_poll_interval)

# Usage
if __name__ == "__main__":
    client = RobustAsyncClient()
    
    # Submit with retry
    job_id = client.submit_with_retry('data.csv')
    
    if job_id:
        # Wait with smart polling
        result = client.wait_with_backoff(job_id)
        
        if result and result['status'] == 'completed':
            print(f"Processed: {result['output_rows']} rows")
        else:
            print(f"Job failed or timed out")
"""

# ============================================================================
# EXAMPLE 4: PRODUCTION MONITORING AND ALERTING
# ============================================================================

EXAMPLE_MONITORING = """
import requests
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class QueueMonitor:
    '''Monitor async queue health and trigger alerts'''
    
    def __init__(self, api_base='http://localhost:5000',
                 alert_thresholds=None):
        self.api_base = api_base
        self.thresholds = alert_thresholds or {
            'queue_size': 100,  # Alert if queue > 100
            'error_rate': 0.05,  # Alert if > 5% error rate
            'response_time': 30,  # Alert if > 30s per job
            'idle_worker_count': 0  # Alert if all workers idle
        }
        self.metric_history = []
    
    def get_queue_stats(self) -> dict:
        '''Get current queue statistics'''
        try:
            response = requests.get(
                f'{self.api_base}/api/async/queue/stats',
                timeout=5
            )
            return response.json()['data']
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return None
    
    def get_storage_stats(self) -> dict:
        '''Get storage usage statistics'''
        try:
            response = requests.get(
                f'{self.api_base}/api/storage/stats',
                timeout=5
            )
            return response.json()['data']
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return None
    
    def check_health(self) -> dict:
        '''Check system health and return alert status'''
        queue_stats = self.get_queue_stats()
        storage_stats = self.get_storage_stats()
        
        if not queue_stats or not storage_stats:
            return {'status': 'error', 'message': 'Cannot reach API'}
        
        alerts = []
        
        # Check queue size
        if queue_stats['queue_size'] > self.thresholds['queue_size']:
            alerts.append({
                'severity': 'warning',
                'message': f"Queue size high: {queue_stats['queue_size']}"
            })
        
        # Check error rate
        total = queue_stats['total']
        failed = queue_stats['failed']
        if total > 0:
            error_rate = failed / total
            if error_rate > self.thresholds['error_rate']:
                alerts.append({
                    'severity': 'critical',
                    'message': f"High error rate: {error_rate*100:.1f}%"
                })
        
        # Check storage usage
        if storage_stats['total_size_bytes'] > 100 * 1024 * 1024 * 1024:  # 100GB
            alerts.append({
                'severity': 'warning',
                'message': "Storage usage high"
            })
        
        # Record metrics
        self.metric_history.append({
            'timestamp': datetime.now(),
            'queue_size': queue_stats['queue_size'],
            'processed': queue_stats['processed'],
            'failed': queue_stats['failed'],
            'workers': queue_stats['workers']
        })
        
        return {
            'status': 'healthy' if not alerts else 'degraded',
            'alerts': alerts,
            'stats': {
                'queue': queue_stats,
                'storage': storage_stats
            }
        }
    
    def generate_report(self) -> str:
        '''Generate monitoring report'''
        health = self.check_health()
        
        lines = []
        lines.append('=== Async Processing Health Report ===')
        lines.append(f'Generated: {datetime.now().isoformat()}')
        lines.append(f\"Status: {health['status'].upper()}\")
        lines.append('')
        lines.append('Queue Status:')
        lines.append(f\"  - Size: {health['stats']['queue']['queue_size']}\")
        lines.append(f\"  - Workers: {health['stats']['queue']['workers']}\")
        lines.append(f\"  - Total Processed: {health['stats']['queue']['processed']}\")
        lines.append(f\"  - Failed: {health['stats']['queue']['failed']}\")
        lines.append('')
        lines.append('Storage Status:')
        lines.append(f\"  - Jobs: {health['stats']['storage']['total_jobs']}\")
        lines.append(f\"  - Results: {health['stats']['storage']['total_results']}\")
        
        storage_size_gb = health['stats']['storage']['total_size_bytes'] / (1024.0 * 1024.0 * 1024.0)
        lines.append(f'  - Size: {storage_size_gb:.1f} GB')
        lines.append('')
        lines.append('Alerts:')
        
        for alert in health['alerts']:
            severity = alert['severity'].upper()
            message = alert['message']
            lines.append(f'  [{severity}] {message}')
        
        return '\\n'.join(lines)

# Usage
if __name__ == "__main__":
    monitor = QueueMonitor()
    
    # Get instant health check
    health = monitor.check_health()
    print(f"Status: {health['status']}")
    
    # Generate detailed report
    report = monitor.generate_report()
    print(report)
"""

# ============================================================================
# EXAMPLE 5: INTEGRATION WITH DATA PIPELINE
# ============================================================================

EXAMPLE_PIPELINE_INTEGRATION = """
import requests
import json
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class AsyncPipelineStep:
    '''Decorator to make data processing steps async-compatible'''
    
    def __init__(self, api_base='http://localhost:5000'):
        self.api_base = api_base
    
    def process_async(self, filepath, operation_config):
        '''
        Submit data processing to async system
        Returns job_id
        '''
        with open(filepath, 'rb') as f:
            files = {'file': f}
            data = {'config': json.dumps(operation_config)}
            
            response = requests.post(
                f'{self.api_base}/api/async/process',
                files=files,
                data=data
            )
        
        if response.status_code == 202:
            return response.json()['data']['job_id']
        raise Exception(f"Async submission failed: {response.text}")
    
    def wait_and_fetch_results(self, job_id):
        '''
        Wait for job completion and fetch results
        Returns processed data
        '''
        import time
        
        while True:
            response = requests.get(
                f'{self.api_base}/api/async/status/{job_id}'
            )
            
            data = response.json()['data']
            
            if data['status'] == 'completed':
                # Load actual results
                result_file = data.get('result_file')
                if result_file:
                    with open(result_file) as f:
                        return json.load(f)
                return data
            
            elif data['status'] == 'failed':
                raise Exception(f"Job failed: {data.get('error')}")
            
            time.sleep(2)

class DataPipeline:
    '''Multi-step data processing pipeline using async'''
    
    def __init__(self):
        self.async_step = AsyncPipelineStep()
    
    def run_pipeline(self, input_file):
        '''
        Run multi-step pipeline asynchronously
        Step 1: Validate data
        Step 2: Filter and clean
        Step 3: Transform
        Step 4: Analytics
        '''
        logger.info(f"Starting pipeline for {input_file}")
        
        try:
            # Step 1: Validation
            logger.info("Step 1: Validating data...")
            job1 = self.async_step.process_async(
                input_file,
                {'operation': 'validate'}
            )
            result1 = self.async_step.wait_and_fetch_results(job1)
            logger.info(f"Validation complete: {result1}")
            
            # Step 2: Filter and Clean
            logger.info("Step 2: Filtering and cleaning...")
            job2 = self.async_step.process_async(
                input_file,
                {
                    'filters': {'status': 'active'},
                    'transformations': [
                        {'type': 'drop_columns', 'columns': ['temp']}
                    ]
                }
            )
            result2 = self.async_step.wait_and_fetch_results(job2)
            logger.info(f"Cleaning complete: {result2}")
            
            # Step 3: Analytics
            logger.info("Step 3: Running analytics...")
            job3 = self.async_step.process_async(
                input_file,
                {'operation': 'analytics'}
            )
            result3 = self.async_step.wait_and_fetch_results(job3)
            logger.info(f"Analytics complete: {result3}")
            
            return {
                'validation': result1,
                'cleaning': result2,
                'analytics': result3,
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {'status': 'failed', 'error': str(e)}

# Usage
if __name__ == "__main__":
    pipeline = DataPipeline()
    result = pipeline.run_pipeline('input_data.csv')
    print(json.dumps(result, indent=2))
"""

if __name__ == "__main__":
    print("Async Processing Integration Examples")
    print("="*60)
    print("\nFive production-ready examples included:")
    print("1. Simple file upload and processing")
    print("2. Batch processing with monitoring")
    print("3. Error handling and retry logic")
    print("4. Production monitoring and alerting")
    print("5. Integration with data pipelines")
