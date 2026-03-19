"""
Flask application entry point
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import atexit

from backend.config import get_config
from utils.logger import setup_logging
from utils.helpers import create_success_response, create_error_response
from backend.services.async_queue import initialize_async_queue
from backend.services.data_storage import DataStorage
from backend.services.async_processor import AsyncProcessor


def create_app(env='development'):
    """Create and configure Flask application
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(env)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize async job queue
    num_workers = config.ASYNC_WORKERS if hasattr(config, 'ASYNC_WORKERS') else 4
    async_queue = initialize_async_queue(num_workers=num_workers, logger=app.logger)
    async_queue.start()
    
    # Store queue in app context for access in routes
    app.config['async_queue'] = async_queue
    
    # Initialize data storage
    storage_dir = config.STORAGE_DIR if hasattr(config, 'STORAGE_DIR') else './storage'
    data_storage = DataStorage(storage_dir, logger=app.logger)
    app.config['data_storage'] = data_storage
    
    # Initialize async processor
    async_processor = AsyncProcessor(async_queue, data_storage, logger=app.logger)
    app.config['async_processor'] = async_processor
    
    # Cleanup function to stop async queue on shutdown
    def shutdown_async_queue():
        app.logger.info("Shutting down async queue...")
        async_queue.stop()
        app.logger.info("Async queue stopped")
    
    atexit.register(shutdown_async_queue)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    from backend.routes import upload_routes, validate_routes, process_routes, results_routes, analytics_routes, async_routes
    
    app.register_blueprint(upload_routes.bp)
    app.register_blueprint(validate_routes.bp)
    app.register_blueprint(process_routes.bp)
    app.register_blueprint(results_routes.bp)
    app.register_blueprint(analytics_routes.bp)
    app.register_blueprint(async_routes.bp)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request"""
        return jsonify(create_error_response(
            error='Bad Request',
            details=str(error),
            error_code='BAD_REQUEST',
            status_code=400
        )), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found"""
        return jsonify(create_error_response(
            error='Not Found',
            details=f"Endpoint {request.path} not found",
            error_code='NOT_FOUND',
            status_code=404
        )), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed"""
        return jsonify(create_error_response(
            error='Method Not Allowed',
            details=f"Method {request.method} not allowed on {request.path}",
            error_code='METHOD_NOT_ALLOWED',
            status_code=405
        )), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify(create_error_response(
            error='Internal Server Error',
            details='An unexpected error occurred',
            error_code='INTERNAL_ERROR',
            status_code=500
        )), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large"""
        return jsonify(create_error_response(
            error='Request Entity Too Large',
            details='File size exceeds maximum allowed limit',
            error_code='FILE_TOO_LARGE',
            status_code=413
        )), 413
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - welcome and info"""
        return jsonify(create_success_response(
            data={
                'message': 'Welcome to Advanced Data Processing & Analytics API',
                'version': '1.0.0',
                'environment': env,
                'info_url': '/api/info',
                'health_url': '/api/health',
                'status': 'running'
            },
            message='API is running'
        )), 200

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify(create_success_response(
            data={
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'environment': env
            },
            message='Service is healthy'
        )), 200
    
    # Info endpoint
    @app.route('/api/info', methods=['GET'])
    def info():
        """API information endpoint"""
        return jsonify(create_success_response(
            data={
                'name': 'Advanced Data Processing & Analytics API',
                'version': '1.0.0',
                'environment': env,
                'endpoints': {
                    'upload': '/api/upload (POST)',
                    'validate': '/api/validate (POST)',
                    'process': '/api/process (POST)',
                    'results': '/api/results/<job_id> (GET)',
                    'analytics': '/api/analytics/<job_id> (GET)',
                    'health': '/api/health (GET)',
                    'info': '/api/info (GET)',
                    'async_stats': '/api/async/stats (GET)',
                    'async_queue': '/api/async/queue (GET)'
                }
            },
            message='API information'
        )), 200
    
    # Async job status endpoint
    @app.route('/api/async/job/<job_id>', methods=['GET'])
    def get_async_job_status(job_id):
        """Get async job status
        
        Args:
            job_id: Job ID
        
        Returns:
            JSON response with job status
        """
        status = app.config['async_processor'].get_job_status(job_id)
        
        return jsonify(create_success_response(
            data=status,
            message='Job status retrieved'
        )), 200
    
    # Async statistics endpoint
    @app.route('/api/async/stats', methods=['GET'])
    def get_async_stats():
        """Get async processing statistics"""
        stats = app.config['async_processor'].get_processing_stats()
        
        return jsonify(create_success_response(
            data=stats,
            message='Processing statistics'
        )), 200
    
    # Queue status endpoint
    @app.route('/api/async/queue', methods=['GET'])
    def get_queue_status():
        """Get job queue status"""
        stats = {
            'queue_size': app.config['async_queue'].get_queue_size(),
            'stats': app.config['async_queue'].get_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(create_success_response(
            data=stats,
            message='Queue status retrieved'
        )), 200
    
    # Storage statistics endpoint
    @app.route('/api/storage/stats', methods=['GET'])
    def get_storage_stats():
        """Get data storage statistics"""
        stats = app.config['data_storage'].get_storage_stats()
        
        return jsonify(create_success_response(
            data=stats,
            message='Storage statistics'
        )), 200
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests"""
        app.logger.info(f"{request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses"""
        app.logger.info(f"{request.method} {request.path} - {response.status_code}")
        return response
    
    return app


if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(debug=env == 'development', host='0.0.0.0', port=5000)
