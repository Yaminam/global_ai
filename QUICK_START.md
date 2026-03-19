# Quick Start Guide - Running the Flask Backend

## Minimum Setup (3 steps)

### Step 1: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2: Start the Server
```bash
python backend/app.py
```

The server will start on `http://localhost:5000`

### Step 3: Test the Health Endpoint
```bash
# In a new terminal/command prompt
curl http://localhost:5000/api/health
```

You should see:
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:45",
    "version": "1.0.0",
    "environment": "development"
  },
  "message": "Service is healthy"
}
```

---

## Common Commands

### Check Server Status
```bash
curl http://localhost:5000/api/health
```

### View API Information
```bash
curl http://localhost:5000/api/info
```

### Upload a CSV File
```bash
# Sample with curl
curl -X POST \
  -F "file=@your_file.csv" \
  -F "description=My Data" \
  -F "category=sales" \
  http://localhost:5000/api/upload
```

### Stop the Server
- Press `Ctrl+C` in the terminal where the server is running

---

## Directory Structure Created at Runtime

After first run, these directories are automatically created:

```
sadul_globalai/
├── uploads/          # Your uploaded files
├── results/          # Processing results
└── logs/            # Application logs
    ├── app.log      # General logs
    └── error.log    # Error logs
```

---

## Environment Setup (Optional)

Create a `.env` file to customize settings:

```bash
FLASK_ENV=development
SERVER_PORT=5000
DEBUG=True
MAX_FILE_SIZE_MB=100
```

---

## Port in Use?

If port 5000 is already in use:

```bash
# Use a different port
python -m flask run --port 8000
```

Then access the server at `http://localhost:8000`

---

## Next Steps

1. **Upload a file**: Use `/api/upload`
2. **Validate data**: Use `/api/validate`
3. **Process data**: Use `/api/process`
4. **Get results**: Use `/api/results/<job_id>`
5. **Analytics**: Use `/api/analytics`

For detailed API documentation, see `BACKEND_README.md`

---

## Troubleshooting

### Module not found error?
```bash
pip install -r backend/requirements.txt
```

### Can't connect to server?
- Check if port 5000 is available
- Verify server is running: `curl http://localhost:5000/api/health`

### File upload fails?
- Check file size (max 100MB default)
- Verify file format is supported (csv, json, xlsx, xls, parquet)

---

## For Production Deployment

```bash
# Install Gunicorn
pip install gunicorn

# Run with production settings
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app('production')"
```

---

Last updated: 2024
