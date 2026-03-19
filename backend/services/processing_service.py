"""
Processing service - handles data processing jobs
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from utils.helpers import generate_uuid, get_timestamp, save_json_file, ensure_directory
from backend.models.data_models import ProcessingJob, ProcessingResult, JobStatus


class ProcessingService:
    """Service for managing data processing jobs"""
    
    def __init__(self, results_folder: str):
        """Initialize ProcessingService
        
        Args:
            results_folder: Directory to store results
        """
        self.results_folder = results_folder
        ensure_directory(results_folder)
        self.jobs = {}  # In-memory job registry
    
    def create_job(self, dataset_id: str, config: Dict[str, Any]) -> ProcessingJob:
        """Create a new processing job
        
        Args:
            dataset_id: ID of dataset to process
            config: Processing configuration
            
        Returns:
            ProcessingJob object
        """
        job_id = f"job-{generate_uuid()}"
        
        job = ProcessingJob(
            job_id=job_id,
            dataset_id=dataset_id,
            status=JobStatus.QUEUED.value,
            created_at=get_timestamp(),
            config=config
        )
        
        self.jobs[job_id] = job
        return job
    
    def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """Update job status and additional fields
        
        Args:
            job_id: Job ID
            status: New status
            **kwargs: Additional fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.status = status
        
        if 'progress_percentage' in kwargs:
            job.progress_percentage = kwargs['progress_percentage']
        if 'processed_rows' in kwargs:
            job.processed_rows = kwargs['processed_rows']
        if 'output_rows' in kwargs:
            job.output_rows = kwargs['output_rows']
        if 'started_at' in kwargs:
            job.started_at = kwargs['started_at']
        if 'completed_at' in kwargs:
            job.completed_at = kwargs['completed_at']
        if 'error_message' in kwargs:
            job.error_message = kwargs['error_message']
        if 'result_file_path' in kwargs:
            job.result_file_path = kwargs['result_file_path']
        
        return True
    
    def get_job(self, job_id: str) -> Tuple[bool, Optional[ProcessingJob], str]:
        """Get job by ID
        
        Args:
            job_id: Job ID
            
        Returns:
            Tuple of (success: bool, job: ProcessingJob or None, message: str)
        """
        if job_id not in self.jobs:
            return False, None, f"Job {job_id} not found"
        
        return True, self.jobs[job_id], "Job found"
    
    def process_dataframe(self, df: pd.DataFrame, config: Dict[str, Any], job_id: str) -> Tuple[bool, pd.DataFrame, str]:
        """Process DataFrame according to configuration
        
        Args:
            df: Pandas DataFrame to process
            config: Processing configuration
            job_id: Job ID for tracking
            
        Returns:
            Tuple of (success: bool, processed_df: pd.DataFrame, message: str)
        """
        try:
            original_rows = len(df)
            
            # Update job status
            self.update_job_status(job_id, JobStatus.PROCESSING.value, started_at=get_timestamp())
            
            # Apply filters
            if 'filters' in config:
                df = self._apply_filters(df, config['filters'])
                self.update_job_status(job_id, JobStatus.PROCESSING.value, progress_percentage=25)
            
            # Apply transformations
            if 'transformations' in config:
                df = self._apply_transformations(df, config['transformations'])
                self.update_job_status(job_id, JobStatus.PROCESSING.value, progress_percentage=50)
            
            # Apply sorting
            if 'sorting' in config:
                df = self._apply_sorting(df, config['sorting'])
            
            # Update job metrics
            self.update_job_status(
                job_id,
                JobStatus.PROCESSING.value,
                input_rows=original_rows,
                processed_rows=len(df),
                output_rows=len(df),
                progress_percentage=75
            )
            
            return True, df, f"Processing successful: {original_rows} → {len(df)} rows"
        
        except Exception as e:
            error_msg = str(e)
            self.update_job_status(job_id, JobStatus.FAILED.value, error_message=error_msg)
            return False, df, f"Processing error: {error_msg}"
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame
        
        Args:
            df: Pandas DataFrame
            filters: Filter configuration
            
        Returns:
            Filtered DataFrame
        """
        for column, condition in filters.items():
            if column not in df.columns:
                continue
            
            if isinstance(condition, dict):
                # Handle comparison operators
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
            else:
                df = df[df[column] == condition]
        
        return df
    
    def _apply_transformations(self, df: pd.DataFrame, transformations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply transformations to DataFrame
        
        Args:
            df: Pandas DataFrame
            transformations: List of transformation configs
            
        Returns:
            Transformed DataFrame
        """
        for transform in transformations:
            transform_type = transform.get('type', '').lower()
            
            if transform_type == 'normalize':
                df = self._normalize_columns(df, transform.get('columns', []))
            
            elif transform_type == 'aggregate':
                df = self._aggregate_data(df, transform)
            
            elif transform_type == 'drop_columns':
                columns_to_drop = [col for col in transform.get('columns', []) if col in df.columns]
                df = df.drop(columns=columns_to_drop)
            
            elif transform_type == 'rename':
                rename_dict = transform.get('mapping', {})
                df = df.rename(columns=rename_dict)
        
        return df
    
    def _normalize_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize numeric columns
        
        Args:
            df: Pandas DataFrame
            columns: Column names to normalize
            
        Returns:
            DataFrame with normalized columns
        """
        for column in columns:
            if column in df.columns and df[column].dtype in ['int32', 'int64', 'float32', 'float64']:
                min_val = df[column].min()
                max_val = df[column].max()
                if max_val - min_val != 0:
                    df[column] = (df[column] - min_val) / (max_val - min_val)
        
        return df
    
    def _aggregate_data(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate data
        
        Args:
            df: Pandas DataFrame
            transform: Aggregation configuration
            
        Returns:
            Aggregated DataFrame
        """
        group_by = transform.get('group_by', [])
        aggregations = transform.get('aggregations', {})
        
        if group_by:
            return df.groupby(group_by, as_index=False).agg(aggregations)
        
        return df
    
    def _apply_sorting(self, df: pd.DataFrame, sorting: Dict[str, str]) -> pd.DataFrame:
        """Apply sorting to DataFrame
        
        Args:
            df: Pandas DataFrame
            sorting: Column and direction mapping
            
        Returns:
            Sorted DataFrame
        """
        columns = list(sorting.keys())
        ascending = [sorting[col].lower() != 'desc' for col in columns]
        
        return df.sort_values(by=columns, ascending=ascending)
    
    def save_results(self, job_id: str, result_data: pd.DataFrame, data_format: str = 'json') -> Tuple[bool, str, str]:
        """Save processing results
        
        Args:
            job_id: Job ID
            result_data: Processed data
            data_format: Output format (json, csv)
            
        Returns:
            Tuple of (success: bool, file_path: str, message: str)
        """
        try:
            # Create results directory
            ensure_directory(self.results_folder)
            
            if data_format.lower() == 'csv':
                file_path = os.path.join(self.results_folder, f"{job_id}_results.csv")
                result_data.to_csv(file_path, index=False)
            else:  # json
                file_path = os.path.join(self.results_folder, f"{job_id}_results.json")
                result_data.to_json(file_path, orient='records', indent=2)
            
            return True, file_path, f"Results saved to {file_path}"
        
        except Exception as e:
            return False, "", f"Error saving results: {str(e)}"
    
    def get_result_preview(self, job_id: str, nrows: int = 10) -> Dict[str, Any]:
        """Get preview of results
        
        Args:
            job_id: Job ID
            nrows: Number of rows to preview
            
        Returns:
            Dictionary with result preview and statistics
        """
        success, job, message = self.get_job(job_id)
        
        if not success or job is None:
            return {'error': message}
        
        if not job.result_file_path or not os.path.exists(job.result_file_path):
            return {'error': 'Results file not found'}
        
        try:
            # Load results
            if job.result_file_path.endswith('.csv'):
                df = pd.read_csv(job.result_file_path, nrows=nrows)
            else:
                df = pd.read_json(job.result_file_path)
                df = df.head(nrows)
            
            # Get statistics
            statistics = {}
            for col in df.columns:
                if df[col].dtype in ['int32', 'int64', 'float32', 'float64']:
                    statistics[col] = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median())
                    }
            
            return {
                'preview': df.head(nrows).to_dict('records'),
                'total_rows': len(pd.read_csv(job.result_file_path)) if job.result_file_path.endswith('.csv') else len(pd.read_json(job.result_file_path)),
                'columns': list(df.columns),
                'statistics': statistics
            }
        
        except Exception as e:
            return {'error': f"Error reading results: {str(e)}"}
