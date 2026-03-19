"""
Data Aggregator - handles data aggregations and calculations
Provides methods for data cleaning, aggregations, and filtering
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from functools import reduce


class DataAggregator:
    """Service for data aggregation, cleaning, and transformations"""
    
    @staticmethod
    def clean_data(df: pd.DataFrame, 
                   drop_duplicates: bool = True,
                   drop_null_rows: bool = False,
                   fill_strategy: Optional[str] = None) -> pd.DataFrame:
        """Clean data by removing duplicates and handling missing values
        
        Args:
            df: Input DataFrame
            drop_duplicates: Whether to remove duplicate rows
            drop_null_rows: Whether to drop rows with any null values
            fill_strategy: Strategy for filling nulls ('mean', 'median', 'forward_fill', None)
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Remove duplicates
        if drop_duplicates:
            initial_rows = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            removed = initial_rows - len(df_clean)
            if removed > 0:
                print(f"Removed {removed} duplicate rows")
        
        # Handle missing values
        if fill_strategy and not drop_null_rows:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if df_clean[col].isnull().sum() > 0:
                    if fill_strategy == 'mean':
                        df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                    elif fill_strategy == 'median':
                        df_clean[col].fillna(df_clean[col].median(), inplace=True)
                    elif fill_strategy == 'forward_fill':
                        df_clean[col].fillna(method='ffill', inplace=True)
        
        # Drop rows with any null values
        if drop_null_rows:
            initial_rows = len(df_clean)
            df_clean = df_clean.dropna()
            removed = initial_rows - len(df_clean)
            if removed > 0:
                print(f"Dropped {removed} rows with null values")
        
        return df_clean
    
    @staticmethod
    def filter_data(df: pd.DataFrame, 
                   filters: Dict[str, Union[Any, Dict[str, Any]]]) -> pd.DataFrame:
        """Filter DataFrame based on column criteria
        
        Args:
            df: Input DataFrame
            filters: Dictionary of column names and filter criteria
                    Simple: {'age': 25} (equality)
                    Range: {'age': {'$gte': 18, '$lte': 65}}
                    Operators: {'$in': [1, 2, 3], '$nin': [4, 5]}
            
        Returns:
            Filtered DataFrame
        """
        df_filtered = df.copy()
        
        for column, criteria in filters.items():
            if column not in df_filtered.columns:
                print(f"Column '{column}' not found in DataFrame")
                continue
            
            # Handle different filter types
            if isinstance(criteria, dict):
                # Complex filter with operators
                if '$eq' in criteria:
                    df_filtered = df_filtered[df_filtered[column] == criteria['$eq']]
                if '$ne' in criteria:
                    df_filtered = df_filtered[df_filtered[column] != criteria['$ne']]
                if '$gt' in criteria:
                    df_filtered = df_filtered[df_filtered[column] > criteria['$gt']]
                if '$gte' in criteria:
                    df_filtered = df_filtered[df_filtered[column] >= criteria['$gte']]
                if '$lt' in criteria:
                    df_filtered = df_filtered[df_filtered[column] < criteria['$lt']]
                if '$lte' in criteria:
                    df_filtered = df_filtered[df_filtered[column] <= criteria['$lte']]
                if '$in' in criteria:
                    df_filtered = df_filtered[df_filtered[column].isin(criteria['$in'])]
                if '$nin' in criteria:
                    df_filtered = df_filtered[~df_filtered[column].isin(criteria['$nin'])]
                if '$contains' in criteria:
                    df_filtered = df_filtered[df_filtered[column].astype(str).str.contains(criteria['$contains'], case=False)]
            else:
                # Simple equality filter
                df_filtered = df_filtered[df_filtered[column] == criteria]
        
        return df_filtered
    
    @staticmethod
    def aggregate(df: pd.DataFrame,
                 group_by: Optional[Union[str, List[str]]] = None,
                 aggregations: Optional[Dict[str, Union[str, List[str]]]] = None) -> pd.DataFrame:
        """Perform aggregations on DataFrame
        
        Args:
            df: Input DataFrame
            group_by: Column(s) to group by
            aggregations: Dictionary of column names and aggregation functions
                         Can be: 'sum', 'mean', 'median', 'min', 'max', 'std', 'count'
                         Can also be list of multiple functions
                         Example: {'age': 'mean', 'salary': ['sum', 'mean']}
            
        Returns:
            Aggregated DataFrame
        """
        if aggregations is None:
            aggregations = {}
        
        if group_by is None:
            # Simple aggregations without grouping
            result = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if col in aggregations:
                    agg_funcs = aggregations[col]
                    if isinstance(agg_funcs, str):
                        agg_funcs = [agg_funcs]
                    
                    for func in agg_funcs:
                        key = f"{col}_{func}" if len(agg_funcs) > 1 else col
                        if func == 'sum':
                            result[key] = df[col].sum()
                        elif func == 'mean':
                            result[key] = df[col].mean()
                        elif func == 'median':
                            result[key] = df[col].median()
                        elif func == 'min':
                            result[key] = df[col].min()
                        elif func == 'max':
                            result[key] = df[col].max()
                        elif func == 'std':
                            result[key] = df[col].std()
                        elif func == 'count':
                            result[key] = df[col].count()
                else:
                    # Default aggregations
                    result[f"{col}_mean"] = df[col].mean()
                    result[f"{col}_sum"] = df[col].sum()
                    result[f"{col}_count"] = df[col].count()
            
            return pd.DataFrame([result])
        
        else:
            # Grouped aggregations
            grouped = df.groupby(group_by)
            
            if not aggregations:
                # Default aggregations for all numeric columns
                aggregations = {}
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                aggregations = {col: 'mean' for col in numeric_cols}
            
            return grouped.agg(aggregations).reset_index()
    
    @staticmethod
    def calculate_statistics(df: pd.DataFrame,
                           columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """Calculate detailed statistics for columns
        
        Args:
            df: Input DataFrame
            columns: Specific columns to analyze (defaults to all numeric)
            
        Returns:
            Dictionary with statistics for each column
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        statistics = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            col_data = df[col].dropna()
            
            if len(col_data) > 0:
                statistics[col] = {
                    'count': len(col_data),
                    'mean': float(col_data.mean()),
                    'median': float(col_data.median()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'q25': float(col_data.quantile(0.25)),
                    'q75': float(col_data.quantile(0.75)),
                    'variance': float(col_data.var()),
                    'sum': float(col_data.sum()),
                }
        
        return statistics
    
    @staticmethod
    def calculate_correlations(df: pd.DataFrame,
                              columns: Optional[List[str]] = None,
                              method: str = 'pearson') -> pd.DataFrame:
        """Calculate correlation matrix for numeric columns
        
        Args:
            df: Input DataFrame
            columns: Specific columns to correlate
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation DataFrame
        """
        numeric_df = df.select_dtypes(include=[np.number])
        
        if columns:
            numeric_df = numeric_df[[col for col in columns if col in numeric_df.columns]]
        
        return numeric_df.corr(method=method)
    
    @staticmethod
    def group_and_count(df: pd.DataFrame,
                       column: str,
                       top_n: Optional[int] = None) -> pd.Series:
        """Count occurrences of unique values in a column
        
        Args:
            df: Input DataFrame
            column: Column to count
            top_n: Limit to top N values
            
        Returns:
            Series with counts
        """
        counts = df[column].value_counts()
        
        if top_n:
            counts = counts.head(top_n)
        
        return counts
    
    @staticmethod
    def pivot_data(df: pd.DataFrame,
                  index: str,
                  columns: str,
                  values: str,
                  aggfunc: str = 'sum') -> pd.DataFrame:
        """Create pivot table from DataFrame
        
        Args:
            df: Input DataFrame
            index: Column to use as index
            columns: Column to use as columns
            values: Values to aggregate
            aggfunc: Aggregation function ('sum', 'mean', 'count')
            
        Returns:
            Pivoted DataFrame
        """
        return df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)
    
    @staticmethod
    def resample_time_series(df: pd.DataFrame,
                            date_column: str,
                            frequency: str = 'D',
                            aggregation: str = 'mean') -> pd.DataFrame:
        """Resample time series data
        
        Args:
            df: Input DataFrame
            date_column: Column with datetime values
            frequency: Resampling frequency ('D', 'W', 'M', 'Q', 'Y')
            aggregation: Aggregation function
            
        Returns:
            Resampled DataFrame
        """
        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])
        df_copy = df_copy.set_index(date_column)
        
        if aggregation == 'mean':
            return df_copy.resample(frequency).mean().reset_index()
        elif aggregation == 'sum':
            return df_copy.resample(frequency).sum().reset_index()
        elif aggregation == 'count':
            return df_copy.resample(frequency).count().reset_index()
        elif aggregation == 'first':
            return df_copy.resample(frequency).first().reset_index()
        elif aggregation == 'last':
            return df_copy.resample(frequency).last().reset_index()
        else:
            return df_copy.resample(frequency).mean().reset_index()
    
    @staticmethod
    def normalize_columns(df: pd.DataFrame,
                         columns: List[str] = None,
                         method: str = 'minmax') -> pd.DataFrame:
        """Normalize numeric columns
        
        Args:
            df: Input DataFrame
            columns: Columns to normalize (defaults to all numeric)
            method: Normalization method ('minmax' or 'zscore')
            
        Returns:
            DataFrame with normalized columns
        """
        df_norm = df.copy()
        
        if columns is None:
            columns = df_norm.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if col not in df_norm.columns:
                continue
            
            if method == 'minmax':
                # Min-Max normalization (0-1)
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                if max_val != min_val:
                    df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            
            elif method == 'zscore':
                # Z-score normalization
                mean_val = df_norm[col].mean()
                std_val = df_norm[col].std()
                if std_val != 0:
                    df_norm[col] = (df_norm[col] - mean_val) / std_val
        
        return df_norm
    
    @staticmethod
    def detect_outliers(df: pd.DataFrame,
                       columns: List[str] = None,
                       method: str = 'iqr',
                       threshold: float = 1.5) -> Dict[str, List[int]]:
        """Detect outliers in numeric columns
        
        Args:
            df: Input DataFrame
            columns: Columns to analyze (defaults to all numeric)
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Dictionary with outlier indices for each column
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outliers = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            col_data = df[col].dropna()
            
            if len(col_data) == 0:
                continue
            
            if method == 'iqr':
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - (threshold * iqr)
                upper = q3 + (threshold * iqr)
                outlier_mask = (df[col] < lower) | (df[col] > upper)
            
            elif method == 'zscore':
                mean = col_data.mean()
                std = col_data.std()
                z_scores = np.abs((df[col] - mean) / std)
                outlier_mask = z_scores > threshold
            
            else:
                continue
            
            outlier_indices = df[outlier_mask].index.tolist()
            if outlier_indices:
                outliers[col] = outlier_indices
        
        return outliers
