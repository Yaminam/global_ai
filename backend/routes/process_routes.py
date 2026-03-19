"""
Data processing routes
"""

from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import json

from backend.config import get_config
from backend.services.file_service import FileService
from backend.services.processing_service import ProcessingService
from utils.helpers import generate_uuid, get_timestamp, create_success_response, create_error_response


bp = Blueprint('process', __name__, url_prefix='/api')

# Initialize services
config = get_config('development')
file_service = FileService(
    upload_folder=config.UPLOAD_FOLDER,
    max_file_size_bytes=config.MAX_FILE_SIZE_BYTES,
    allowed_extensions=config.ALLOWED_EXTENSIONS
)
processing_service = ProcessingService(config.RESULTS_FOLDER)


@bp.route('/process', methods=['POST'])
def start_processing():
    """Start a data processing job
    
    Expected JSON body:
        - file_path: Path to file to process
        - config: Processing configuration
            - filters: Filter rules (optional)
            - transformations: Transformation rules (optional)
            - sorting: Sorting rules (optional)
        - async: Boolean - use async processing (optional, default: true)
    
    Returns:
        JSON response with job details
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            current_app.logger.warning("Process request without file_path")
            return jsonify(create_error_response(
                error='Missing parameters',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        config = data.get('config', {})
        dataset_id = data.get('dataset_id', f"dataset-{generate_uuid()}")
        use_async = data.get('async', True)  # Default to async
        
        # Load file
        success, df, load_message = file_service.load_file_data(file_path)
        
        if not success:
            current_app.logger.warning(f"Failed to load file for processing: {load_message}")
            return jsonify(create_error_response(
                error='File load failed',
                details=load_message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        job_id = f"job-{generate_uuid()}"
        
        # Check if we should use async processing
        if use_async and current_app.config.get('async_processor'):
            # Submit to async queue
            success = current_app.config['async_processor'].process_file_async(
                job_id, file_path, config
            )
            
            if not success:
                return jsonify(create_error_response(
                    error='Failed to queue job',
                    details='Unable to submit job to processing queue',
                    error_code='QUEUE_FAILED',
                    status_code=500
                )), 500
            
            current_app.logger.info(f"Async processing job queued: {job_id}")
            
            response_data = {
                'job_id': job_id,
                'dataset_id': dataset_id,
                'status': 'queued',
                'mode': 'async',
                'queue_position': current_app.config['async_queue'].get_queue_size(),
                'message': 'Job submitted to async queue',
                'check_status_at': f'/api/async/job/{job_id}'
            }
            
            return jsonify(create_success_response(
                data=response_data,
                message='Job queued for processing'
            )), 202  # Accepted (async processing)
        
        else:
            # Synchronous processing (original behavior)
            job = processing_service.create_job(dataset_id, config)
            
            success, processed_df, process_message = processing_service.process_dataframe(
                df, config, job.job_id
            )
            
            if not success:
                current_app.logger.warning(f"Processing failed: {process_message}")
                return jsonify(create_error_response(
                    error='Processing failed',
                    details=process_message,
                    error_code='PROCESSING_FAILED',
                    status_code=500
                )), 500
            
            # Save results
            result_success, result_path, result_message = processing_service.save_results(
                job.job_id, processed_df, 'json'
            )
            
            if result_success:
                processing_service.update_job_status(
                    job.job_id,
                    'completed',
                    result_file_path=result_path,
                    completed_at=get_timestamp()
                )
            
            job = processing_service.jobs[job.job_id]
            
            current_app.logger.info(f"Processing job completed: {job.job_id}")
            
            response_data = {
                'job_id': job.job_id,
                'dataset_id': job.dataset_id,
                'status': job.status,
                'mode': 'sync',
                'progress': {
                    'percentage': job.progress_percentage,
                    'input_rows': job.input_rows,
                    'processed_rows': job.processed_rows,
                    'output_rows': job.output_rows
                },
                'timestamps': {
                    'created_at': job.created_at,
                    'started_at': job.started_at,
                    'completed_at': job.completed_at
                },
                'result_file_path': job.result_file_path
            }
            
            return jsonify(create_success_response(
                data=response_data,
                message='Processing completed successfully'
            )), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in processing: {str(e)}")
        return jsonify(create_error_response(
            error='Processing error',
            details=str(e),
            error_code='PROCESSING_ERROR',
            status_code=500
        )), 500


@bp.route('/process/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get processing job status
    
    Args:
        job_id: Job ID
    
    Returns:
        JSON response with job status
    """
    try:
        success, job, message = processing_service.get_job(job_id)
        
        if not success or job is None:
            current_app.logger.warning(f"Job not found: {job_id}")
            return jsonify(create_error_response(
                error='Job not found',
                details=message,
                error_code='JOB_NOT_FOUND',
                status_code=404
            )), 404
        
        response_data = {
            'job_id': job.job_id,
            'dataset_id': job.dataset_id,
            'status': job.status,
            'progress': {
                'percentage': job.progress_percentage,
                'input_rows': job.input_rows,
                'processed_rows': job.processed_rows,
                'output_rows': job.output_rows
            },
            'timestamps': {
                'created_at': job.created_at,
                'started_at': job.started_at,
                'completed_at': job.completed_at
            },
            'error_message': job.error_message,
            'result_file_path': job.result_file_path
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Job status retrieved'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting job status: {str(e)}")
        return jsonify(create_error_response(
            error='Error retrieving job status',
            details=str(e),
            error_code='RETRIEVAL_ERROR',
            status_code=500
        )), 500


@bp.route('/process/sample-config', methods=['GET'])
def get_sample_config():
    """Get sample processing configuration
    
    Returns:
        JSON response with sample configurations
    """
    sample_configs = {
        'filter_example': {
            'filters': {
                'age': {'$gte': 18},
                'status': 'active',
                'salary': {'$lte': 100000}
            }
        },
        'transform_example': {
            'transformations': [
                {
                    'type': 'normalize',
                    'columns': ['salary', 'experience']
                },
                {
                    'type': 'drop_columns',
                    'columns': ['temp_column']
                },
                {
                    'type': 'rename',
                    'mapping': {'old_name': 'new_name'}
                }
            ]
        },
        'sort_example': {
            'sorting': {
                'salary': 'desc',
                'name': 'asc'
            }
        },
        'combined_example': {
            'filters': {
                'age': {'$gte': 21},
                'active': True
            },
            'transformations': [
                {
                    'type': 'drop_columns',
                    'columns': ['internal_id']
                }
            ],
            'sorting': {
                'salary': 'desc'
            }
        }
    }
    
    return jsonify(create_success_response(
        data=sample_configs,
        message='Sample processing configurations retrieved'
    )), 200


@bp.route('/process/operators', methods=['GET'])
def get_filter_operators():
    """Get available filter operators info
    
    Returns:
        JSON response with operator documentation
    """
    operators_info = {
        'comparison_operators': {
            '$gt': 'Greater than',
            '$gte': 'Greater than or equal',
            '$lt': 'Less than',
            '$lte': 'Less than or equal',
            '$eq': 'Equal',
            '$ne': 'Not equal',
            '$in': 'In array'
        },
        'transformation_types': {
            'normalize': 'Min-Max normalization on numeric columns',
            'aggregate': 'Group and aggregate data',
            'drop_columns': 'Remove specified columns',
            'rename': 'Rename columns'
        },
        'example_filter': {
            'age': {'$gte': 18},
            'salary': {'$lte': 100000},
            'status': 'active',
            'country': {'$in': ['USA', 'Canada']}
        }
    }
    
    return jsonify(create_success_response(
        data=operators_info,
        message='Filter operators and transformation types'
    )), 200
