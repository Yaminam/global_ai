# Advanced Smart Data Processing & Analytics API

A comprehensive REST API for data processing, validation, and analytics built with Flask.

## Features

- **File Upload**: Upload CSV, JSON, and Excel files with automatic metadata extraction
- **Data Validation**: Validate data against custom rules with regex patterns
- **Data Processing**: Filter, transform, and sort data with configurable pipelines
- **Results Management**: Retrieve and download processed results
- **Advanced Analytics**: Perform statistical analysis, anomaly detection, and trend analysis

## Project Structure

```
backend/
├── app.py                 # Flask application entry point
├── config.py             # Configuration management
├── models/               # Data models
│   └── data_models.py   # Dataclasses for entities
├── services/             # Business logic
│   ├── file_service.py          # File upload and handling
│   ├── validation_service.py    # Data validation
│   ├── processing_service.py    # Data processing
│   └── analytics_service.py     # Analytics operations
└── routes/              # API endpoints
    ├── upload_routes.py         # File upload endpoints
    ├── validate_routes.py       # Validation endpoints
    ├── process_routes.py        # Processing endpoints
    ├── results_routes.py        # Results endpoints
    └── analytics_routes.py      # Analytics endpoints

utils/
├── validators.py        # Regex validation utilities
├── helpers.py           # Helper functions
└── logger.py           # Logging configuration

uploads/                 # Uploaded files directory (created at runtime)
results/                 # Processing results directory (created at runtime)
logs/                   # Application logs directory (created at runtime)
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**:
```bash
cd sadul_globalai
```

2. **Create a virtual environment** (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r backend/requirements.txt
```

4. **Configure environment variables**:
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings (optional for development)
```

5. **Create required directories** (automatically created if missing):
```bash
mkdir -p uploads results logs
```

## Running the Server

### Development Mode
```bash
# Option 1: Using Flask CLI
export FLASK_ENV=development  # or set FLASK_ENV=development on Windows
python -m flask run

# Option 2: Using Python directly
python backend/app.py

# Option 3: Using Flask with custom settings
python -m flask run --host 0.0.0.0 --port 5000 --debug
```

### Production Mode
```bash
# Using Gunicorn (install with: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:create_app()

# Or with specific environment
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app('production')"
```

### With Specific Port
```bash
python -m flask run --port 8000
```

## API Endpoints

### Health & Info
- `GET /api/health` - Health check endpoint
- `GET /api/info` - API information and available endpoints

### File Upload
- `POST /api/upload` - Upload single file
- `POST /api/upload/multiple` - Upload multiple files

### Validation
- `POST /api/validate` - Validate data with rules
- `POST /api/validate/rules` - Validate with custom regex rules
- `POST /api/validate/profile` - Get data profile
- `GET /api/validate/sample-rules` - Get sample validation rules

### Processing
- `POST /api/process` - Start processing job
- `GET /api/process/<job_id>` - Get job status
- `GET /api/process/sample-config` - Get sample configurations
- `GET /api/process/operators` - Get filter operators info

### Results
- `GET /api/results/<job_id>` - Get results
- `GET /api/results/<job_id>/download` - Download results file
- `GET /api/results/<job_id>/stats` - Get result statistics
- `GET /api/results` - List all results

### Analytics
- `POST /api/analytics` - Perform analytics
- `GET /api/analytics/<job_id>` - Get analytics
- `GET /api/analytics/stats/<job_id>` - Get statistical analysis
- `GET /api/analytics/anomalies/<job_id>` - Get detected anomalies
- `GET /api/analytics/trends/<job_id>` - Get trend analysis
- `GET /api/analytics/insights/<job_id>` - Get AI-generated insights

## Example Usage

### 1. Upload a File
```bash
curl -X POST -F "file=@data.csv" \
  -F "description=Sales Data" \
  -F "category=finance" \
  http://localhost:5000/api/upload
