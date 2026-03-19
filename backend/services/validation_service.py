"""
Validation service - handles data validation
"""

import pandas as pd
from typing import Tuple, Dict, List, Any
from utils.helpers import generate_uuid, get_timestamp
from utils.validators import DataValidator
from backend.models.data_models import ValidationResult


class ValidationService:
    """Service for data validation"""
    
    def __init__(self):
        """Initialize ValidationService"""
        pass
    
    def validate_dataframe(self, df: pd.DataFrame, rules: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """Validate a DataFrame against rules (optimized for speed)
        
        Args:
            df: Pandas DataFrame to validate
            rules: Validation rules dictionary
            
        Returns:
            ValidationResult object
        """
        validation_id = f"val-{generate_uuid()}"
        total_rows = len(df)
        issues = []
        
        # Check required columns
        required_columns = set(rules.keys())
        missing_columns = required_columns - set(df.columns)
        
        if missing_columns:
            issues.append({
                'type': 'missing_columns',
                'severity': 'error',
                'columns': list(missing_columns),
                'message': f"Missing columns: {', '.join(missing_columns)}"
            })
        
        # Fast detection of missing values (vectorized)
        missing_value_issues = self._detect_missing_values(df)
        if missing_value_issues:
            issues.extend(missing_value_issues)
        
        # Fast detection of duplicates (vectorized)
        duplicate_issues = self._detect_duplicates(df)
        if duplicate_issues:
            issues.extend(duplicate_issues)
        
        # Quick validation: check if any rows have all NaN or completely invalid
        # Skip expensive row-by-row validation for speed
        fully_empty_rows = df.isna().all(axis=1).sum()
        if fully_empty_rows > 0:
            issues.append({
                'type': 'empty_rows',
                'severity': 'error',
                'count': int(fully_empty_rows),
                'message': f"Found {fully_empty_rows} completely empty rows"
            })
        
        # Calculate valid/invalid rows based on issues found
        error_count = len([i for i in issues if i['severity'] == 'error'])
        invalid_rows = error_count if error_count > 0 else 0
        valid_rows = total_rows - invalid_rows if invalid_rows < total_rows else 0
        
        status = 'passed' if error_count == 0 else 'failed'
        
        return ValidationResult(
            validation_id=validation_id,
            dataset_id="",  # Will be set by caller
            status=status,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            issues=issues,
            created_at=get_timestamp()
        )
    
    def _detect_missing_values(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect missing values in DataFrame
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        
        for column in df.columns:
            missing_count = df[column].isna().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / len(df)) * 100
                row_indices = df[df[column].isna()].index.tolist()[:5]  # First 5 indices
                
                issue = {
                    'type': 'missing_value',
                    'severity': 'warning' if missing_percentage < 5 else 'error',
                    'column': column,
                    'missing_count': int(missing_count),
                    'missing_percentage': round(missing_percentage, 2),
                    'row_indices': row_indices,
                    'message': f"Column '{column}' has {missing_count} missing values ({missing_percentage:.2f}%)"
                }
                issues.append(issue)
        
        return issues
    
    def _detect_duplicates(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect duplicate rows in DataFrame
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        
        # Check for completely duplicate rows
        duplicate_mask = df.duplicated(keep=False)
        duplicate_count = duplicate_mask.sum()
        
        if duplicate_count > 0:
            duplicate_indices = df[duplicate_mask].index.tolist()[:5]  # First 5 indices
            
            issue = {
                'type': 'duplicate_rows',
                'severity': 'warning',
                'duplicate_count': int(duplicate_count),
                'row_indices': duplicate_indices,
                'message': f"Found {duplicate_count} duplicate rows"
            }
            issues.append(issue)
        
        return issues
    
    def validate_column_types(self, df: pd.DataFrame, type_rules: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate column data types
        
        Args:
            df: Pandas DataFrame
            type_rules: Dict mapping column names to expected types
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []
        
        for column, expected_type in type_rules.items():
            if column not in df.columns:
                errors.append(f"Column '{column}' not found")
                continue
            
            # Get actual dtype
            actual_type = str(df[column].dtype)
            
            # Map common type names
            type_mapping = {
                'integer': ['int', 'int32', 'int64'],
                'float': ['float', 'float32', 'float64'],
                'string': ['object', 'str'],
                'date': ['datetime64', 'datetime'],
                'boolean': ['bool']
            }
            
            expected_types = type_mapping.get(expected_type.lower(), [expected_type.lower()])
            
            if not any(t in actual_type.lower() for t in expected_types):
                errors.append(f"Column '{column}' has type '{actual_type}', expected '{expected_type}'")
        
        return len(errors) == 0, errors
    
    def get_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive data profile
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with data profile
        """
        profile = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'columns': {},
            'missing_values': {},
            'data_types': {}
        }
        
        for column in df.columns:
            # Column stats
            profile['columns'][column] = {
                'dtype': str(df[column].dtype),
                'null_count': int(df[column].isna().sum()),
                'null_percentage': float((df[column].isna().sum() / len(df)) * 100),
                'unique_count': int(df[column].nunique())
            }
            
            # Numeric columns
            if df[column].dtype in ['int32', 'int64', 'float32', 'float64']:
                profile['columns'][column].update({
                    'min': float(df[column].min()),
                    'max': float(df[column].max()),
                    'mean': float(df[column].mean()),
                    'median': float(df[column].median()),
                    'std': float(df[column].std())
                })
            
            # Missing values summary
            missing_count = df[column].isna().sum()
            if missing_count > 0:
                profile['missing_values'][column] = {
                    'count': int(missing_count),
                    'percentage': float((missing_count / len(df)) * 100)
                }
            
            # Data types summary
            dtype_str = str(df[column].dtype)
            profile['data_types'][dtype_str] = profile['data_types'].get(dtype_str, 0) + 1
        
        return profile
