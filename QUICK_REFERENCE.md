# Quick Reference Guide

## Commands Cheat Sheet

### Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend
cd backend && python app.py
```

### Frontend
```bash
# Serve static files
cd frontend
python -m http.server 8000

# Or use
npx http-server
```

### Testing
```bash
# Run unit tests
pytest tests/unit/

# Run all tests with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/unit/test_upload.py
```

### Code Quality
```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

### Database
```bash
# Initialize database
python backend/init_db.py

# Run migrations
flask db upgrade

# Create backup
cp storage/*.json backups/
```

---

## File Structure Quick Reference

```
sadul_globalai/
├── frontend/                    HTML, CSS, JavaScript UI
│   ├── index.html              Main entry point
│   ├── css/                    Stylesheets
│   └── js/                     JavaScript modules
│
├── backend/                     Flask API server
│   ├── app.py                  App bootstrap
│   ├── config.py               Configuration
│   ├── routes/                 API endpoints
│   ├── services/               Business logic
│   ├── models/                 Data structures
│   └── requirements.txt        Python dependencies
│
├── analytics/                   Data processing
│   ├── processors/             Algorithms
│   └── reports/                Report generation
│
├── utils/                       Shared utilities
│   ├── logger.py              Logging setup
│   ├── decorators.py          Custom decorators
│   └── validators.py          Validation schemas
│
├── storage/                     Data storage
│   ├── datasets/              Raw files
│   ├── processed/             Transformed data
│   ├── results/               Final results
│   └── cache/                 Temporary cache
│
└── docs/                        Documentation
    ├── ARCHITECTURE.md        Project structure
    ├── API_CONTRACT.md        API specifications
    ├── DATA_FLOW.md           Data flow diagrams
    ├── SCHEMA.md              Data schemas
    ├── DEPLOYMENT.md          Deployment guide
    └── SYSTEM_DESIGN.md       System architecture
```

---

## API Endpoint Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload file |
| POST | `/api/validate` | Validate data |
| POST | `/api/process` | Start processing |
| GET | `/api/status/{job_id}` | Check status |
| GET | `/api/results/{job_id}` | Get results |
| GET | `/api/analytics/{job_id}` | Get analytics |
| DELETE | `/api/jobs/{job_id}` | Cancel job |
| GET | `/health` | Health check |

---

## Common Workflows

### Upload and Process File
```
1. POST /api/upload
   ├─ Upload file
   └─ Get dataset_id

2. POST /api/validate
   ├─ Validate data
   └─ Check for issues

3. POST /api/process
   ├─ Start job
   └─ Get job_id

4. GET /api/status/{job_id}
   ├─ Poll for progress
   └─ Eventually get 100%

5. GET /api/results/{job_id}
   ├─ Retrieve processed data
   └─ Get result preview

6. GET /api/analytics/{job_id}
   ├─ Statistical analysis
   ├─ Anomaly detection
   └─ Trend analysis
```

---

## Environment Variables

Key variables in `.env`:

```
FLASK_ENV=development          Dev/prod mode
FLASK_DEBUG=True              Debug mode
STORAGE_PATH=./storage        Data storage location
MAX_FILE_SIZE_MB=1024         Max upload size
MAX_WORKERS=4                 Processing workers
JOB_TIMEOUT_MINUTES=60        Processing timeout
ENABLE_CORS=True              CORS support
RATE_LIMIT_ENABLED=True       Rate limiting
```

---

## Monitoring & Logs

```bash
# View logs
tail -f logs/app.log

# Check process status
ps aux | grep app.py

# Monitor resources
htop

# Check disk usage
du -sh storage/
```

---

## Data Storage Format

All data stored as JSON files:

- **Datasets:** `/storage/datasets/uuid.csv` (raw file)
- **Metadata:** `/storage/datasets/metadata.json` (file info)
- **Validation:** `/storage/results/validation-uuid.json`
- **Results:** `/storage/results/results-uuid.json`
- **Analytics:** `/storage/analytics/analytics-uuid.json`

---

## Error Troubleshooting

| Error | Solution |
|-------|----------|
| Port 5000 in use | Change port in config, or `lsof -i :5000` to find process |
| Import error | Run `pip install -r requirements.txt` |
| File too large | Increase `MAX_FILE_SIZE_MB` in config |
| Slow processing | Reduce `MAX_BATCH_SIZE`, enable streaming |
| Out of memory | Reduce workers, enable chunked processing |
| CORS error | Check `CORS_ORIGINS` in config |

---

## Performance Tips

1. **Enable caching** - Reduces redundant processing
2. **Use streaming** - For files >100MB
3. **Increase workers** - For high concurrency
4. **Archive old data** - Keep storage lean
5. **Use indexes** - If using database
6. **Monitor memory** - Watch for leaks
7. **Batch requests** - Group multiple operations

---

## Security Reminders

✓ Change SECRET_KEY in production
✓ Use HTTPS in production
✓ Enable API authentication
✓ Validate all inputs
✓ Implement rate limiting
✓ Log security events
✓ Regular backups
✓ Update dependencies

---

## Resources

- **API Docs:** See `docs/API_CONTRACT.md`
- **Data Flow:** See `docs/DATA_FLOW.md`
- **Deployment:** See `docs/DEPLOYMENT.md`
- **Architecture:** See `ARCHITECTURE.md`
- **Full README:** See `README.md`

---

**Last Updated:** March 18, 2026
**Version:** 1.0.0
