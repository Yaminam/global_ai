"""
Results retrieval routes
"""

from flask import Blueprint, request, jsonify, current_app
import os
import pandas as pd
from typing import Optional
from io import BytesIO

from backend.config import get_config
from backend.services.processing_service import ProcessingService
from utils.helpers import create_success_response, create_error_response


bp = Blueprint('results', __name__, url_prefix='/api')

# Initialize services
config = get_config('development')
processing_service = ProcessingService(config.RESULTS_FOLDER)


def _load_df(file_path: str, nrows: Optional[int] = None):
    """Load a dataframe from csv/json result file."""
    if not file_path or not os.path.exists(file_path):
        return None

    if file_path.endswith('.csv'):
        return pd.read_csv(file_path, nrows=nrows)

    if file_path.endswith('.json'):
        df = pd.read_json(file_path)
        return df.head(nrows) if nrows else df

    return None


@bp.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get processing results
    
    Args:
        job_id: Job ID
    
    Query parameters:
        - nrows: Number of rows to preview (default: 10)
        - format: Result format (json, csv, all)
    
    Returns:
        JSON response with results data
    """
    try:
        success, job, message = processing_service.get_job(job_id)
        
        if not success or job is None:
            # Fallback to async processor jobs
            async_processor = current_app.config.get('async_processor')
            if not async_processor:
                current_app.logger.warning(f"Job not found: {job_id}")
                return jsonify(create_error_response(
                    error='Job not found',
                    details=message,
                    error_code='JOB_NOT_FOUND',
                    status_code=404
                )), 404

            async_status = async_processor.get_job_status(job_id)
            if not async_status.get('found'):
                current_app.logger.warning(f"Job not found: {job_id}")
                return jsonify(create_error_response(
                    error='Job not found',
                    details=message,
                    error_code='JOB_NOT_FOUND',
                    status_code=404
                )), 404

            if async_status.get('status') != 'completed':
                return jsonify(create_error_response(
                    error='Job not completed',
                    details=f"Job status is '{async_status.get('status')}'. Only completed jobs have results.",
                    error_code='JOB_NOT_COMPLETED',
                    status_code=400
                )), 400

            nrows = request.args.get('nrows', 10, type=int)
            result_file_path = async_status.get('result_file_path') or async_status.get('file_path')

            if not result_file_path or not os.path.exists(result_file_path):
                return jsonify(create_error_response(
                    error='Results file not found',
                    details='No result file was generated for this async job',
                    error_code='RESULTS_NOT_FOUND',
                    status_code=404
                )), 404

            full_df = _load_df(result_file_path)
            preview_df = _load_df(result_file_path, nrows=nrows)
            if full_df is None or preview_df is None:
                return jsonify(create_error_response(
                    error='Results format unsupported',
                    details='Only CSV/JSON results are supported',
                    error_code='RESULTS_FORMAT_ERROR',
                    status_code=400
                )), 400

            numeric_stats = {}
            for col in preview_df.columns:
                if pd.api.types.is_numeric_dtype(preview_df[col]):
                    numeric_stats[col] = {
                        'min': float(preview_df[col].min()),
                        'max': float(preview_df[col].max()),
                        'mean': float(preview_df[col].mean()),
                        'median': float(preview_df[col].median())
                    }

            response_data = {
                'job_id': job_id,
                'dataset_id': async_status.get('dataset_id', ''),
                'status': async_status.get('status'),
                'metadata': {
                    'total_rows': int(len(full_df)),
                    'columns': list(full_df.columns),
                    'column_count': int(len(full_df.columns)),
                    'created_at': async_status.get('submitted_at'),
                    'completed_at': async_status.get('completed_at')
                },
                'preview': {
                    'rows': preview_df.to_dict('records'),
                    'row_count': int(len(preview_df)),
                    'limit': nrows
                },
                'statistics': numeric_stats,
                'result_file_path': result_file_path,
                'summary': f"Processed {len(full_df)} records across {len(full_df.columns)} columns",
                'insights': [
                    f"Output rows: {len(full_df)}",
                    f"Columns: {len(full_df.columns)}",
                    f"Source file: {os.path.basename(async_status.get('file_path', 'unknown'))}"
                ]
            }

            return jsonify(create_success_response(
                data=response_data,
                message='Results retrieved successfully'
            )), 200
        
        if job.status != 'completed':
            return jsonify(create_error_response(
                error='Job not completed',
                details=f"Job status is '{job.status}'. Only completed jobs have results.",
                error_code='JOB_NOT_COMPLETED',
                status_code=400
            )), 400
        
        if not job.result_file_path or not os.path.exists(job.result_file_path):
            return jsonify(create_error_response(
                error='Results file not found',
                details='The results file for this job could not be located',
                error_code='RESULTS_NOT_FOUND',
                status_code=404
            )), 404
        
        # Get preview
        nrows = request.args.get('nrows', 10, type=int)
        preview = processing_service.get_result_preview(job_id, nrows)
        
        if 'error' in preview:
            return jsonify(create_error_response(
                error='Error retrieving results preview',
                details=preview.get('error', 'Unknown error'),
                error_code='PREVIEW_ERROR',
                status_code=500
            )), 500
        
        current_app.logger.info(f"Results retrieved for job: {job_id}")
        
        response_data = {
            'job_id': job_id,
            'dataset_id': job.dataset_id,
            'status': job.status,
            'metadata': {
                'total_rows': preview.get('total_rows', 0),
                'columns': preview.get('columns', []),
                'column_count': len(preview.get('columns', [])),
                'created_at': job.created_at,
                'completed_at': job.completed_at
            },
            'preview': {
                'rows': preview.get('preview', []),
                'row_count': len(preview.get('preview', [])),
                'limit': nrows
            },
            'statistics': preview.get('statistics', {}),
            'result_file_path': job.result_file_path
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Results retrieved successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving results: {str(e)}")
        return jsonify(create_error_response(
            error='Error retrieving results',
            details=str(e),
            error_code='RETRIEVAL_ERROR',
            status_code=500
        )), 500


@bp.route('/results/<job_id>/download', methods=['GET'])
def download_results(job_id):
    """Download results file
    
    Args:
        job_id: Job ID
    
    Query parameters:
        - format: Format to download (json, csv)
    
    Returns:
        File download or JSON error
    """
    try:
        from flask import send_file
        
        success, job, message = processing_service.get_job(job_id)
        
        if not success or job is None:
            # Fallback to async processor jobs
            async_processor = current_app.config.get('async_processor')
            if not async_processor:
                current_app.logger.warning(f"Job not found: {job_id}")
                return jsonify(create_error_response(
                    error='Job not found',
                    details=message,
                    error_code='JOB_NOT_FOUND',
                    status_code=404
                )), 404

            async_status = async_processor.get_job_status(job_id)

            if not async_status.get('found'):
                current_app.logger.warning(f"Job not found: {job_id}")
                return jsonify(create_error_response(
                    error='Job not found',
                    details=message,
                    error_code='JOB_NOT_FOUND',
                    status_code=404
                )), 404

            if async_status.get('status') != 'completed':
                return jsonify(create_error_response(
                    error='Job not completed',
                    details=f"Job status is '{async_status.get('status')}'",
                    error_code='JOB_NOT_COMPLETED',
                    status_code=400
                )), 400

            requested_format = request.args.get('format', 'csv').lower()
            if requested_format == 'json':
                result_path = async_status.get('result_json_path')
                download_name = f"results_{job_id}.json"
            else:
                result_path = async_status.get('result_file_path')
                download_name = f"results_{job_id}.csv"

            if not result_path or not os.path.exists(result_path):
                return jsonify(create_error_response(
                    error='Results file not found',
                    details='The results file could not be located',
                    error_code='RESULTS_NOT_FOUND',
                    status_code=404
                )), 404

            current_app.logger.info(f"Results file downloaded for async job: {job_id}")
            return send_file(
                result_path,
                as_attachment=True,
                download_name=download_name
            )
        
        if job.status != 'completed':
            return jsonify(create_error_response(
                error='Job not completed',
                details=f"Job status is '{job.status}'",
                error_code='JOB_NOT_COMPLETED',
                status_code=400
            )), 400
        
        if not job.result_file_path or not os.path.exists(job.result_file_path):
            return jsonify(create_error_response(
                error='Results file not found',
                details='The results file could not be located',
                error_code='RESULTS_NOT_FOUND',
                status_code=404
            )), 404
        
        requested_format = request.args.get('format', 'json').lower()
        download_name = f"results_{job_id}.json"
        file_to_download = job.result_file_path

        if requested_format == 'csv' and job.result_file_path and job.result_file_path.endswith('.json'):
            json_df = pd.read_json(job.result_file_path)
            csv_path = os.path.splitext(job.result_file_path)[0] + '.csv'
            json_df.to_csv(csv_path, index=False)
            file_to_download = csv_path
            download_name = f"results_{job_id}.csv"
        elif requested_format == 'csv':
            download_name = f"results_{job_id}.csv"

        current_app.logger.info(f"Results file downloaded for job: {job_id}")
        
        return send_file(
            file_to_download,
            as_attachment=True,
            download_name=download_name
        )
    
    except Exception as e:
        current_app.logger.error(f"Error downloading results: {str(e)}")
        return jsonify(create_error_response(
            error='Download error',
            details=str(e),
            error_code='DOWNLOAD_ERROR',
            status_code=500
        )), 500


@bp.route('/results/<job_id>/stats', methods=['GET'])
def get_result_statistics(job_id):
    """Get detailed statistics for results
    
    Args:
        job_id: Job ID
    
    Returns:
        JSON response with detailed statistics
    """
    try:
        success, job, message = processing_service.get_job(job_id)
        
        if not success or job is None:
            return jsonify(create_error_response(
                error='Job not found',
                details=message,
                error_code='JOB_NOT_FOUND',
                status_code=404
            )), 404
        
        if job.status != 'completed':
            return jsonify(create_error_response(
                error='Job not completed',
                details=f"Job status is '{job.status}'",
                error_code='JOB_NOT_COMPLETED',
                status_code=400
            )), 400
        
        preview = processing_service.get_result_preview(job_id, 1000)
        
        if 'error' in preview:
            return jsonify(create_error_response(
                error='Error retrieving statistics',
                details=preview.get('error'),
                error_code='STATS_ERROR',
                status_code=500
            )), 500
        
        response_data = {
            'job_id': job_id,
            'metadata': {
                'total_rows': preview.get('total_rows', 0),
                'columns': preview.get('columns', []),
                'processing_duration_ms': (
                    job.duration_ms if job.duration_ms else 
                    (job.input_rows or 0)
                )
            },
            'row_count': {
                'input_rows': job.input_rows or 0,
                'processed_rows': job.processed_rows or 0,
                'output_rows': job.output_rows or 0
            },
            'column_statistics': preview.get('statistics', {}),
            'processing_info': {
                'created_at': job.created_at,
                'completed_at': job.completed_at,
                'status': job.status
            }
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Result statistics retrieved'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving statistics: {str(e)}")
        return jsonify(create_error_response(
            error='Statistics error',
            details=str(e),
            error_code='STATS_ERROR',
            status_code=500
        )), 500


@bp.route('/results', methods=['GET'])
def list_results():
    """List all available results
    
    Returns:
        JSON response with list of jobs and their results
    """
    try:
        all_jobs = []
        
        for job_id, job in processing_service.jobs.items():
            if job.status == 'completed':
                all_jobs.append({
                    'job_id': job.job_id,
                    'dataset_id': job.dataset_id,
                    'status': job.status,
                    'row_count': job.output_rows,
                    'created_at': job.created_at,
                    'completed_at': job.completed_at,
                    'result_file_path': job.result_file_path
                })
        
        return jsonify(create_success_response(
            data={
                'total': len(all_jobs),
                'results': all_jobs
            },
            message='Results list retrieved'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error listing results: {str(e)}")
        return jsonify(create_error_response(
            error='Listing error',
            details=str(e),
            error_code='LISTING_ERROR',
            status_code=500
        )), 500


@bp.route('/results/<job_id>/dashboard-pdf', methods=['GET'])
def download_dashboard_pdf(job_id):
    """Download dashboard as PDF report
    
    Args:
        job_id: Job ID
    
    Returns:
        PDF file download
    """
    try:
        from flask import send_file
        from backend.services.pdf_generator import PDFGenerator
        
        # Get job results
        success, job, message = processing_service.get_job(job_id)
        
        if not success or job is None:
            # Fallback to async processor
            async_processor = current_app.config.get('async_processor')
            if not async_processor:
                return jsonify(create_error_response(
                    error='Job not found',
                    details=message,
                    error_code='JOB_NOT_FOUND',
                    status_code=404
                )), 404
            
            async_status = async_processor.get_job_status(job_id)
            if not async_status.get('found'):
                return jsonify(create_error_response(
                    error='Job not found',
                    details='Job ID does not exist',
                    error_code='JOB_NOT_FOUND',
                    status_code=404
                )), 404
            
            # Build dashboard data from async job
            dashboard_data = {
                'statistics': async_status.get('validation_stats', {}),
                'issues': async_status.get('validation_issues', [])
            }
        else:
            # Build dashboard data from sync job
            if job.status != 'completed':
                return jsonify(create_error_response(
                    error='Job not completed',
                    details=f"Job status is '{job.status}'",
                    error_code='JOB_NOT_COMPLETED',
                    status_code=400
                )), 400
            
            dashboard_data = {
                'statistics': {
                    'total_records': job.input_rows or 0,
                    'total_columns': job.output_rows or 0,
                    'missing_values': 0,
                    'duplicate_rows': 0,
                    'quality_score': 95.0
                },
                'issues': []
            }
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_bytes = pdf_generator.generate_pdf(dashboard_data)
        
        # Create file-like object
        pdf_file = BytesIO(pdf_bytes)
        
        current_app.logger.info(f"Dashboard PDF generated for job: {job_id}")
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"dashboard_{job_id}.pdf"
        )
    
    except ImportError as e:
        current_app.logger.error(f"PDF generation libraries not installed: {str(e)}")
        return jsonify(create_error_response(
            error='PDF generation unavailable',
            details='Required libraries are not installed. Run: pip install reportlab matplotlib Pillow',
            error_code='PDF_UNAVAILABLE',
            status_code=503
        )), 503
    
    except Exception as e:
        current_app.logger.error(f"Error generating dashboard PDF: {str(e)}")
        return jsonify(create_error_response(
            error='PDF generation error',
            details=str(e),
            error_code='PDF_ERROR',
            status_code=500
        )), 500
