"""
Async processing routes for background job management
"""

from flask import Blueprint, request, jsonify, current_app
from utils.helpers import generate_uuid, create_success_response, create_error_response

bp = Blueprint('async_ops', __name__, url_prefix='/api/async')


@bp.route('/process', methods=['POST'])
def async_process():
    """Submit a file processing job to async queue
    
    Expected JSON body:
        - file_path: Path to file to process
        - config: Processing configuration
        
    Returns:
        JSON response with job ID and queue status (202 Accepted)
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing file_path',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        config = data.get('config', {})
        dataset_id = data.get('dataset_id', f"dataset-{generate_uuid()}")
        
        job_id = f"job-{generate_uuid()}"
        
        # Submit to async processor
        success = current_app.config['async_processor'].process_file_async(
            job_id, file_path, config
        )
        
        if not success:
            return jsonify(create_error_response(
                error='Failed to queue job',
                details='Processing queue is full or unavailable',
                error_code='QUEUE_FULL',
                status_code=503
            )), 503
        
        current_app.logger.info(f"Job queued: {job_id}")
        
        response_data = {
            'job_id': job_id,
            'dataset_id': dataset_id,
            'status': 'queued',
            'queue_size': current_app.config['async_queue'].get_queue_size(),
            'check_status_at': f'/api/async/status/{job_id}',
            'message': 'Job submitted to async queue'
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Job queued for processing'
        )), 202  # Accepted
    
    except Exception as e:
        current_app.logger.error(f"Error in async process: {str(e)}")
        return jsonify(create_error_response(
            error='Server error',
            details=str(e),
            error_code='SERVER_ERROR',
            status_code=500
        )), 500


@bp.route('/validate', methods=['POST'])
def async_validate():
    """Submit a validation job to async queue
    
    Expected JSON body:
        - file_path: Path to file to validate
        - rules: Validation rules (optional)
        
    Returns:
        JSON response with job ID (202 Accepted)
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing file_path',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        rules = data.get('rules', {})
        
        job_id = f"job-{generate_uuid()}"
        
        # Submit to async processor
        success = current_app.config['async_processor'].validate_file_async(
            job_id, file_path, rules
        )
        
        if not success:
            return jsonify(create_error_response(
                error='Failed to queue job',
                details='Processing queue is full',
                error_code='QUEUE_FULL',
                status_code=503
            )), 503
        
        current_app.logger.info(f"Validation job queued: {job_id}")
        
        response_data = {
            'job_id': job_id,
            'status': 'queued',
            'type': 'validation',
            'check_status_at': f'/api/async/status/{job_id}'
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Validation job queued'
        )), 202
    
    except Exception as e:
        current_app.logger.error(f"Error in async validate: {str(e)}")
        return jsonify(create_error_response(
            error='Server error',
            details=str(e),
            error_code='SERVER_ERROR',
            status_code=500
        )), 500


@bp.route('/analytics', methods=['POST'])
def async_analytics():
    """Submit an analytics job to async queue
    
    Expected JSON body:
        - file_path: Path to file to analyze
        
    Returns:
        JSON response with job ID (202 Accepted)
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing file_path',
                details='Request must include file_path',
                error_code='MISSING_PARAMS',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        job_id = f"job-{generate_uuid()}"
        
        # Submit to async processor
        success = current_app.config['async_processor'].analytics_async(job_id, file_path)
        
        if not success:
            return jsonify(create_error_response(
                error='Failed to queue job',
                details='Processing queue is full',
                error_code='QUEUE_FULL',
                status_code=503
            )), 503
        
        current_app.logger.info(f"Analytics job queued: {job_id}")
        
        response_data = {
            'job_id': job_id,
            'status': 'queued',
            'type': 'analytics',
            'check_status_at': f'/api/async/status/{job_id}'
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Analytics job queued'
        )), 202
    
    except Exception as e:
        current_app.logger.error(f"Error in async analytics: {str(e)}")
        return jsonify(create_error_response(
            error='Server error',
            details=str(e),
            error_code='SERVER_ERROR',
            status_code=500
        )), 500


@bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of an async job
    
    Args:
        job_id: Job ID
        
    Returns:
        JSON response with job status
    """
    try:
        status = current_app.config['async_processor'].get_job_status(job_id)
        
        if not status.get('found'):
            return jsonify(create_error_response(
                error='Job not found',
                details=f'Job {job_id} not found',
                error_code='JOB_NOT_FOUND',
                status_code=404
            )), 404
        
        return jsonify(create_success_response(
            data=status,
            message='Job status retrieved'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting job status: {str(e)}")
        return jsonify(create_error_response(
            error='Server error',
            details=str(e),
            error_code='SERVER_ERROR',
            status_code=500
        )), 500


@bp.route('/jobs', methods=['GET'])
def list_async_jobs():
    """List all active async jobs
    
    Returns:
        JSON response with jobs list
    """
    try:
        jobs = []
        for job_id, job_info in current_app.config['async_processor'].active_jobs.items():
            jobs.append({
                'job_id': job_id,
                **job_info
            })
        
        return jsonify(create_success_response(
            data={
                'total': len(jobs),
                'jobs': jobs
            },
            message='Active jobs list'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error listing jobs: {str(e)}")
        return jsonify(create_error_response(
            error='Server error',
            details=str(e),
            error_code='SERVER_ERROR',
            status_code=500
        )), 500


@bp.route('/queue/stats', methods=['GET'])
def get_queue_stats():
    """Get async queue statistics
    
    Returns:
        JSON response with queue stats
    """
    try:
        stats = current_app.config['async_queue'].get_stats()
        stats['timestamp'] = current_app.config['async_queue'].logger.info.__self__.__class__.__name__
        
        return jsonify(create_success_response(
            data=stats,
            message='Queue statistics'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting queue stats: {str(e)}")
        return jsonify(create_error_response(
            error='Server error',
            details=str(e),
            error_code='SERVER_ERROR',
            status_code=500
        )), 500
