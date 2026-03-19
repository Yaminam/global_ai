"""
Data models - Dataset, Job, Result, Validation, Analytics
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class JobStatus(Enum):
    """Processing job status enum"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationStatus(Enum):
    """Validation status enum"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class Column:
    """Represents a data column"""
    index: int
    name: str
    data_type: str
    nullable: bool = True
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Dataset:
    """Represents an uploaded dataset"""
    dataset_id: str
    filename: str
    file_path: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]
    mime_type: str
    created_at: str
    status: str = "uploaded"
    description: str = ""
    category: str = ""
    
    def to_dict(self):
        return {
            'dataset_id': self.dataset_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'columns': self.columns,
            'mime_type': self.mime_type,
            'created_at': self.created_at,
            'status': self.status,
            'description': self.description,
            'category': self.category,
        }


@dataclass
class ValidationResult:
    """Represents validation result"""
    validation_id: str
    dataset_id: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    issues: List[Dict[str, Any]]
    created_at: str
    
    def to_dict(self):
        return {
            'validation_id': self.validation_id,
            'dataset_id': self.dataset_id,
            'status': self.status,
            'total_rows': self.total_rows,
            'valid_rows': self.valid_rows,
            'invalid_rows': self.invalid_rows,
            'issues': self.issues,
            'created_at': self.created_at,
        }


@dataclass
class ProcessingJob:
    """Represents a data processing job"""
    job_id: str
    dataset_id: str
    status: str
    progress_percentage: int = 0
    input_rows: int = 0
    processed_rows: int = 0
    output_rows: int = 0
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: int = 0
    error_message: Optional[str] = None
    result_file_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'dataset_id': self.dataset_id,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'input_rows': self.input_rows,
            'processed_rows': self.processed_rows,
            'output_rows': self.output_rows,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'duration_ms': self.duration_ms,
            'error_message': self.error_message,
            'result_file_path': self.result_file_path,
            'config': self.config,
        }


@dataclass
class ProcessingResult:
    """Represents processing results"""
    result_id: str
    job_id: str
    dataset_id: str
    status: str
    output_rows: int
    data_preview: List[Dict[str, Any]]
    column_statistics: Dict[str, Any]
    created_at: str
    
    def to_dict(self):
        return {
            'result_id': self.result_id,
            'job_id': self.job_id,
            'dataset_id': self.dataset_id,
            'status': self.status,
            'output_rows': self.output_rows,
            'data_preview': self.data_preview,
            'column_statistics': self.column_statistics,
            'created_at': self.created_at,
        }


@dataclass
class AnalyticsResult:
    """Represents analytics results"""
    analytics_id: str
    job_id: str
    dataset_id: str
    statistical_analysis: Dict[str, Any]
    anomaly_detection: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    insights: List[str]
    created_at: str
    
    def to_dict(self):
        return {
            'analytics_id': self.analytics_id,
            'job_id': self.job_id,
            'dataset_id': self.dataset_id,
            'statistical_analysis': self.statistical_analysis,
            'anomaly_detection': self.anomaly_detection,
            'trend_analysis': self.trend_analysis,
            'insights': self.insights,
            'created_at': self.created_at,
        }
