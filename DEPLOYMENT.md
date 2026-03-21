# Global AI - Advanced Analytics Platform

Deployment-ready full-stack analytics platform with:
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask with async processing
- **Analytics**: NumPy, Pandas, Scikit-learn
- **Reports**: PDF generation with ReportLab

## Quick Start

### Local Development
```bash
# Backend
python -m flask --app backend.app run --port 5000

# Frontend (new terminal)
cd frontend
python -m http.server 8000
```

### Deploy to Railway
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Railway auto-detects and deploys!

### Deploy to PythonAnywhere
1. Go to https://pythonanywhere.com
2. "Create new account"
3. Link GitHub repo
4. Configure web app with Flask
5. Deploy!

## Project Structure
```
├── frontend/          # HTML/CSS/JavaScript UI
├── backend/           # Flask API server
├── analytics/         # Data processing engines
├── storage/           # File uploads & results
├── requirements.txt   # Python dependencies
├── Procfile          # Deployment config
└── run_backend.py    # Entry point
```

## Features
- File upload (CSV, JSON, Excel)
- Data validation & cleaning
- Statistical analysis
- PDF report generation
- Async job processing
