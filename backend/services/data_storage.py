"""
Data storage layer for persistent result management
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from utils.helpers import ensure_directory, get_timestamp


class DataStorage:
    """Manages persistent storage of processing results and metadata"""
    
    def __init__(self, storage_dir: str, logger: Optional[logging.Logger] = None):
        """Initialize data storage
        
        Args:
            storage_dir: Base directory for storage
            logger: Logger instance
        """
        self.storage_dir = storage_dir
        self.logger = logger or logging.getLogger(__name__)
        
        # Create subdirectories
        self.jobs_dir = os.path.join(storage_dir, 'jobs')
        self.results_dir = os.path.join(storage_dir, 'results')
        self.datasets_dir = os.path.join(storage_dir, 'datasets')
        self.analytics_dir = os.path.join(storage_dir, 'analytics')
        self.metadata_dir = os.path.join(storage_dir, 'metadata')
        
        for directory in [self.jobs_dir, self.results_dir, self.datasets_dir, 
                         self.analytics_dir, self.metadata_dir]:
            ensure_directory(directory)
        
        self.logger.info(f"Data storage initialized at {storage_dir}")
    
    # Job Storage Methods
    
    def save_job(self, job_id: str, job_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Save job metadata
        
        Args:
            job_id: Job ID
            job_data: Job data dictionary
            
        Returns:
            Tuple of (success, message)
        """
        try:
            job_file = os.path.join(self.jobs_dir, f"{job_id}.json")
            
            # Add storage metadata
            storage_data = {
                'job_id': job_id,
                'data': job_data,
                'stored_at': get_timestamp(),
                'version': '1.0'
            }
            
            with open(job_file, 'w') as f:
                json.dump(storage_data, f, indent=2, default=str)
            
            self.logger.info(f"Job saved: {job_id}")
            return True, f"Job {job_id} saved successfully"
        
        except Exception as e:
            error_msg = f"Error saving job {job_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_job(self, job_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Load job metadata
        
        Args:
            job_id: Job ID
            
        Returns:
            Tuple of (success, data, message)
        """
        try:
            job_file = os.path.join(self.jobs_dir, f"{job_id}.json")
            
            if not os.path.exists(job_file):
                msg = f"Job {job_id} not found"
                self.logger.warning(msg)
                return False, None, msg
            
            with open(job_file, 'r') as f:
                storage_data = json.load(f)
            
            return True, storage_data.get('data'), "Job loaded successfully"
        
        except Exception as e:
            error_msg = f"Error loading job {job_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    def list_jobs(self) -> List[str]:
        """List all stored job IDs
        
        Returns:
            List of job IDs
        """
        try:
            jobs = []
            for filename in os.listdir(self.jobs_dir):
                if filename.endswith('.json'):
                    job_id = filename[:-5]  # Remove .json
                    jobs.append(job_id)
            return sorted(jobs)
        except Exception as e:
            self.logger.error(f"Error listing jobs: {str(e)}")
            return []
    
    # Results Storage Methods
    
    def save_results(self, job_id: str, results_data: Dict[str, Any], 
                    result_type: str = 'processing') -> Tuple[bool, str]:
        """Save processing results
        
        Args:
            job_id: Job ID
            results_data: Results dictionary
            result_type: Type of result (processing, validation, analytics)
            
        Returns:
            Tuple of (success, file_path)
        """
        try:
            result_file = os.path.join(self.results_dir, f"{job_id}_{result_type}.json")
            
            # Add result metadata
            result_storage = {
                'job_id': job_id,
                'result_type': result_type,
                'data': results_data,
                'saved_at': get_timestamp(),
                'version': '1.0'
            }
            
            with open(result_file, 'w') as f:
                json.dump(result_storage, f, indent=2, default=str)
            
            self.logger.info(f"Results saved: {job_id} ({result_type})")
            return True, result_file
        
        except Exception as e:
            error_msg = f"Error saving results for {job_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_results(self, job_id: str, result_type: str = 'processing') -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Load processing results
        
        Args:
            job_id: Job ID
            result_type: Type of result
            
        Returns:
            Tuple of (success, data, message)
        """
        try:
            result_file = os.path.join(self.results_dir, f"{job_id}_{result_type}.json")
            
            if not os.path.exists(result_file):
                msg = f"Results for {job_id} not found"
                return False, None, msg
            
            with open(result_file, 'r') as f:
                result_storage = json.load(f)
            
            return True, result_storage.get('data'), "Results loaded successfully"
        
        except Exception as e:
            error_msg = f"Error loading results for {job_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    # Dataset Storage Methods
    
    def save_dataset_metadata(self, dataset_id: str, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """Save dataset metadata
        
        Args:
            dataset_id: Dataset ID
            metadata: Dataset metadata
            
        Returns:
            Tuple of (success, message)
        """
        try:
            dataset_file = os.path.join(self.datasets_dir, f"{dataset_id}.json")
            
            storage_data = {
                'dataset_id': dataset_id,
                'metadata': metadata,
                'created_at': get_timestamp(),
                'version': '1.0'
            }
            
            with open(dataset_file, 'w') as f:
                json.dump(storage_data, f, indent=2, default=str)
            
            self.logger.info(f"Dataset metadata saved: {dataset_id}")
            return True, f"Dataset {dataset_id} metadata saved"
        
        except Exception as e:
            error_msg = f"Error saving dataset metadata: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_dataset_metadata(self, dataset_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Load dataset metadata
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Tuple of (success, metadata, message)
        """
        try:
            dataset_file = os.path.join(self.datasets_dir, f"{dataset_id}.json")
            
            if not os.path.exists(dataset_file):
                msg = f"Dataset {dataset_id} not found"
                return False, None, msg
            
            with open(dataset_file, 'r') as f:
                storage_data = json.load(f)
            
            return True, storage_data.get('metadata'), "Dataset metadata loaded"
        
        except Exception as e:
            error_msg = f"Error loading dataset metadata: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    # Analytics Storage Methods
    
    def save_analytics(self, job_id: str, analytics_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Save analytics results
        
        Args:
            job_id: Job ID
            analytics_data: Analytics dictionary
            
        Returns:
            Tuple of (success, file_path)
        """
        try:
            analytics_file = os.path.join(self.analytics_dir, f"{job_id}_analytics.json")
            
            storage_data = {
                'job_id': job_id,
                'analytics': analytics_data,
                'saved_at': get_timestamp(),
                'version': '1.0'
            }
            
            with open(analytics_file, 'w') as f:
                json.dump(storage_data, f, indent=2, default=str)
            
            self.logger.info(f"Analytics saved: {job_id}")
            return True, analytics_file
        
        except Exception as e:
            error_msg = f"Error saving analytics: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_analytics(self, job_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Load analytics results
        
        Args:
            job_id: Job ID
            
        Returns:
            Tuple of (success, analytics_data, message)
        """
        try:
            analytics_file = os.path.join(self.analytics_dir, f"{job_id}_analytics.json")
            
            if not os.path.exists(analytics_file):
                msg = f"Analytics for {job_id} not found"
                return False, None, msg
            
            with open(analytics_file, 'r') as f:
                storage_data = json.load(f)
            
            return True, storage_data.get('analytics'), "Analytics loaded"
        
        except Exception as e:
            error_msg = f"Error loading analytics: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    # Index/Metadata Methods
    
    def save_index(self, index_name: str, index_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Save an index file for quick lookups
        
        Args:
            index_name: Name of index
            index_data: Index data
            
        Returns:
            Tuple of (success, message)
        """
        try:
            index_file = os.path.join(self.metadata_dir, f"{index_name}_index.json")
            
            index_storage = {
                'index_name': index_name,
                'entries': index_data,
                'created_at': get_timestamp(),
                'count': len(index_data),
                'version': '1.0'
            }
            
            with open(index_file, 'w') as f:
                json.dump(index_storage, f, indent=2, default=str)
            
            self.logger.info(f"Index saved: {index_name} ({len(index_data)} entries)")
            return True, f"Index {index_name} saved"
        
        except Exception as e:
            error_msg = f"Error saving index: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_index(self, index_name: str) -> Tuple[bool, Optional[List[Dict[str, Any]]], str]:
        """Load an index
        
        Args:
            index_name: Name of index
            
        Returns:
            Tuple of (success, index_data, message)
        """
        try:
            index_file = os.path.join(self.metadata_dir, f"{index_name}_index.json")
            
            if not os.path.exists(index_file):
                msg = f"Index {index_name} not found"
                return False, None, msg
            
            with open(index_file, 'r') as f:
                index_storage = json.load(f)
            
            return True, index_storage.get('entries', []), "Index loaded"
        
        except Exception as e:
            error_msg = f"Error loading index: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg
    
    # Storage Statistics
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        stats = {
            'total_jobs': len(os.listdir(self.jobs_dir)) if os.path.exists(self.jobs_dir) else 0,
            'total_results': len(os.listdir(self.results_dir)) if os.path.exists(self.results_dir) else 0,
            'total_datasets': len(os.listdir(self.datasets_dir)) if os.path.exists(self.datasets_dir) else 0,
            'total_analytics': len(os.listdir(self.analytics_dir)) if os.path.exists(self.analytics_dir) else 0,
            'storage_path': self.storage_dir,
            'timestamp': get_timestamp()
        }
        
        # Calculate directory sizes
        for name, path in [('jobs', self.jobs_dir), ('results', self.results_dir), 
                          ('datasets', self.datasets_dir), ('analytics', self.analytics_dir)]:
            try:
                total_size = sum(
                    os.path.getsize(os.path.join(path, f)) 
                    for f in os.listdir(path) 
                    if os.path.isfile(os.path.join(path, f))
                )
                stats[f'{name}_size_bytes'] = total_size
            except:
                stats[f'{name}_size_bytes'] = 0
        
        return stats
    
    def cleanup_old_entries(self, days: int = 30) -> Tuple[int, int]:
        """Clean up old storage entries
        
        Args:
            days: Delete entries older than this many days
            
        Returns:
            Tuple of (deleted_files, deleted_bytes)
        """
        from datetime import timedelta
        
        deleted_count = 0
        deleted_bytes = 0
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for directory in [self.jobs_dir, self.results_dir, self.datasets_dir, self.analytics_dir]:
            try:
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff_time:
                            file_size = os.path.getsize(filepath)
                            os.remove(filepath)
                            deleted_count += 1
                            deleted_bytes += file_size
                            self.logger.info(f"Cleaned up: {filename}")
            except Exception as e:
                self.logger.error(f"Error during cleanup: {str(e)}")
        
        self.logger.info(f"Cleanup completed: {deleted_count} files, {deleted_bytes} bytes")
        return deleted_count, deleted_bytes
