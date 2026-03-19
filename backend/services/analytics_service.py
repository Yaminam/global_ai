"""
Analytics service - handles data analysis and insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from utils.helpers import generate_uuid, get_timestamp
from backend.models.data_models import AnalyticsResult


class AnalyticsService:
    """Service for performing data analytics and generating insights"""
    
    def perform_analytics(self, df: pd.DataFrame, job_id: str, dataset_id: str) -> AnalyticsResult:
        """Perform comprehensive analytics on DataFrame
        
        Args:
            df: Pandas DataFrame to analyze
            job_id: Associated job ID
            dataset_id: Associated dataset ID
            
        Returns:
            AnalyticsResult object
        """
        analytics_id = f"analytics-{generate_uuid()}"
        
        statistical_analysis = self._perform_statistical_analysis(df)
        anomaly_detection = self._detect_anomalies(df)
        trend_analysis = self._perform_trend_analysis(df)
        insights = self._generate_insights(df, statistical_analysis, anomaly_detection)
        
        return AnalyticsResult(
            analytics_id=analytics_id,
            job_id=job_id,
            dataset_id=dataset_id,
            statistical_analysis=statistical_analysis,
            anomaly_detection=anomaly_detection,
            trend_analysis=trend_analysis,
            insights=[f"{ins.get('type', 'info')}: {ins.get('message', '')}" for ins in insights],
            created_at=datetime.now().isoformat()
        )
    
    def _perform_statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical analysis on DataFrame
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with statistical metrics
        """
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage_bytes': df.memory_usage(deep=True).sum(),
            'numeric_columns': {}
        }
        
        # Analyze numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            
            if len(col_data) > 0:
                stats['numeric_columns'][col] = {
                    'dtype': str(df[col].dtype),
                    'count': len(col_data),
                    'null_count': df[col].isnull().sum(),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'mean': float(col_data.mean()),
                    'median': float(col_data.median()),
                    'std': float(col_data.std()),
                    'variance': float(col_data.var()),
                    'quartile_25': float(col_data.quantile(0.25)),
                    'quartile_75': float(col_data.quantile(0.75)),
                    'iqr': float(col_data.quantile(0.75) - col_data.quantile(0.25)),
                    'skewness': float(col_data.skew() or 0.0) if not pd.isna(col_data.skew()) else 0.0,  # type: ignore
                    'kurtosis': float(col_data.kurtosis() or 0.0) if not pd.isna(col_data.kurtosis()) else 0.0  # type: ignore
                }
        
        # Analyze categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        stats['categorical_columns'] = {}
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            stats['categorical_columns'][col] = {
                'dtype': str(df[col].dtype),
                'unique_count': df[col].nunique(),
                'null_count': df[col].isnull().sum(),
                'top_values': value_counts.head(5).to_dict()
            }
        
        return stats
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in DataFrame
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with anomaly detection results
        """
        anomalies = {
            'missing_values': {},
            'outliers': {},
            'duplicates': {
                'total_duplicates': int(df.duplicated().sum()),
                'duplicate_indices': df[df.duplicated(keep=False)].index.tolist()
            }
        }
        
        # Detect missing values
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                anomalies['missing_values'][col] = {
                    'count': int(null_count),
                    'percentage': float((null_count / len(df)) * 100),
                    'indices': df[df[col].isnull()].index.tolist()[:10]  # First 10
                }
        
        # Detect outliers using IQR method
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            
            if len(col_data) > 0:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    outlier_indices = df[outlier_mask].index.tolist()
                    anomalies['outliers'][col] = {
                        'count': int(outlier_count),
                        'percentage': float((outlier_count / len(df)) * 100),
                        'bounds': {
                            'lower': float(lower_bound),
                            'upper': float(upper_bound)
                        },
                        'indices': outlier_indices[:10]  # First 10
                    }
        
        return anomalies
    
    def _perform_trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform trend analysis on numeric columns
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with trend analysis
        """
        trends = {
            'numeric_trends': {}
        }
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            
            if len(col_data) > 1:
                # Calculate simple linear trend
                x = np.arange(len(col_data), dtype=float)
                y = col_data.values
                
                try:
                    y_values = np.asarray(y, dtype=float)
                    coefficients = np.polyfit(x, y_values, 1)
                    trend_direction = 'increasing' if coefficients[0] > 0 else 'decreasing'
                    
                    # Calculate first and last values
                    first_value = float(col_data.iloc[0])
                    last_value = float(col_data.iloc[-1])
                    change_percentage = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
                    
                    corr_value = float(np.corrcoef(x, y_values)[0, 1]) if len(x) > 1 else 0.0
                    corr_value = 0.0 if np.isnan(corr_value) else corr_value
                    
                    trends['numeric_trends'][col] = {
                        'direction': trend_direction,
                        'slope': float(coefficients[0]),
                        'intercept': float(coefficients[1]),
                        'first_value': first_value,
                        'last_value': last_value,
                        'change_percentage': float(change_percentage),
                        'correlation': corr_value
                    }
                except:
                    pass  # Skip columns where polyfit fails
        
        return trends
    
    def _generate_insights(self, df: pd.DataFrame, stats: Dict[str, Any], 
                          anomalies: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate insights based on analysis
        
        Args:
            df: Pandas DataFrame
            stats: Statistical analysis results
            anomalies: Anomaly detection results
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Row count insight
        row_count = stats['row_count']
        if row_count == 0:
            insights.append({
                'type': 'warning',
                'severity': 'high',
                'message': 'Dataset is empty with 0 rows'
            })
        elif row_count < 100:
            insights.append({
                'type': 'info',
                'severity': 'medium',
                'message': f'Small dataset with only {row_count} rows - limited statistical power'
            })
        
        # Missing values insight
        total_nulls = sum([v['count'] for v in anomalies.get('missing_values', {}).values()])
        if total_nulls > 0:
            null_percentage = (total_nulls / (row_count * stats['column_count'])) * 100
            if null_percentage > 20:
                insights.append({
                    'type': 'warning',
                    'severity': 'high',
                    'message': f'High proportion of missing values: {null_percentage:.1f}% of all data points'
                })
            elif null_percentage > 5:
                insights.append({
                    'type': 'info',
                    'severity': 'medium',
                    'message': f'Moderate missing values: {null_percentage:.1f}% of data'
                })
        
        # Duplicates insight
        duplicates = anomalies.get('duplicates', {}).get('total_duplicates', 0)
        if duplicates > 0:
            dup_percentage = (duplicates / row_count) * 100
            insights.append({
                'type': 'warning',
                'severity': 'medium',
                'message': f'Found {duplicates} duplicate rows ({dup_percentage:.1f}% of dataset)'
            })
        
        # Outliers insight
        total_outliers = sum([v['count'] for v in anomalies.get('outliers', {}).values()])
        if total_outliers > 0:
            insights.append({
                'type': 'info',
                'severity': 'low',
                'message': f'Detected {total_outliers} outlier instances across numeric columns'
            })
        
        # Skewness insight
        for col, col_stats in stats.get('numeric_columns', {}).items():
            skewness = col_stats.get('skewness', 0)
            if abs(skewness) > 1:
                insights.append({
                    'type': 'info',
                    'severity': 'low',
                    'message': f'Column "{col}" shows high skewness ({skewness:.2f}) - consider transformation'
                })
        
        # High cardinality insight
        for col, col_stats in stats.get('categorical_columns', {}).items():
            unique_count = col_stats.get('unique_count', 0)
            if unique_count > row_count * 0.9:
                insights.append({
                    'type': 'info',
                    'severity': 'low',
                    'message': f'Column "{col}" has very high cardinality ({unique_count} unique values)'
                })
        
        # Column distribution insight
        numeric_count = len(stats.get('numeric_columns', {}))
        categorical_count = len(stats.get('categorical_columns', {}))
        
        if numeric_count == 0 and categorical_count > 0:
            insights.append({
                'type': 'info',
                'severity': 'low',
                'message': 'Dataset contains only categorical columns - limited statistical analysis possible'
            })
        elif numeric_count > 0 and categorical_count == 0:
            insights.append({
                'type': 'info',
                'severity': 'low',
                'message': 'Dataset contains only numeric columns - consider categorical encoding if needed'
            })
        
        # Default insight if none generated
        if len(insights) == 0:
            insights.append({
                'type': 'success',
                'severity': 'low',
                'message': 'Dataset appears clean with no major issues detected'
            })
        
        return insights
    
    def export_analytics(self, analytics: AnalyticsResult, format: str = 'json') -> Dict[str, Any]:
        """Export analytics results
        
        Args:
            analytics: AnalyticsResult object
            format: Export format (json, dict)
            
        Returns:
            Dictionary representation of analytics
        """
        return {
            'analytics_id': analytics.analytics_id,
            'job_id': analytics.job_id,
            'dataset_id': analytics.dataset_id,
            'statistical_analysis': analytics.statistical_analysis,
            'anomaly_detection': analytics.anomaly_detection,
            'trend_analysis': analytics.trend_analysis,
            'insights': analytics.insights,
            'timestamp': get_timestamp()
        }