```

### 2. Validate Data
```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/data.csv",
    "rules": {
      "email": "email",
      "phone": "phone",
      "date": "date"
    }
  }'
```

### 3. Process Data
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/data.csv",
    "config": {
      "filters": {
        "age": {"$gte": 18},
        "status": "active"
      },
      "sorting": {
        "salary": "desc"
      }
    }
  }'
```

### 4. Get Results
```bash
curl http://localhost:5000/api/results/job-xxx-xxx \
  -H "Content-Type: application/json"
```

### 5. Perform Analytics
```bash
curl -X POST http://localhost:5000/api/analytics \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/data.csv"
  }'
```

## Configuration

Configuration is managed through environment variables and the `backend/config.py` file:

### Key Settings
- `UPLOAD_FOLDER`: Directory for uploaded files (default: `./uploads`)
- `MAX_FILE_SIZE_BYTES`: Maximum file size in bytes (default: 100MB)
- `ALLOWED_EXTENSIONS`: Comma-separated file extensions (default: `csv,json,xlsx,xls,parquet`)
- `RESULTS_FOLDER`: Directory for results (default: `./results`)
- `LOGS_FOLDER`: Directory for logs (default: `./logs`)
- `DEBUG`: Enable debug mode (default: False in production)
- `CORS_ORIGINS`: CORS origins (default: `*`)

## Validation Rules

### Supported Data Types
- `email` - Email validation
- `phone` - Phone number validation
- `date` - Date validation (multiple formats)
- `url` - URL validation
- `credit_card` - Credit card validation
- `integer` - Integer validation
- `float` - Float validation
- `alphanumeric` - Alphanumeric validation

### Filter Operators
- `$gt` - Greater than
- `$gte` - Greater than or equal
- `$lt` - Less than
- `$lte` - Less than or equal
- `$eq` - Equal
- `$ne` - Not equal
- `$in` - In array

### Transformation Types
- `normalize` - Min-Max normalization
- `aggregate` - Group and aggregate
- `drop_columns` - Remove columns
- `rename` - Rename columns

## Logging

Logs are stored in the `logs/` directory:
- `app.log` - Application logs
- `error.log` - Error logs only
- JSON formatted for easy parsing

Log level can be configured via `LOG_LEVEL` environment variable:
- `DEBUG` - Detailed information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "error": "Error message",
  "details": "Detailed error description",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

## Performance Tips

1. **File Size**: Keep files under 100MB for optimal performance
2. **Row Limit**: Use `nrows` parameter to limit data loading
3. **Batch Processing**: Use `/api/upload/multiple` for multiple files
4. **Monitoring**: Check `logs/` directory for performance insights

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python -m flask run --port 8000
```

### File Too Large Error
- Increase `MAX_FILE_SIZE_BYTES` in `.env`
- Or split the file into smaller chunks

### Module Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r backend/requirements.txt
```

### Permission Errors
```bash
# Ensure write permissions for uploads and logs directories
chmod -R 755 uploads/ results/ logs/
```

## Dependencies

See `backend/requirements.txt` for complete list:
- Flask 2.3.0
- pandas 2.0.0
- numpy 1.24.0
- scikit-learn 1.2.0
- Flask-CORS 4.0.0
- python-dotenv 1.0.0
- Werkzeug 2.3.0
- openpyxl 3.1.0

## Support & Documentation

For detailed information about specific endpoints, use the `/api/info` endpoint or refer to the route files in `backend/routes/`.

## License

This project is part of the Advanced Smart Data Processing & Analytics Platform.

## Version History

- **v1.0.0** (Current) - Initial release with core features
  - File upload with metadata extraction
  - Data validation with regex patterns
  - Data processing with filtering, transformation, sorting
  - Results management
  - Analytics operations

## Future Enhancements

- Database persistence for jobs and results
- Scheduled processing tasks
- Advanced ML-based anomaly detection
- Real-time data streaming
- Multi-tenant support
- API authentication and authorization
