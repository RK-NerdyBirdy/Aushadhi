# Deployment Guide - Aushadhi Backend

## Production Deployment Checklist

### Pre-Deployment

- [ ] Set `DEBUG=False` in `.env`
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Update `DATABASE_URL` with production database
- [ ] Configure `BACKEND_CORS_ORIGINS` for your domain
- [ ] Update `ML_SERVICE_URL` if using ML service
- [ ] Setup SSL/TLS certificates
- [ ] Configure logging
- [ ] Setup monitoring and alerting

### Database Preparation

```bash
# Create production database
psql -U postgres
CREATE DATABASE aushadhi_prod;
CREATE USER aushadhi_user WITH PASSWORD 'strong_password';
ALTER ROLE aushadhi_user SET client_encoding TO 'utf8';
ALTER ROLE aushadhi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE aushadhi_user SET default_transaction_deferrable TO on;
ALTER ROLE aushadhi_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE aushadhi_prod TO aushadhi_user;
```

### Application Setup

#### 1. Clone and Install
```bash
git clone <repository> /app/aushadhi
cd /app/aushadhi
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Create Production .env
```env
# Application
APP_NAME=Aushadhi API
VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://aushadhi_user:strong_password@db.example.com:5432/aushadhi_prod
DB_ECHO=False

# Security
SECRET_KEY=your-random-secret-key-min-32-chars-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
BACKEND_CORS_ORIGINS=["https://app.example.com","https://admin.example.com"]

# ML Service
ML_SERVICE_URL=https://ml-service.example.com
ML_SERVICE_API_KEY=your-production-api-key

# Alerts
ALERT_CHECK_INTERVAL_SECONDS=3600
EXPIRY_WARNING_DAYS=90,60,30

# Pagination
DEFAULT_LIMIT=100
MAX_LIMIT=1000
```

#### 3. Run Database Migrations
```bash
alembic upgrade head
```

#### 4. Test Locally
```bash
python -m uvicorn app.main:app --port 8000
# Visit http://localhost:8000/docs
```

## Deployment Options

### Option 1: Gunicorn + Nginx

#### Install Gunicorn
```bash
pip install gunicorn
```

#### Create systemd service (`/etc/systemd/system/aushadhi.service`)
```ini
[Unit]
Description=Aushadhi API
After=network.target

[Service]
User=www-data
WorkingDirectory=/app/aushadhi
ExecStart=/app/aushadhi/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable aushadhi
sudo systemctl start aushadhi
sudo systemctl status aushadhi
```

#### Nginx Configuration (`/etc/nginx/sites-available/aushadhi`)
```nginx
upstream aushadhi_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    location / {
        proxy_pass http://aushadhi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/aushadhi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
```

#### Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: aushadhi_prod
      POSTGRES_USER: aushadhi_user
      POSTGRES_PASSWORD: strong_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://aushadhi_user:strong_password@db:5432/aushadhi_prod
      DEBUG: "False"
      SECRET_KEY: your-secret-key
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: always

volumes:
  postgres_data:
```

#### Deploy
```bash
docker-compose up -d
docker-compose logs -f api
```

### Option 3: Kubernetes

#### Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aushadhi-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aushadhi
  template:
    metadata:
      labels:
        app: aushadhi
    spec:
      containers:
      - name: api
        image: your-registry/aushadhi:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aushadhi-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: aushadhi-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Monitoring & Logging

### Setup Logging
```python
# Add to app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/aushadhi/app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor Application
```bash
# Check service status
systemctl status aushadhi

# View logs
journalctl -u aushadhi -f

# Monitor processes
htop | grep gunicorn
```

### Database Monitoring
```bash
# Connect to database
psql -U aushadhi_user -d aushadhi_prod

# Check connections
SELECT datname, usename, state FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('aushadhi_prod'));
```

## Backup Strategy

### Automated PostgreSQL Backups
```bash
#!/bin/bash
# /scripts/backup.sh

BACKUP_DIR="/backups/aushadhi"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="aushadhi_prod"
DB_USER="aushadhi_user"

mkdir -p $BACKUP_DIR

pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/aushadhi_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Cron Job
```cron
# Daily backup at 2 AM
0 2 * * * /scripts/backup.sh
```

## Performance Optimization

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_hospital_id ON medicine_info(hospital_id);
CREATE INDEX idx_stock_hospital_id ON hospital_stock(hospital_id);
CREATE INDEX idx_order_status ON orders(order_status);

-- Analyze tables
ANALYZE medicine_info;
ANALYZE hospital_stock;
```

### Application Optimization
- Use connection pooling
- Enable query result caching
- Setup CDN for static files
- Implement rate limiting

## Monitoring Checklist

- [ ] Setup application monitoring
- [ ] Configure database monitoring
- [ ] Setup error tracking (Sentry)
- [ ] Monitor API response times
- [ ] Track database query performance
- [ ] Setup uptime monitoring
- [ ] Configure alerts for issues
- [ ] Monitor disk usage
- [ ] Track log files

## Security Hardening

- [ ] Enable HTTPS/TLS
- [ ] Setup firewall rules
- [ ] Enable database encryption
- [ ] Implement rate limiting
- [ ] Setup DDoS protection
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Penetration testing

## Maintenance

### Regular Tasks
- Daily: Monitor logs and alerts
- Weekly: Review performance metrics
- Monthly: Database maintenance
- Quarterly: Security updates
- Annually: Full system review

### Update Procedures
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Test in staging first
pytest

# Deploy after testing
systemctl restart aushadhi
```

## Rollback Plan

```bash
# If issues occur:
1. Activate previous version
2. Run migrations rollback if needed
3. Verify functionality
4. Monitor for issues

# Alembic rollback
alembic downgrade -1  # Go back one version
```

## Support & Contact

For deployment assistance:
- Check `/var/log/aushadhi/app.log` for errors
- Review database migration logs
- Check Nginx error logs at `/var/log/nginx/error.log`

---

**Deployment Guide Version**: 1.0  
**Last Updated**: January 2026
