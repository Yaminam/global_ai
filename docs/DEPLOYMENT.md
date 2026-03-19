# Deployment Guide - Advanced Smart Data Processing Platform

## Deployment Environments

### 1. Local Development Environment

**Prerequisites:**
- Python 3.9+
- Git
- Text editor (VS Code, PyCharm, etc.)

**Steps:**
```bash
# Clone and navigate
git clone <repo-url>
cd sadul_globalai

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Run backend
cd backend
python app.py

# In another terminal, serve frontend
cd frontend
python -m http.server 8000
```

**Access:**
- Frontend: http://localhost:8000
- API: http://localhost:5000/api
- Health: http://localhost:5000/health

---

### 2. Docker Deployment

**Dockerfile for Backend:**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    image: node:16-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    ports:
      - "8000:8000"
    command: python -m http.server 8000

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sadul_globalai_backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
      - STORAGE_PATH=/app/storage
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    container_name: sadul_globalai_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:latest
    container_name: sadul_globalai_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./storage:/app/storage
    depends_on:
      - backend
      - frontend

volumes:
  redis_data:
```

**Deploy with Docker:**

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

### 3. Production Deployment (Linux/Ubuntu)

**Server Setup:**

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3.9 python3-pip nginx redis-server supervisor git

# Create application user
sudo useradd -m -s /bin/bash sadul_app

# Clone repository
cd /home/sadul_app
git clone <repo-url> sadul_globalai
cd sadul_globalai

# Setup Python environment
python3.9 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install gunicorn

# Create storage directories
mkdir -p storage/{datasets,processed,results,cache}
chmod 755 storage

# Create logs directory
mkdir -p logs
chmod 755 logs
```

**Nginx Configuration:**

```nginx
# /etc/nginx/sites-available/sadul_globalai
upstream backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 1024M;

    # Frontend
    location / {
        alias /home/sadul_app/sadul_globalai/frontend/;
        try_files $uri $uri.html =404;
    }

    # API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running jobs
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
    }

    # Static storage access
    location /storage {
        alias /home/sadul_app/sadul_globalai/storage/;
        autoindex off;
    }
}

# Redirect HTTP to HTTPS (optional)
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**Enable Nginx Site:**

```bash
sudo ln -s /etc/nginx/sites-available/sadul_globalai \
           /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl restart nginx
```

**Supervisor Configuration:**

```ini
# /etc/supervisor/conf.d/sadul_globalai.conf
[program:sadul_globalai]
directory=/home/sadul_app/sadul_globalai
command=/home/sadul_app/sadul_globalai/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    --access-logfile /home/sadul_app/sadul_globalai/logs/access.log \
    --error-logfile /home/sadul_app/sadul_globalai/logs/error.log \
    backend.app:app

user=sadul_app
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

**Start Service:**

```bash
sudo systemctl restart supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sadul_globalai
```

---

### 4. SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d yourdomain.com

# Update Nginx config
sudo nano /etc/nginx/sites-available/sadul_globalai
# Add SSL directives...

# Auto-renew certificates
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

**Updated Nginx with SSL:**

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Rest of configuration...
}
```

---

### 5. Monitoring and Maintenance

**Check Application Status:**

```bash
# Check process
sudo supervisorctl status sadul_globalai

# View logs
tail -f /home/sadul_app/sadul_globalai/logs/error.log
tail -f /home/sadul_app/sadul_globalai/logs/access.log

# Check disk usage
du -sh /home/sadul_app/sadul_globalai/storage

# Monitor system
htop
```

**Backup Strategy:**

```bash
#!/bin/bash
# Daily backup script
BACKUP_DIR="/backups/sadul_globalai"
APP_DIR="/home/sadul_app/sadul_globalai"

mkdir -p $BACKUP_DIR

# Backup storage
tar -czf $BACKUP_DIR/storage-$(date +%Y%m%d).tar.gz \
    $APP_DIR/storage

# Backup configuration
tar -czf $BACKUP_DIR/config-$(date +%Y%m%d).tar.gz \
    $APP_DIR/.env

# Keep last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

**Add to Crontab:**

```bash
crontab -e

# Add: 0 2 * * * /home/sadul_app/backup.sh
```

---

### 6. Scaling Considerations

**Horizontal Scaling:**

```yaml
# Load balancer configuration (HAProxy)
global
    log stdout local0
    maxconn 4096

defaults
    log     global
    mode    http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend main
    bind *:80
    default_backend servers

backend servers
    balance roundrobin
    server server1 192.168.1.10:5000
    server server2 192.168.1.11:5000
    server server3 192.168.1.12:5000
```

**Database Scaling:**

```ini
# PostgreSQL for production
DATABASE_URL=postgresql://user:password@db-server:5432/sadul_globalai

# Connection pooling
pool_size=20
max_overflow=40
```

**Cache Scaling:**

```python
# Multiple Redis nodes
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://redis1:6379',
            'redis://redis2:6379',
            'redis://redis3:6379',
        ]
    }
}
```

---

### 7. Environment-Specific Configurations

**Development (.env.development):**
```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///dev.db
```

**Staging (.env.staging):**
```
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://...staging...
SEND_ERROR_EMAILS=True
```

**Production (.env.production):**
```
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://...production...
SEND_ERROR_EMAILS=True
ENABLE_SENTRY=True
```

---

### 8. Troubleshooting Deployment

**Issue: High Memory Usage**
```bash
# Solution: Limit workers and batch size
GUNICORN_WORKERS=2
MAX_BATCH_SIZE=5000
```

**Issue: Slow File Uploads**
```bash
# Solution: Increase timeouts in Nginx
client_body_timeout 300s;
client_header_timeout 300s;
```

**Issue: Processing Jobs Timing Out**
```bash
# Solution: Use background job queue (Celery)
pip install celery redis
```

**Issue: Disk Space Running Out**
```bash
# Solution: Archive old results
find storage/results -mtime +30 -exec gzip {} \;
```

---

## Monitoring & Alerting

### Application Monitoring
```python
# Use tools like:
# - New Relic
# - DataDog
# - Prometheus + Grafana
```

### Log Aggregation
```bash
# Use ELK Stack:
# - Elasticsearch
# - Logstash
# - Kibana
```

### Uptime Monitoring
```bash
# Use services like:
# - Pingdom
# - StatusCake
# - UptimeRobot
```

---

## Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Update dependencies regularly
- [ ] Configure firewalls
- [ ] Set up rate limiting
- [ ] Enable logging/monitoring
- [ ] Regular backups
- [ ] Database encryption
- [ ] API authentication
- [ ] CORS restrictions
- [ ] Input validation
- [ ] Security headers
- [ ] Regular security audits

---

## Performance Optimization

1. **Database:** Use indexes, optimize queries
2. **Caching:** Redis for frequently accessed data
3. **CDN:** CloudFlare for static content
4. **Compression:** Enable gzip for responses
5. **Async:** Use background jobs for heavy tasks
6. **Monitoring:** Track and optimize slow endpoints

---

## Disaster Recovery

**Recovery Time Objective (RTO):** 4 hours
**Recovery Point Objective (RPO):** 1 hour

**Steps:**
1. Restore from latest backup
2. Verify data integrity
3. Update DNS records
4. Test all functionality
5. Monitor for issues

---

**Last Updated:** March 18, 2026
