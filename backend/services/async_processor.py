"""
Async processing module for large-scale data operations
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import time
import os

from backend.services.async_queue import AsyncJobQueue, JobTask
from backend.services.data_storage import DataStorage
from utils.helpers import get_timestamp, generate_uuid


class AsyncProcessor:
    """High-level async processor for data operations"""
    
    def __init__(self, job_queue: AsyncJobQueue, data_storage: DataStorage,
                 logger: Optional[logging.Logger] = None):
        """Initialize async processor
        
        Args:
            job_queue: AsyncJobQueue instance
            data_storage: DataStorage instance
            logger: Logger instance
        """
        self.job_queue = job_queue
        self.storage = data_storage
        self.logger = logger or logging.getLogger(__name__)
        self.active_jobs = {}  # Track active jobs
        
        # Register handlers with the job queue
        self.job_queue.register_handler('process_file', self._handle_process_file)
        self.job_queue.register_handler('validate_file', self._handle_validate_file)
    
    def process_file_async(self, job_id: str, file_path: str, 
                          config: Dict[str, Any]) -> bool:
        """Submit file processing job asynchronously
        
        Args:
            job_id: Job ID
            file_path: Path to file
            config: Processing configuration
            
        Returns:
            True if job submitted successfully
        """
        payload = {
            'job_id': job_id,
            'file_path': file_path,
            'config': config,
            'started_at': get_timestamp()
        }
        
        success = self.job_queue.submit_job(
            job_id,
            'process_file',
            payload,
            callback=self._job_completion_callback
        )
        
        if success:
            self.active_jobs[job_id] = {
                'status': 'queued',
                'submitted_at': get_timestamp(),
                'file_path': file_path,
                'config': config,
                'job_type': 'process_file'
            }
        
        return success
    
    def validate_file_async(self, job_id: str, file_path: str,
                           rules: Optional[Dict[str, str]] = None) -> bool:
        """Submit validation job asynchronously
        
        Args:
            job_id: Job ID
            file_path: Path to file
            rules: Validation rules
            
        Returns:
            True if job submitted successfully
        """
        payload = {
            'job_id': job_id,
            'file_path': file_path,
            'rules': rules or {},
            'started_at': get_timestamp()
        }
        
        success = self.job_queue.submit_job(
            job_id,
            'validate_file',
            payload,
            callback=self._job_completion_callback
        )
        
        if success:
            self.active_jobs[job_id] = {
                'status': 'queued',
                'submitted_at': get_timestamp(),
                'file_path': file_path
            }
        
        return success
    
    def analytics_async(self, job_id: str, file_path: str) -> bool:
        """Submit analytics job asynchronously
        
        Args:
            job_id: Job ID
            file_path: Path to file
            
        Returns:
            True if job submitted successfully
        """
        payload = {
            'job_id': job_id,
            'file_path': file_path,
            'started_at': get_timestamp()
        }
        
        success = self.job_queue.submit_job(
            job_id,
            'analytics',
            payload,
            callback=self._job_completion_callback
        )
        
        if success:
            self.active_jobs[job_id] = {
                'status': 'queued',
                'submitted_at': get_timestamp(),
                'file_path': file_path
            }
        
        return success
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a job
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dictionary
        """
        status_dict = {
            'job_id': job_id,
            'found': False,
            'status': None,
            'submitted_at': None,
            'file_path': None
        }
        
        if job_id in self.active_jobs:
            status_dict['found'] = True
            status_dict.update(self.active_jobs[job_id])
        
        return status_dict
    
    def _job_completion_callback(self, job_id: str, result: Any):
        """Callback when job completes
        
        Args:
            job_id: Job ID
            result: Job result
        """
        if job_id not in self.active_jobs:
            self.logger.info(f"Job completed (not tracked in active_jobs): {job_id}")
            return

        # Handle failed jobs explicitly so UI can surface the error.
        if isinstance(result, dict) and not result.get('success', True):
            self.active_jobs[job_id]['status'] = 'failed'
            self.active_jobs[job_id]['error'] = result.get('error', 'Unknown error')
            self.active_jobs[job_id]['completed_at'] = get_timestamp()
            self.logger.error(f"Job failed: {job_id} - {self.active_jobs[job_id]['error']}")
            return

        self.active_jobs[job_id]['status'] = 'completed'
        self.active_jobs[job_id]['completed_at'] = get_timestamp()
        self.active_jobs[job_id]['progress'] = 100

        # Persist processed output for downstream results/download endpoints.
        if isinstance(result, dict) and isinstance(result.get('dataframe'), pd.DataFrame):
            df = result['dataframe']
            csv_path = os.path.abspath(os.path.join(self.storage.results_dir, f"{job_id}_results.csv"))
            json_path = os.path.abspath(os.path.join(self.storage.results_dir, f"{job_id}_results.json"))

            df.to_csv(csv_path, index=False)
            df.to_json(json_path, orient='records', indent=2)

            self.active_jobs[job_id]['result_file_path'] = csv_path
            self.active_jobs[job_id]['result_json_path'] = json_path
            self.active_jobs[job_id]['output_rows'] = int(len(df))

        result_for_storage = result
        if isinstance(result, dict) and 'dataframe' in result:
            result_for_storage = {k: v for k, v in result.items() if k != 'dataframe'}

        self.storage.save_results(job_id, result_for_storage if isinstance(result_for_storage, dict) else {'result': result_for_storage}, 'processing')

        self.logger.info(f"Job completed: {job_id}")
    
    def process_large_dataframe(self, df: pd.DataFrame, config: Dict[str, Any],
                               job_id: str, chunk_size: int = 10000) -> Dict[str, Any]:
        """Process large DataFrame in chunks
        
        Args:
            df: Pandas DataFrame
            config: Processing configuration
            job_id: Job ID for logging
            chunk_size: Size of chunks for processing
            
        Returns:
            Processing result dictionary
        """
        self.logger.info(f"Starting chunked processing: {job_id} ({len(df)} rows)")
        
        start_time = time.time()
        total_rows = len(df)
        processed_rows = 0
        results = []
        metadata = {
            'job_id': job_id,
            'total_rows': total_rows,
            'chunk_size': chunk_size,
            'chunks_processed': 0,
            'started_at': get_timestamp(),
            'processing_steps': []
        }
        
        try:
            # Apply filters
            if 'filters' in config:
                self.logger.info(f"{job_id}: Applying filters")
                df = self._apply_filters_chunked(df, config['filters'], job_id, metadata)
                metadata['processing_steps'].append('filters')
            
            # Apply transformations
            if 'transformations' in config:
                self.logger.info(f"{job_id}: Applying transformations")
                df = self._apply_transformations_chunked(df, config['transformations'], 
                                                         job_id, metadata)
                metadata['processing_steps'].append('transformations')
            
            # Apply sorting
            if 'sorting' in config:
                self.logger.info(f"{job_id}: Applying sorting")
                df = self._apply_sorting_chunked(df, config['sorting'], job_id, metadata)
                metadata['processing_steps'].append('sorting')
            
            processed_rows = len(df)
            elapsed = time.time() - start_time
            
            result = {
                'success': True,
                'output_rows': processed_rows,
                'input_rows': total_rows,
                'rows_removed': total_rows - processed_rows,
                'elapsed_seconds': round(elapsed, 2),
                'rows_per_second': round(total_rows / elapsed, 2) if elapsed > 0 else 0,
                'metadata': metadata,
                'dataframe': df
            }
            
            self.logger.info(f"{job_id}: Processing complete ({processed_rows} rows in {elapsed:.2f}s)")
            return result
        
        except Exception as e:
            self.logger.error(f"{job_id}: Processing failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'metadata': metadata
            }
    
    def _apply_filters_chunked(self, df: pd.DataFrame, filters: Dict[str, Any],
                               job_id: str, metadata: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters with logging
        
        Args:
            df: DataFrame
            filters: Filter rules
            job_id: Job ID
            metadata: Metadata dict to update
            
        Returns:
            Filtered DataFrame
        """
        initial_rows = len(df)
        
        for column, condition in filters.items():
            if column not in df.columns:
                self.logger.warning(f"{job_id}: Column '{column}' not found")
                continue
            
            if isinstance(condition, dict):
                for operator, value in condition.items():
                    if operator == '$gt':
                        df = df[df[column] > value]
                    elif operator == '$gte':
                        df = df[df[column] >= value]
                    elif operator == '$lt':
                        df = df[df[column] < value]
                    elif operator == '$lte':
                        df = df[df[column] <= value]
                    elif operator == '$eq':
                        df = df[df[column] == value]
                    elif operator == '$ne':
                        df = df[df[column] != value]
                    elif operator == '$in':
                        df = df[df[column].isin(value)]
                    
                    removed = initial_rows - len(df)
                    if removed > 0:
                        self.logger.debug(f"{job_id}: Filter {column}{operator} removed {removed} rows")
            else:
                df = df[df[column] == condition]
        
        metadata['filter_stats'] = {
            'initial_rows': initial_rows,
            'final_rows': len(df),
            'rows_removed': initial_rows - len(df)
        }
        
        return df
    
    def _apply_transformations_chunked(self, df: pd.DataFrame, 
                                       transformations: List[Dict[str, Any]],
                                       job_id: str, metadata: Dict[str, Any]) -> pd.DataFrame:
        """Apply transformations with logging
        
        Args:
            df: DataFrame
            transformations: List of transformation configs
            job_id: Job ID
            metadata: Metadata dict to update
            
        Returns:
            Transformed DataFrame
        """
        transform_log = []
        
        for transform in transformations:
            transform_type = transform.get('type', '').lower()
            
            if transform_type == 'normalize':
                columns = transform.get('columns', [])
                df = self._normalize_columns(df, columns)
                self.logger.debug(f"{job_id}: Normalized {len(columns)} columns")
                transform_log.append({'type': 'normalize', 'columns': len(columns)})
            
            elif transform_type == 'drop_columns':
                columns = [c for c in transform.get('columns', []) if c in df.columns]
                df = df.drop(columns=columns)
                self.logger.debug(f"{job_id}: Dropped {len(columns)} columns")
                transform_log.append({'type': 'drop_columns', 'count': len(columns)})
            
            elif transform_type == 'rename':
                mapping = transform.get('mapping', {})
                df = df.rename(columns=mapping)
                self.logger.debug(f"{job_id}: Renamed {len(mapping)} columns")
                transform_log.append({'type': 'rename', 'count': len(mapping)})
        
        metadata['transformations_applied'] = transform_log
        return df
    
    def _apply_sorting_chunked(self, df: pd.DataFrame, sorting: Dict[str, str],
                               job_id: str, metadata: Dict[str, Any]) -> pd.DataFrame:
        """Apply sorting with logging
        
        Args:
            df: DataFrame
            sorting: Sorting configuration
            job_id: Job ID
            metadata: Metadata dict to update
            
        Returns:
            Sorted DataFrame
        """
        columns = [c for c in sorting.keys() if c in df.columns]
        ascending = [sorting[col].lower() != 'desc' for col in columns]
        
        df = df.sort_values(by=columns, ascending=ascending)
        self.logger.debug(f"{job_id}: Sorted by {len(columns)} columns")
        metadata['sorting_columns'] = columns
        
        return df
    
    def _normalize_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize numeric columns"""
        for column in columns:
            if column in df.columns and df[column].dtype in ['int32', 'int64', 'float32', 'float64']:
                min_val = df[column].min()
                max_val = df[column].max()
                if max_val - min_val != 0:
                    df[column] = (df[column] - min_val) / (max_val - min_val)
        return df
    
    def _handle_process_file(self, task) -> Dict[str, Any]:
        """Handler for process_file tasks
        
        Args:
            task: JobTask instance
            
        Returns:
            Result dictionary
        """
        job_id = task.payload.get('job_id')
        file_path = task.payload.get('file_path')
        config = task.payload.get('config', {})
        
        self.logger.info(f"Processing file: {job_id} ({file_path})")
        
        try:
            # Load file
            df = pd.read_csv(file_path)
            
            # Process using large dataframe handler
            result = self.process_large_dataframe(df, config, job_id)
            
            # Update job status
            if result.get('success'):
                if job_id in self.active_jobs:
                    self.active_jobs[job_id]['status'] = 'processing'
                    self.active_jobs[job_id]['progress'] = 100
                
                self.logger.info(f"File processing completed: {job_id}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"File processing failed: {job_id}: {str(e)}", exc_info=True)
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'failed'
                self.active_jobs[job_id]['error'] = str(e)
            
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def _handle_validate_file(self, task) -> Dict[str, Any]:
        """Handler for validate_file tasks
        
        Args:
            task: JobTask instance
            
        Returns:
            Result dictionary
        """
        job_id = task.payload.get('job_id')
        file_path = task.payload.get('file_path')
        rules = task.payload.get('rules', {})
        
        self.logger.info(f"Validating file: {job_id} ({file_path})")
        
        try:
            # Load file
            df = pd.read_csv(file_path)
            
            # Basic validation
            validation_result = {
                'success': True,
                'total_rows': len(df),
                'valid_rows': len(df),
                'invalid_rows': 0,
                'columns': list(df.columns),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'issues': []
            }
            
            # Update job status
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'completed'
                self.active_jobs[job_id]['progress'] = 100
            
            self.logger.info(f"File validation completed: {job_id}")
            
            return validation_result
        
        except Exception as e:
            self.logger.error(f"File validation failed: {job_id}: {str(e)}", exc_info=True)
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'failed'
                self.active_jobs[job_id]['error'] = str(e)
            
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'active_jobs': len(self.active_jobs),
            'queue_stats': self.job_queue.get_stats(),
            'storage_stats': self.storage.get_storage_stats(),
            'timestamp': get_timestamp()
        }
