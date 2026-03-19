"""
Asynchronous job queue for processing tasks
"""

import threading
import queue
import json
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from utils.helpers import generate_uuid, get_timestamp


class JobTask:
    """Represents a job task to be processed"""
    
    def __init__(self, job_id: str, task_type: str, payload: Dict[str, Any], 
                 callback: Optional[Callable] = None):
        """Initialize job task
        
        Args:
            job_id: Unique job ID
            task_type: Type of task (process, validate, analytics)
            payload: Task data
            callback: Optional callback function when task completes
        """
        self.job_id = job_id
        self.task_type = task_type
        self.payload = payload
        self.callback = callback
        self.created_at = get_timestamp()
    
    def __repr__(self):
        return f"JobTask(job_id={self.job_id}, type={self.task_type})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'task_type': self.task_type,
            'payload': self.payload,
            'created_at': self.created_at
        }


class AsyncJobQueue:
    """Manages asynchronous job processing with worker threads"""
    
    def __init__(self, num_workers: int = 4, logger: Optional[logging.Logger] = None):
        """Initialize async job queue
        
        Args:
            num_workers: Number of worker threads
            logger: Logger instance
        """
        self.task_queue = queue.Queue()
        self.num_workers = num_workers
        self.logger = logger or logging.getLogger(__name__)
        self.workers = []
        self.running = False
        self.job_handlers = {}  # Map task_type to handler function
        self.max_queue_size = 1000
        self.processed_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type
        
        Args:
            task_type: Type of task
            handler: Handler function
        """
        self.job_handlers[task_type] = handler
        self.logger.info(f"Registered handler for task type: {task_type}")
    
    def start(self):
        """Start worker threads"""
        if self.running:
            self.logger.warning("Job queue is already running")
            return
        
        self.running = True
        
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"JobWorker-{i}",
                daemon=False
            )
            worker.start()
            self.workers.append(worker)
        
        self.logger.info(f"Started {self.num_workers} job queue workers")
    
    def stop(self, timeout: int = 30):
        """Stop worker threads gracefully
        
        Args:
            timeout: Timeout in seconds to wait for workers
        """
        self.logger.info("Stopping job queue workers...")
        self.running = False
        
        # Send stop signals
        for _ in range(self.num_workers):
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=timeout)
        
        self.workers = []
        self.logger.info("All job queue workers stopped")
    
    def submit_job(self, job_id: str, task_type: str, payload: Dict[str, Any],
                   callback: Optional[Callable] = None) -> bool:
        """Submit a job for processing
        
        Args:
            job_id: Job ID
            task_type: Type of task
            payload: Task data
            callback: Optional callback when done
            
        Returns:
            True if job submitted, False if queue full
        """
        if not self.running:
            self.logger.error("Job queue is not running")
            return False
        
        if self.task_queue.qsize() >= self.max_queue_size:
            self.logger.error(f"Job queue full (max {self.max_queue_size})")
            return False
        
        task = JobTask(job_id, task_type, payload, callback)
        
        try:
            self.task_queue.put(task, block=False)
            self.logger.info(f"Job submitted: {job_id} (type: {task_type})")
            return True
        except queue.Full:
            self.logger.error(f"Failed to submit job {job_id}: queue full")
            return False
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.task_queue.qsize()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                'queue_size': self.task_queue.qsize(),
                'workers': self.num_workers,
                'running': self.running,
                'processed': self.processed_count,
                'failed': self.failed_count,
                'total': self.processed_count + self.failed_count
            }
    
    def _worker_loop(self):
        """Worker thread main loop"""
        worker_name = threading.current_thread().name
        self.logger.info(f"{worker_name} started")
        
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                
                # None is stop signal
                if task is None:
                    break
                
                self._process_task(task)
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"{worker_name} error: {str(e)}")
                self.task_queue.task_done()
        
        self.logger.info(f"{worker_name} stopped")
    
    def _process_task(self, task: JobTask):
        """Process a single task
        
        Args:
            task: JobTask instance
        """
        task_type = task.task_type
        
        if task_type not in self.job_handlers:
            self.logger.error(f"No handler for task type: {task_type}")
            with self.lock:
                self.failed_count += 1
            return
        
        try:
            self.logger.info(f"Processing task: {task}")
            handler = self.job_handlers[task_type]
            result = handler(task)
            
            # Execute callback if provided
            if task.callback:
                task.callback(task.job_id, result)
            
            with self.lock:
                self.processed_count += 1
            
            self.logger.info(f"Task completed: {task.job_id}")
            
        except Exception as e:
            self.logger.error(f"Task failed {task.job_id}: {str(e)}", exc_info=True)
            with self.lock:
                self.failed_count += 1
    
    def wait_completion(self, timeout: Optional[int] = None) -> bool:
        """Wait for all tasks to complete
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            True if all tasks completed, False if timeout
        """
        try:
            self.task_queue.join()
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for completion: {str(e)}")
            return False


# Global job queue instance
_async_queue: Optional[AsyncJobQueue] = None


def get_async_queue() -> AsyncJobQueue:
    """Get or create global async queue"""
    global _async_queue
    if _async_queue is None:
        _async_queue = AsyncJobQueue(num_workers=4)
    return _async_queue


def initialize_async_queue(num_workers: int = 4, logger: Optional[logging.Logger] = None):
    """Initialize the global async queue
    
    Args:
        num_workers: Number of worker threads
        logger: Logger instance
    """
    global _async_queue
    _async_queue = AsyncJobQueue(num_workers=num_workers, logger=logger)
    return _async_queue
