FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "run_backend:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
