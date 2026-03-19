"""
Example: Using Async Processing API

This script demonstrates how to use the async processing features
of the Advanced Data Processing & Analytics API.

Requirements:
- Server running: python backend/app.py
- requests library: pip install requests
"""

import requests
import time
import json

# API Base URL
BASE_URL = "http://localhost:5000/api"

# Helper functions
def upload_file(file_path):
    """Upload a file and get dataset ID"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'description': 'Example data', 'category': 'demo'}
        response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
    
    if response.status_code == 200:
        return response.json()['data']['file_path']
    else:
        print(f"Upload failed: {response.json()}")
        return None


def submit_async_process(file_path, config):
    """Submit an async processing job"""
    payload = {
        'file_path': file_path,
        'config': config
    }
    
    response = requests.post(f"{BASE_URL}/async/process", json=payload)
    
    if response.status_code == 202:  # Accepted
        data = response.json()['data']
        print(f"\n✓ Job submitted: {data['job_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Queue size: {data['queue_size']}")
        return data['job_id']
    else:
        print(f"Submission failed: {response.json()}")
        return None


def get_job_status(job_id):
    """Check job status"""
    response = requests.get(f"{BASE_URL}/async/status/{job_id}")
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_queue_stats():
    """Get async queue statistics"""
    response = requests.get(f"{BASE_URL}/async/jobs")
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_storage_stats():
    """Get data storage statistics"""
    response = requests.get(f"{BASE_URL}/storage/stats")
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


# Example 1: Submit async processing job
def example_async_processing():
    """Example: Submit an async processing job"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Async Processing Job")
    print("="*60)
    
    # Configuration for processing
    config = {
        'filters': {
            'age': {'$gte': 18},
            'status': 'active'
        },
        'transformations': [
            {
                'type': 'normalize',
                'columns': ['salary', 'experience']
            }
        ],
        'sorting': {
            'salary': 'desc'
        }
    }
    
    # Note: Replace with actual file path
    file_path = "uploads/sample_data.csv"
    
    # Submit job
    job_id = submit_async_process(file_path, config)
    
    if job_id:
        # Check status periodically
        for i in range(5):
            time.sleep(2)
            status = get_job_status(job_id)
            
            if status:
                print(f"\n  Check {i+1}: Status = {status.get('status')}")
                if status.get('status') == 'completed':
                    print("  ✓ Job completed!")
                    break
            else:
                print(f"\n  Check {i+1}: Job not found (still processing)")


# Example 2: Async validation
def example_async_validation():
    """Example: Submit async validation job"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Async Validation Job")
    print("="*60)
    
    payload = {
        'file_path': 'uploads/data.csv',
        'rules': {
            'email': 'email',
            'phone': 'phone',
            'age': 'integer'
        }
    }
    
    response = requests.post(f"{BASE_URL}/async/validate", json=payload)
    
    if response.status_code == 202:
        job_id = response.json()['data']['job_id']
        print(f"\n✓ Validation job submitted: {job_id}")
        print(f"  Check status at: /api/async/status/{job_id}")
    else:
        print(f"Failed: {response.json()}")


# Example 3: Async analytics
def example_async_analytics():
    """Example: Submit async analytics job"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Async Analytics Job")
    print("="*60)
    
    payload = {
        'file_path': 'uploads/data.csv'
    }
    
    response = requests.post(f"{BASE_URL}/async/analytics", json=payload)
    
    if response.status_code == 202:
        job_id = response.json()['data']['job_id']
        print(f"\n✓ Analytics job submitted: {job_id}")
        print(f"  Check status at: /api/async/status/{job_id}")
    else:
        print(f"Failed: {response.json()}")


# Example 4: Monitor queue
def example_monitor_queue():
    """Example: Monitor the async queue"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Monitor Async Queue")
    print("="*60)
    
    # Get active jobs
    jobs_data = get_queue_stats()
    if jobs_data:
        print(f"\nActive jobs: {jobs_data['total']}")
        for job in jobs_data.get('jobs', [])[:3]:
            print(f"  - {job['job_id']}: {job.get('status')}")
    
    # Get storage stats
    storage = get_storage_stats()
    if storage:
        print(f"\nStorage Statistics:")
        print(f"  Total jobs: {storage['total_jobs']}")
        print(f"  Total results: {storage['total_results']}")
        print(f"  Total datasets: {storage['total_datasets']}")
        print(f"  Total analytics: {storage['total_analytics']}")
        print(f"  Storage path: {storage['storage_path']}")


# Example 5: Sync vs Async comparison
def example_sync_vs_async():
    """Example: Compare sync vs async processing"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Sync vs Async Comparison")
    print("="*60)
    
    config = {
        'filters': {'age': {'$gte': 25}}
    }
    
    # Async request (returns immediately)
    print("\nAsync Processing (non-blocking):")
    payload_async = {
        'file_path': 'uploads/data.csv',
        'config': config,
        'async': True
    }
    response = requests.post(f"{BASE_URL}/process", json=payload_async)
    print(f"  Status Code: {response.status_code} (202 = Accepted)")
    print(f"  Response time: < 100ms")
    
    # Sync request (waits for completion)
    print("\nSync Processing (blocking):")
    payload_sync = {
        'file_path': 'uploads/data.csv',
        'config': config,
        'async': False
    }
    response = requests.post(f"{BASE_URL}/process", json=payload_sync)
    print(f"  Status Code: {response.status_code} (200 = OK)")
    print(f"  Response time: depends on data size")


# Example 6: Batch processing with async
def example_batch_processing():
    """Example: Submit multiple jobs asynchronously"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Batch Async Processing")
    print("="*60)
    
    files = [
        ('uploads/data1.csv', {'filters': {'age': {'$gte': 20}}}),
        ('uploads/data2.csv', {'filters': {'salary': {'$lte': 100000}}}),
        ('uploads/data3.csv', {'transformations': [{'type': 'normalize', 'columns': ['amount']}]})
    ]
    
    job_ids = []
    print("\nSubmitting batch jobs:")
    
    for file_path, config in files:
        job_id = submit_async_process(file_path, config)
        if job_id:
            job_ids.append(job_id)
    
    print(f"\nSubmitted {len(job_ids)} jobs")
    print("Job IDs:", job_ids)
    
    # Monitor progress
    print("\nMonitoring progress:")
    completed = 0
    while completed < len(job_ids):
        for job_id in job_ids:
            status = get_job_status(job_id)
            if status and status.get('status') == 'completed':
                print(f"  ✓ {job_id}: Completed")
                completed += 1
        
        if completed < len(job_ids):
            time.sleep(5)


# Main execution
if __name__ == '__main__':
    print("\n" + "="*60)
    print("Async Processing API Examples")
    print("="*60)
    print("\nNote: Ensure server is running on http://localhost:5000")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is running")
            
            # Run examples
            # example_async_processing()
            # example_async_validation()
            # example_async_analytics()
            example_monitor_queue()
            # example_sync_vs_async()
            # example_batch_processing()
            
        else:
            print("✗ Server is not responding correctly")
    
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure it's running:")
        print("  python backend/app.py")
