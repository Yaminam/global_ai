# Backend Configuration - app.py

This is the main Flask application entry point. Configure settings here.

```python
# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import logging.config
import json
import os

# Configuration
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Setup logging
logging.config.fileConfig('logging_config.ini')
logger = logging.getLogger(__name__)

# Import blueprints (routes)
from routes import upload_bp, validation_bp, processing_bp, results_bp, analytics_bp

# Register blueprints
app.register_blueprint(upload_bp.bp, url_prefix='/api')
app.register_blueprint(validation_bp.bp, url_prefix='/api')
app.register_blueprint(processing_bp.bp, url_prefix='/api')
app.register_blueprint(results_bp.bp, url_prefix='/api')
app.register_blueprint(analytics_bp.bp, url_prefix='/api')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Bad Request",
        "details": str(error)
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": "Unauthorized",
        "details": "Missing or invalid authentication"
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Not Found",
        "details": "Resource not found"
    }), 404

@app.errorhandler(429)
def rate_limit(error):
    return jsonify({
        "success": False,
        "error": "Rate Limit Exceeded",
        "details": "Too many requests"
    }), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal Server Error",
        "details": "An unexpected error occurred",
        "request_id": request.headers.get('X-Request-ID')
    }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

# Main entry point
if __name__ == '__main__':
    debug = app.config.get('DEBUG', False)
    port = app.config.get('PORT', 5000)
    app.run(debug=debug, port=port)
```

## Backend Requirements

```
# backend/requirements.txt
Flask==2.3.0
Flask-CORS==4.0.0
numpy==1.24.0
pandas==2.0.0
scikit-learn==1.2.0
python-dotenv==1.0.0
requests==2.31.0
Werkzeug==2.3.0
```

## Configuration

```python
# backend/config.py
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    DEBUG = os.getenv('FLASK_DEBUG', False)
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Storage
    STORAGE_PATH = os.getenv('STORAGE_PATH', './storage')
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 1024))
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls', 'parquet'}
    
    # Processing
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    JOB_TIMEOUT_MINUTES = int(os.getenv('JOB_TIMEOUT_MINUTES', 60))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 10000))
    
    # Analytics
    ENABLE_ANOMALY_DETECTION = os.getenv('ENABLE_ANOMALY_DETECTION', 'True') == 'True'
    ENABLE_TREND_ANALYSIS = os.getenv('ENABLE_TREND_ANALYSIS', 'True') == 'True'
    
    # Security
    ENABLE_CORS = os.getenv('ENABLE_CORS', 'True') == 'True'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True') == 'True'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW_MINUTES = int(os.getenv('RATE_LIMIT_WINDOW_MINUTES', 1))
    
    # Session
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
```
