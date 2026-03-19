"""
Backend Configuration Module
Environment-based settings for Flask application
"""

import os
from datetime import timedelta


class Config:
    """Base configuration - default settings"""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Storage paths
    STORAGE_PATH = os.getenv('STORAGE_PATH', './storage')
    UPLOAD_FOLDER = os.path.join(STORAGE_PATH, 'datasets')
    PROCESSED_FOLDER = os.path.join(STORAGE_PATH, 'processed')
    RESULTS_FOLDER = os.path.join(STORAGE_PATH, 'results')
    CACHE_FOLDER = os.path.join(STORAGE_PATH, 'cache')
    
    # File upload settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 1024))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls', 'parquet'}
    
    # Processing settings
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    JOB_TIMEOUT_MINUTES = int(os.getenv('JOB_TIMEOUT_MINUTES', 60))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 10000))
    ENABLE_STREAMING = os.getenv('ENABLE_STREAMING', 'True') == 'True'
    ENABLE_ASYNC = os.getenv('ENABLE_ASYNC', 'True') == 'True'
    
    # Analytics settings
    ENABLE_ANOMALY_DETECTION = os.getenv('ENABLE_ANOMALY_DETECTION', 'True') == 'True'
    ENABLE_TREND_ANALYSIS = os.getenv('ENABLE_TREND_ANALYSIS', 'True') == 'True'
    ENABLE_FORECASTING = os.getenv('ENABLE_FORECASTING', 'True') == 'True'
    
    # Security settings
    ENABLE_CORS = os.getenv('ENABLE_CORS', 'True') == 'True'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True') == 'True'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW_MINUTES = int(os.getenv('RATE_LIMIT_WINDOW_MINUTES', 1))
    
    # Session settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    LOG_DIR = os.getenv('LOG_DIR', './logs')
    
    # Cache settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True') == 'True'
    CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL_HOURS', 24))
    
    # Async Processing Configuration
    ASYNC_WORKERS = int(os.getenv('ASYNC_WORKERS', 4))
    ASYNC_QUEUE_MAX_SIZE = int(os.getenv('ASYNC_QUEUE_MAX_SIZE', 1000))
    ASYNC_CHUNK_SIZE = int(os.getenv('ASYNC_CHUNK_SIZE', 10000))
    
    # Data Storage Configuration
    STORAGE_DIR = os.path.join(STORAGE_PATH, 'persistent')
    STORAGE_RETENTION_DAYS = int(os.getenv('STORAGE_RETENTION_DAYS', 30))
    STORAGE_INDEX_ENABLED = os.getenv('STORAGE_INDEX_ENABLED', 'True') == 'True'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration object for given environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config_dict.get(env, config_dict['default'])
