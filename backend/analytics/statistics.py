"""
Statistical analysis module using Pandas and NumPy
Demonstrates: mean, median, standard deviation, correlation analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Optional, Any


def _to_float(value: Any) -> float:
    """Convert scalar-like values to float while handling complex values safely."""
    if isinstance(value, complex):
        return float(value.real)
    return float(value)


class StatisticalAnalyzer:
    """
    Performs statistical analysis on datasets using Pandas and NumPy
    Computes: mean, median, std, correlation, distribution analysis
    """

    def __init__(self, dataframe: pd.DataFrame):
        """Initialize with a pandas DataFrame"""
        self.df = dataframe
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

    def compute_mean(self, column: Optional[str] = None) -> Union[float, Dict[str, float]]:
        """
        Compute mean using Pandas and NumPy
        If column specified, returns mean for that column
        Otherwise returns mean for all numeric columns
        """
        if column:
            if column not in self.numeric_cols:
                raise ValueError(f"Column '{column}' is not numeric")
            # Using both NumPy and Pandas
            return float(np.mean(self.df[column]))

        # Compute mean for all numeric columns
        means = {}
        for col in self.numeric_cols:
            means[col] = float(self.df[col].mean())  # Pandas method
        return means

    def compute_median(self, column: Optional[str] = None) -> Union[float, Dict[str, float]]:
        """
        Compute median using Pandas and NumPy
        If column specified, returns median for that column
        Otherwise returns median for all numeric columns
        """
        if column:
            if column not in self.numeric_cols:
                raise ValueError(f"Column '{column}' is not numeric")
            # Using NumPy
            return float(np.median(self.df[column]))

        # Compute median for all numeric columns
        medians = {}
        for col in self.numeric_cols:
            medians[col] = float(self.df[col].median())  # Pandas method
        return medians

    def compute_std(self, column: Optional[str] = None) -> Union[float, Dict[str, float]]:
        """
        Compute standard deviation using Pandas and NumPy
        If column specified, returns std for that column
        Otherwise returns std for all numeric columns
        """
        if column:
            if column not in self.numeric_cols:
                raise ValueError(f"Column '{column}' is not numeric")
            # Using NumPy
            return float(np.std(self.df[column], ddof=1))  # Sample std

        # Compute std for all numeric columns
        std_devs = {}
        for col in self.numeric_cols:
            std_devs[col] = float(self.df[col].std())  # Pandas method
        return std_devs

    def compute_all_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Compute all statistics for all numeric columns
        Returns: {column_name: {mean, median, std}}
        """
        statistics = {}

        for col in self.numeric_cols:
            statistics[col] = {
                'mean': _to_float(np.mean(self.df[col])),
                'median': _to_float(np.median(self.df[col])),
                'std': _to_float(np.std(self.df[col], ddof=1)),
                'min': _to_float(self.df[col].min()),
                'max': _to_float(self.df[col].max()),
                'count': int(self.df[col].count()),
                'missing': int(self.df[col].isna().sum())
            }

        return statistics

    def compute_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Compute correlation matrix for numeric columns using Pandas
        Returns: {col1: {col2: correlation_value}}
        """
        if len(self.numeric_cols) < 2:
            return {}

        corr_matrix = self.df[self.numeric_cols].corr()

        # Convert to nested dict
        result = {}
        for col1 in corr_matrix.columns:
            result[col1] = {}
            for col2 in corr_matrix.columns:
                result[col1][col2] = _to_float(corr_matrix.loc[col1, col2])

        return result

    def compute_distribution(self) -> Dict[str, Dict[str, Any]]:
        """
        Compute distribution statistics for each numeric column
        Returns percentiles, quartiles, etc.
        """
        distribution = {}

        for col in self.numeric_cols:
            distribution[col] = {
                'q1': _to_float(self.df[col].quantile(0.25)),
                'q2': _to_float(self.df[col].quantile(0.50)),  # Median
                'q3': _to_float(self.df[col].quantile(0.75)),
                'iqr': _to_float(self.df[col].quantile(0.75) - self.df[col].quantile(0.25)),
                'skewness': _to_float(self.df[col].skew()),
                'kurtosis': _to_float(self.df[col].kurtosis())
            }

        return distribution

    def get_summary_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistical summary report
        """
        return {
            'dataset_info': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'numeric_columns': len(self.numeric_cols),
                'column_names': list(self.df.columns)
            },
            'statistics': self.compute_all_statistics(),
            'correlations': self.compute_correlation_matrix(),
            'distributions': self.compute_distribution(),
            'missing_values': {
                col: int(self.df[col].isna().sum())
                for col in self.df.columns
            }
        }
