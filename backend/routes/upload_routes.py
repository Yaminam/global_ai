"""
File upload routes
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from backend.config import get_config
from backend.services.file_service import FileService
from utils.helpers import create_success_response, create_error_response, generate_uuid


bp = Blueprint('upload', __name__, url_prefix='/api')

# Initialize file service
config = get_config('development')
file_service = FileService(
    upload_folder=config.UPLOAD_FOLDER,
    max_file_size_bytes=config.MAX_FILE_SIZE_BYTES,
    allowed_extensions=config.ALLOWED_EXTENSIONS
)


@bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process a file
    
    Expected form data:
        - file: File upload
        - description: Optional description
        - category: Optional category
    
    Returns:
        JSON response with file metadata
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            current_app.logger.warning("Upload attempt without file")
            return jsonify(create_error_response(
                error='No file provided',
                details='Request must include a file in form data',
                error_code='NO_FILE',
                status_code=400
            )), 400
        
        file = request.files['file']
        
        # Check if file has a name
        if file.filename == '':
            current_app.logger.warning("Upload attempt with empty filename")
            return jsonify(create_error_response(
                error='No file selected',
                details='Selected file has no name',
                error_code='EMPTY_FILENAME',
                status_code=400
            )), 400
        
        # Validate file
        valid, message = file_service.validate_file(file)
        if not valid:
            current_app.logger.warning(f"File validation failed: {message}")
            return jsonify(create_error_response(
                error='File validation failed',
                details=message,
                error_code='VALIDATION_FAILED',
                status_code=400
            )), 400
        
        # Save file
        success, file_info, save_message = file_service.save_file(file)
        
        if not success:
            current_app.logger.error(f"File save failed: {save_message}")
            return jsonify(create_error_response(
                error='File save failed',
                details=save_message,
                error_code='SAVE_FAILED',
                status_code=500
            )), 500
        
        current_app.logger.info(f"File saved successfully: {file_info}")
        
        # Add additional info
        description = request.form.get('description', '')
        category = request.form.get('category', 'general')
        
        response_data = {
            'dataset_id': file_info.get('dataset_id'),
            'file_id': file_info.get('file_id'),
            'filename': file_info.get('original_filename'),
            'file_size_bytes': file_info.get('file_size'),
            'file_size_mb': file_info.get('file_size_mb'),
            'row_count': file_info.get('row_count'),
            'column_count': file_info.get('column_count'),
            'columns': file_info.get('columns'),
            'mime_type': file_info.get('mime_type'),
            'file_path': file_info.get('file_path'),
            'description': description,
            'category': category,
            'status': 'uploaded',
            'timestamp': file_info.get('upload_timestamp')
        }
        
        current_app.logger.info(f"Upload response data: {response_data}")
        
        return jsonify(create_success_response(
            data=response_data,
            message='File uploaded successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify(create_error_response(
            error='Unexpected error',
            details=str(e),
            error_code='UNEXPECTED_ERROR',
            status_code=500
        )), 500


@bp.route('/upload/multiple', methods=['POST'])
def upload_multiple_files():
    """Upload multiple files
    
    Expected form data:
        - files: Multiple file uploads
    
    Returns:
        JSON response with list of uploaded files metadata
    """
    try:
        if 'files' not in request.files:
            return jsonify(create_error_response(
                error='No files provided',
                details='Request must include files in form data',
                error_code='NO_FILES',
                status_code=400
            )), 400
        
        files = request.files.getlist('files')
        
        if len(files) == 0:
            return jsonify(create_error_response(
                error='No files selected',
                details='At least one file must be provided',
                error_code='EMPTY_FILES',
                status_code=400
            )), 400
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            if file.filename == '':
                failed_files.append({
                    'filename': 'unknown',
                    'error': 'Empty filename'
                })
                continue
            
            # Validate
            valid, message = file_service.validate_file(file)
            if not valid:
                failed_files.append({
                    'filename': file.filename,
                    'error': message
                })
                continue
            
            # Save
            success, file_info, save_message = file_service.save_file(file)
            
            if success:
                dataset_id = f"dataset-{generate_uuid()}"
                uploaded_files.append({
                    'dataset_id': dataset_id,
                    'file_id': file_info.get('file_id'),
                    'filename': file_info.get('filename'),
                    'file_size_bytes': file_info.get('file_size_bytes'),
                    'row_count': file_info.get('row_count'),
                    'column_count': file_info.get('column_count')
                })
            else:
                failed_files.append({
                    'filename': file.filename,
                    'error': save_message
                })
        
        current_app.logger.info(f"Batch upload completed: {len(uploaded_files)} successful, {len(failed_files)} failed")
        
        return jsonify(create_success_response(
            data={
                'uploaded': uploaded_files,
                'failed': failed_files,
                'summary': {
                    'total': len(files),
                    'successful': len(uploaded_files),
                    'failed': len(failed_files)
                }
            },
            message='Batch upload completed'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in batch upload: {str(e)}")
        return jsonify(create_error_response(
            error='Unexpected error',
            details=str(e),
            error_code='UNEXPECTED_ERROR',
            status_code=500
        )), 500
