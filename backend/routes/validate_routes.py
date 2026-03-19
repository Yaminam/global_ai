"""
Data validation routes
"""

from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import json

from backend.config import get_config
from backend.services.file_service import FileService
from backend.services.validation_service import ValidationService
from utils.validators import DataValidator
from utils.helpers import generate_uuid, get_timestamp, create_success_response, create_error_response


bp = Blueprint('validate', __name__, url_prefix='/api')

# Initialize services
config = get_config('development')
file_service = FileService(
    upload_folder=config.UPLOAD_FOLDER,
    max_file_size_bytes=config.MAX_FILE_SIZE_BYTES,
    allowed_extensions=config.ALLOWED_EXTENSIONS
)
validation_service = ValidationService()


@bp.route('/validate', methods=['POST'])
def validate_data():
    """Validate uploaded data
    
    Expected JSON body:
        - file_path: Path to uploaded file
        - rules: Optional validation rules (dict mapping column names to validation rules)
    
    Returns:
        JSON response with validation results
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            current_app.logger.warning("Validation request without file_path")
            return jsonify(create_error_response(
                error='Missing file path',
                details='Request must include file_path in JSON body',
                error_code='MISSING_FILE_PATH',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        rules = data.get('rules', {})
        
        # Load file
        success, df, load_message = file_service.load_file_data(file_path)
        
        if not success:
            current_app.logger.warning(f"Failed to load file for validation: {load_message}")
            return jsonify(create_error_response(
                error='File load failed',
                details=load_message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        # Validate data
        validation_result = validation_service.validate_dataframe(df, rules)
        
        current_app.logger.info(f"Data validation completed: {validation_result.total_rows} rows, "
                               f"{validation_result.valid_rows} valid")
        
        response_data = {
            'validation_id': validation_result.validation_id,
            'dataset_id': validation_result.dataset_id,
            'file_path': file_path,
            'status': validation_result.status,
            'summary': {
                'total_rows': validation_result.total_rows,
                'valid_rows': validation_result.valid_rows,
                'invalid_rows': validation_result.invalid_rows,
                'valid_percentage': round((validation_result.valid_rows / validation_result.total_rows * 100), 2)
            },
            'issues': validation_result.issues,
            'timestamp': validation_result.created_at
        }
        
        return jsonify(create_success_response(
            data=response_data,
            message='Data validation completed successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in validation: {str(e)}")
        return jsonify(create_error_response(
            error='Validation error',
            details=str(e),
            error_code='VALIDATION_ERROR',
            status_code=500
        )), 500


@bp.route('/validate/rules', methods=['POST'])
def validate_with_custom_rules():
    """Validate data with custom regex rules
    
    Expected JSON body:
        - file_path: Path to uploaded file
        - column_rules: Dict mapping column names to validation types
    
    Returns:
        JSON response with validation results
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
        
        file_path = data.get('file_path')
        column_rules = data.get('column_rules', {})
        
        # Load file
        success, df, load_message = file_service.load_file_data(file_path)
        
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=load_message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        # Get quick profile summary (fast)
        profile = validation_service.get_data_profile(df)
        
        current_app.logger.info(f"Quick validation: {len(df)} rows, {len(df.columns)} columns")
        
        return jsonify(create_success_response(
            data={
                'total_rows': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'data_types': profile['data_types'],
                'columns_detail': profile['columns'],
                'missing_values': profile['missing_values']
            },
            message='Quick validation completed'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in custom rule validation: {str(e)}")
        return jsonify(create_error_response(
            error='Validation error',
            details=str(e),
            error_code='VALIDATION_ERROR',
            status_code=500
        )), 500


@bp.route('/validate/profile', methods=['POST'])
def get_data_profile():
    """Get comprehensive data profile
    
    Expected JSON body:
        - file_path: Path to uploaded file
    
    Returns:
        JSON response with detailed data profile
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify(create_error_response(
                error='Missing file path',
                details='Request must include file_path',
                error_code='MISSING_FILE_PATH',
                status_code=400
            )), 400
        
        file_path = data.get('file_path')
        
        # Load file
        success, df, load_message = file_service.load_file_data(file_path)
        
        if not success:
            return jsonify(create_error_response(
                error='File load failed',
                details=load_message,
                error_code='LOAD_FAILED',
                status_code=400
            )), 400
        
        # Get profile
        profile = validation_service.get_data_profile(df)
        
        current_app.logger.info(f"Data profile generated for {len(df)} rows, {len(df.columns)} columns")
        
        return jsonify(create_success_response(
            data=profile,
            message='Data profile retrieved successfully'
        )), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in data profile: {str(e)}")
        return jsonify(create_error_response(
            error='Profile error',
            details=str(e),
            error_code='PROFILE_ERROR',
            status_code=500
        )), 500


@bp.route('/validate/sample-rules', methods=['GET'])
def get_sample_rules():
    """Get sample validation rules
    
    Returns:
        JSON response with sample validation rules
    """
    sample_rules = {
        'email_validation': {
            'email': 'email',
            'backup_email': 'email'
        },
        'contact_validation': {
            'phone': 'phone',
            'mobile': 'phone'
        },
        'date_validation': {
            'date_of_birth': 'date',
            'registration_date': 'date'
        },
        'url_validation': {
            'website': 'url',
            'profile_link': 'url'
        },
        'financial_validation': {
            'credit_card': 'credit_card',
            'amount': 'float'
        },
        'mixed_validation': {
            'email': 'email',
            'phone': 'phone',
            'age': 'integer',
            'salary': 'float',
            'website': 'url',
            'name': 'alphanumeric'
        }
    }
    
    return jsonify(create_success_response(
        data=sample_rules,
        message='Sample validation rules retrieved'
    )), 200
