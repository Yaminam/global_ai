"""
Analytics routes - handles analytics, visualizations, and data aggregations
"""

from flask import Blueprint, request, jsonify, current_app, send_file
import os
import json
import numpy as np
from datetime import datetime

from backend.config import get_config
from backend.services.file_service import FileService
from backend.services.analytics_service import AnalyticsService
from backend.services.visualization_engine import VisualizationEngine
from backend.services.data_aggregator import DataAggregator
from utils.helpers import generate_uuid, create_success_response, create_error_response


bp = Blueprint('analytics', __name__, url_prefix='/api')

# Initialize services
config = get_config('development')
file_service = FileService(
    upload_folder=config.UPLOAD_FOLDER,
    max_file_size_bytes=config.MAX_FILE_SIZE_BYTES,
    allowed_extensions=config.ALLOWED_EXTENSIONS
)
analytics_service = AnalyticsService()
viz_engine = VisualizationEngine()
data_aggregator = DataAggregator()


@bp.route('/analytics', methods=['POST'])
def perform_analytics():
    """Perform analytics on uploaded data
    
    Expected JSON body:
        - file_path: Path to file to analyze
    
    Returns:
        JSON response with analytics results
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            current_app.logger.warning("Analytics request without file_path")
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        job_id = data.get('job_id', f"job-{generate_uuid()}")
        dataset_id = data.get('dataset_id', f"dataset-{generate_uuid()}")
        
        # Load file
        success, df, load_message = file_service.load_file_data(file_path)
        
        if not success:
            current_app.logger.warning(f"Failed to load file for analytics: {load_message}")
            return jsonify(create_error_response(
                error='File load failed',
                details=load_message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        # Perform analytics
        analytics_result = analytics_service.perform_analytics(df, job_id, dataset_id)
        
        # Export results
        exported = analytics_service.export_analytics(analytics_result)
        
        current_app.logger.info(f"Analytics completed for job: {job_id}")
        
        return jsonify(create_success_response(
            data=exported,
            message='Analytics completed successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in analytics: {str(e)}")
        return jsonify(create_error_response(
            error='Analytics error',
            details=str(e),
            error_code='ANALYTICS_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/<job_id>', methods=['GET'])
def get_analytics(job_id):
    """Get analytics for a specific job
    
    Args:
        job_id: Job ID
    
    Returns:
        JSON response with analytics results
    """
    try:
        # 1) Try persistent analytics first.
        storage = current_app.config.get('data_storage')
        if storage:
            stored_ok, stored_analytics, _ = storage.load_analytics(job_id)
            if stored_ok and stored_analytics:
                return jsonify(create_success_response(
                    data=stored_analytics,
                    message='Analytics retrieved successfully'
                )), 200

        # 2) Build analytics from the async job source file.
        async_processor = current_app.config.get('async_processor')
        if not async_processor:
            return jsonify(create_error_response(
                error='Async processor not available',
                details='The async processor is not configured',
                error_code='ASYNC_UNAVAILABLE',
                status_code=500
            )), 500

        job_status = async_processor.get_job_status(job_id)
        if not job_status.get('found'):
            return jsonify(create_error_response(
                error='Analytics not found',
                details=f"No analytics data found for job {job_id}",
                error_code='ANALYTICS_NOT_FOUND',
                status_code=404
            )), 404

        file_path = job_status.get('file_path')
        if not file_path:
            return jsonify(create_error_response(
                error='Source file not found',
                details=f"No file path available for job {job_id}",
                error_code='SOURCE_FILE_NOT_FOUND',
                status_code=404
            )), 404

        success, df, load_message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=load_message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400

        # Create frontend-compatible summary fields.
        total_records = int(len(df))
        total_columns = int(len(df.columns))
        missing_values = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        numeric_df = df.select_dtypes(include=[np.number])
        distribution = {}
        correlations = {}

        if len(numeric_df.columns) > 0:
            # Use mean values as a compact distribution summary per numeric column.
            distribution = {
                col: float(numeric_df[col].mean()) if not np.isnan(numeric_df[col].mean()) else 0.0
                for col in numeric_df.columns[:10]
            }

            corr_matrix = numeric_df.corr(numeric_only=True).fillna(0.0)
            for col in corr_matrix.columns[:10]:
                # Average absolute correlation (excluding self-correlation).
                col_values = corr_matrix[col].drop(labels=[col], errors='ignore').abs()
                correlations[col] = float(col_values.mean()) if len(col_values) > 0 else 0.0

        missing_analysis = {
            col: int(df[col].isna().sum())
            for col in df.columns[:10]
        }

        data_points = max(total_records * max(total_columns, 1), 1)
        missing_ratio = missing_values / data_points
        duplicate_ratio = duplicate_rows / max(total_records, 1)
        quality_score = max(0.0, min(100.0, 100.0 - ((missing_ratio * 70.0) + (duplicate_ratio * 30.0)) * 100.0))

        analytics_payload = {
            'job_id': job_id,
            'source_file_path': file_path,
            'statistics': {
                'total_records': total_records,
                'total_columns': total_columns,
                'missing_values': missing_values,
                'duplicate_rows': duplicate_rows
            },
            'distribution': distribution,
            'correlations': correlations,
            'missing_analysis': missing_analysis,
            'quality_score': round(float(quality_score), 2),
            'generated_at': datetime.utcnow().isoformat()
        }

        # Persist generated analytics for faster future retrieval.
        if storage:
            storage.save_analytics(job_id, analytics_payload)

        return jsonify(create_success_response(
            data=analytics_payload,
            message='Analytics generated successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving analytics: {str(e)}")
        return jsonify(create_error_response(
            error='Retrieval error',
            details=str(e),
            error_code='RETRIEVAL_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/stats/<job_id>', methods=['GET'])
def get_analytics_stats(job_id):
    """Get statistical analysis for a job
    
    Args:
        job_id: Job ID
    
    Query parameters:
        - include: Comma-separated stats to include (numeric, categorical, all)
    
    Returns:
        JSON response with statistical analysis
    """
    try:
        include = request.args.get('include', 'all')
        
        # In a real implementation, this would work with persisted analytics
        return jsonify(create_error_response(
            error='Analytics not found',
            details=f"No analytics data for job {job_id}",
            error_code='ANALYTICS_NOT_FOUND',
            status_code=404
        )), 404
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving analytics stats: {str(e)}")
        return jsonify(create_error_response(
            error='Error retrieving stats',
            details=str(e),
            error_code='STATS_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/anomalies/<job_id>', methods=['GET'])
def get_anomalies(job_id):
    """Get detected anomalies for a job
    
    Args:
        job_id: Job ID
    
    Query parameters:
        - type: Anomaly type to filter (outliers, missing, duplicates, all)
    
    Returns:
        JSON response with anomalies
    """
    try:
        anomaly_type = request.args.get('type', 'all')
        
        # In a real implementation, this would work with persisted analytics
        return jsonify(create_error_response(
            error='Anomalies not found',
            details=f"No anomaly data for job {job_id}",
            error_code='ANOMALIES_NOT_FOUND',
            status_code=404
        )), 404
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving anomalies: {str(e)}")
        return jsonify(create_error_response(
            error='Error retrieving anomalies',
            details=str(e),
            error_code='ANOMALY_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/trends/<job_id>', methods=['GET'])
def get_trends(job_id):
    """Get trend analysis for a job
    
    Args:
        job_id: Job ID
    
    Returns:
        JSON response with trend analysis
    """
    try:
        # In a real implementation, this would work with persisted analytics
        return jsonify(create_error_response(
            error='Trends not found',
            details=f"No trend data for job {job_id}",
            error_code='TRENDS_NOT_FOUND',
            status_code=404
        )), 404
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving trends: {str(e)}")
        return jsonify(create_error_response(
            error='Error retrieving trends',
            details=str(e),
            error_code='TREND_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/insights/<job_id>', methods=['GET'])
def get_insights(job_id):
    """Get AI-generated insights for a job
    
    Args:
        job_id: Job ID
    
    Query parameters:
        - severity: Filter by severity level (low, medium, high, all)
    
    Returns:
        JSON response with insights
    """
    try:
        severity = request.args.get('severity', 'all')
        
        # In a real implementation, this would work with persisted analytics
        return jsonify(create_error_response(
            error='Insights not found',
            details=f"No insight data for job {job_id}",
            error_code='INSIGHTS_NOT_FOUND',
            status_code=404
        )), 404
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving insights: {str(e)}")
        return jsonify(create_error_response(
            error='Error retrieving insights',
            details=str(e),
            error_code='INSIGHT_ERROR',
            status_code=500
        )), 500


# ============================================================================
# VISUALIZATION ENDPOINTS
# ============================================================================

@bp.route('/analytics/visualize/histogram', methods=['POST'])
def create_histogram():
    """Create a histogram visualization
    
    Expected JSON body:
        - file_path: Path to file
        - column: Column to analyze
        - title: Chart title (optional)
        - bins: Number of bins (optional, default 30)
    
    Returns:
        JSON response with chart path
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data or 'column' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path and column',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        column = data['column']
        title = data.get('title', f'Distribution of {column}')
        bins = data.get('bins', 30)
        filename = data.get('filename', f'histogram_{column}_{generate_uuid()}.png')
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        if column not in df.columns:
            return jsonify(create_error_response(
                error='Column not found',
                details=f'Column "{column}" not in dataset',
                error_code='COLUMN_NOT_FOUND',
                status_code=400
            )), 400
        
        chart_path = viz_engine.generate_histogram(
            df[column],
            title=title,
            xlabel=column,
            filename=filename,
            bins=bins
        )
        
        current_app.logger.info(f"Histogram created: {chart_path}")
        
        return jsonify(create_success_response(
            data={'chart_path': chart_path},
            message='Histogram created successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error creating histogram: {str(e)}")
        return jsonify(create_error_response(
            error='Visualization error',
            details=str(e),
            error_code='VIZ_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/aggregate', methods=['POST'])
def aggregate_data():
    """Aggregate data from a file
    
    Expected JSON body:
        - file_path: Path to file
        - group_by: Column(s) to group by (optional)
        - aggregations: {'column': 'func'} where func is sum, mean, count, etc
    
    Returns:
        JSON response with aggregation results
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        group_by = data.get('group_by')
        aggregations = data.get('aggregations')
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        result = data_aggregator.aggregate(df, group_by=group_by, aggregations=aggregations)
        
        current_app.logger.info(f"Data aggregation completed")
        
        return jsonify(create_success_response(
            data={'results': result.to_dict(orient='records')},
            message='Aggregation completed successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error aggregating data: {str(e)}")
        return jsonify(create_error_response(
            error='Aggregation error',
            details=str(e),
            error_code='AGG_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/filter', methods=['POST'])
def filter_data():
    """Filter data based on criteria
    
    Expected JSON body:
        - file_path: Path to file
        - filters: {'column': value or {operators}}
            Operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, $contains
    
    Returns:
        JSON response with filtered data
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data or 'filters' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path and filters',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        filters = data['filters']
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        filtered_df = data_aggregator.filter_data(df, filters)
        
        current_app.logger.info(f"Data filtered: {len(filtered_df)} rows returned from {len(df)}")
        
        return jsonify(create_success_response(
            data={
                'row_count': len(filtered_df),
                'original_count': len(df),
                'sample': filtered_df.head(10).to_dict(orient='records')
            },
            message=f'Filtered to {len(filtered_df)} rows'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error filtering data: {str(e)}")
        return jsonify(create_error_response(
            error='Filter error',
            details=str(e),
            error_code='FILTER_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/statistics', methods=['POST'])
def get_statistics():
    """Get detailed statistics for numeric columns
    
    Expected JSON body:
        - file_path: Path to file
        - columns: List of columns to analyze (optional)
    
    Returns:
        JSON response with statistics
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        columns = data.get('columns')
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        stats = data_aggregator.calculate_statistics(df, columns=columns)
        
        current_app.logger.info(f"Statistics calculated for {len(stats)} columns")
        
        return jsonify(create_success_response(
            data={'statistics': stats},
            message='Statistics calculated successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error calculating statistics: {str(e)}")
        return jsonify(create_error_response(
            error='Statistics error',
            details=str(e),
            error_code='STATS_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/correlations', methods=['POST'])
def get_correlations():
    """Get correlation matrix for numeric columns
    
    Expected JSON body:
        - file_path: Path to file
        - columns: List of columns (optional)
        - method: 'pearson', 'spearman', or 'kendall' (optional)
    
    Returns:
        JSON response with correlation matrix
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        columns = data.get('columns')
        method = data.get('method', 'pearson')
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        corr_matrix = data_aggregator.calculate_correlations(df, columns=columns, method=method)
        
        current_app.logger.info(f"Correlation matrix calculated with {method} method")
        
        return jsonify(create_success_response(
            data={'correlations': corr_matrix.to_dict()},
            message='Correlations calculated successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error calculating correlations: {str(e)}")
        return jsonify(create_error_response(
            error='Correlation error',
            details=str(e),
            error_code='CORR_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/outliers', methods=['POST'])
def detect_outliers():
    """Detect outliers in numeric columns
    
    Expected JSON body:
        - file_path: Path to file
        - columns: List of columns to analyze (optional)
        - method: 'iqr' or 'zscore' (optional, default 'iqr')
        - threshold: Detection threshold (optional)
    
    Returns:
        JSON response with outlier information
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        columns = data.get('columns')
        method = data.get('method', 'iqr')
        threshold = data.get('threshold', 1.5 if method == 'iqr' else 3)
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        outliers = data_aggregator.detect_outliers(
            df, 
            columns=columns, 
            method=method, 
            threshold=threshold
        )
        
        current_app.logger.info(f"Outlier detection completed: {sum(len(v) for v in outliers.values())} outliers found")
        
        return jsonify(create_success_response(
            data={'outliers': outliers},
            message='Outlier detection completed successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error detecting outliers: {str(e)}")
        return jsonify(create_error_response(
            error='Outlier detection error',
            details=str(e),
            error_code='OUTLIER_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics/clean', methods=['POST'])
def clean_data():
    """Clean data by removing duplicates and handling missing values
    
    Expected JSON body:
        - file_path: Path to file
        - drop_duplicates: True/False (optional)
        - drop_null_rows: True/False (optional)
        - fill_strategy: 'mean', 'median', 'forward_fill' (optional)
    
    Returns:
        JSON response with cleaning results
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data['file_path']
        drop_duplicates = data.get('drop_duplicates', True)
        drop_null_rows = data.get('drop_null_rows', False)
        fill_strategy = data.get('fill_strategy', None)
        
        success, df, message = file_service.load_file_data(file_path)
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        original_rows = len(df)
        cleaned_df = data_aggregator.clean_data(
            df,
            drop_duplicates=drop_duplicates,
            drop_null_rows=drop_null_rows,
            fill_strategy=fill_strategy
        )
        
        removed_rows = original_rows - len(cleaned_df)
        
        current_app.logger.info(f"Data cleaned: {removed_rows} rows removed")
        
        return jsonify(create_success_response(
            data={
                'original_rows': original_rows,
                'cleaned_rows': len(cleaned_df),
                'rows_removed': removed_rows,
                'null_counts_before': df.isnull().sum().to_dict(),
                'null_counts_after': cleaned_df.isnull().sum().to_dict()
            },
            message='Data cleaning completed successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error cleaning data: {str(e)}")
        return jsonify(create_error_response(
            error='Data cleaning error',
            details=str(e),
            error_code='CLEAN_ERROR',
            status_code=500
        )), 500
