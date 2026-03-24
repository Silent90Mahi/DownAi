# Deployment Guide

Complete guide for deploying the Ooumph SHG Smart Market Linkage Platform.

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- OpenAI API Key (for AI agent features)
- Domain name (optional, for production)
- SSL certificate (optional, for production HTTPS)
- 4GB+ RAM recommended
- 20GB+ disk space

## Quick Start

### 1. Clone and Configure

```bash
git clone <repository-url>
cd downAi
cp .env.example .env
```

### 2. Set Required Environment Variables

Edit `.env` and set at minimum:

```bash
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Verify Deployment

```bash
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000/health
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

### Core Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for AI agents |
| `SECRET_KEY` | Yes | - | JWT secret key (generate with `openssl rand -hex 32`) |
| `ENVIRONMENT` | No | `development` | Environment: `development` or `production` |
| `DEBUG` | No | `true` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./ooumph.db` | Database connection URL |
| `POSTGRES_DB` | No | `ooumph` | PostgreSQL database name |
| `POSTGRES_USER` | No | `ooumph` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password (change in production!) |

### Redis Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection URL |

### Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token expiration (24 hours) |

### OpenAI Models

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_MODEL` | No | `gpt-4o` | Chat model |
| `OPENAI_WHISPER_MODEL` | No | `whisper-1` | Speech-to-text model |
| `OPENAI_TTS_MODEL` | No | `tts-1` | Text-to-speech model |
| `OPENAI_TTS_VOICE` | No | `alloy` | TTS voice |

### CORS Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FRONTEND_URL` | No | `http://localhost:5173` | Frontend URL for CORS |

### Payment Gateway (Razorpay)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RAZORPAY_KEY_ID` | No | - | Razorpay key ID |
| `RAZORPAY_KEY_SECRET` | No | - | Razorpay key secret |

### Government API Integrations

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEM_API_KEY` | No | - | GeM Portal API key |
| `GEM_API_URL` | No | - | GeM Portal API URL |
| `ONDC_API_KEY` | No | - | ONDC API key |
| `ONDC_API_URL` | No | - | ONDC API URL |
| `ESARAS_API_KEY` | No | - | eSARAS API key |
| `ESARAS_API_URL` | No | - | eSARAS API URL |

### Feature Flags

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_MOCK_DATA` | No | `true` | Use mock data for APIs |
| `ENABLE_WEBSOCKET` | No | `true` | Enable WebSocket support |
| `ENABLE_CACHE` | No | `true` | Enable Redis caching |
| `CACHE_TTL` | No | `3600` | Cache TTL in seconds |
| `ENABLE_VOICE_AGENT` | No | `true` | Enable voice features |
| `ENABLE_TRUST_COINS` | No | `true` | Enable trust coins |
| `ENABLE_BULK_ORDERING` | No | `true` | Enable bulk ordering |
| `ENABLE_NEGOTIATION` | No | `true` | Enable AI negotiation |

### Rate Limiting

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | No | `true` | Enable rate limiting |
| `RATE_LIMIT_PER_MINUTE` | No | `60` | Requests per minute |

### File Upload

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAX_UPLOAD_SIZE` | No | `10485760` | Max upload size (10MB) |
| `UPLOAD_DIR` | No | `./uploads` | Upload directory |

## Docker Services

### Backend (FastAPI)

- **Image**: Python 3.9-slim
- **Port**: 8000
- **Workers**: 4 (Gunicorn + Uvicorn)
- **Health Check**: `/health` endpoint

```bash
docker-compose up -d backend
docker-compose logs -f backend
```

### Frontend (React + Nginx)

- **Image**: Node 20-alpine + Nginx
- **Port**: 3000 (maps to Nginx port 80)
- **Build**: Vite production build
- **Health Check**: `/health` endpoint

```bash
docker-compose up -d frontend
docker-compose logs -f frontend
```

### Database (PostgreSQL)

- **Image**: postgres:15-alpine
- **Port**: 5432
- **Volume**: `postgres-data`

```bash
docker-compose up -d db
docker-compose exec db psql -U ooumph -d ooumph
```

### Redis

- **Image**: redis:7-alpine
- **Port**: 6379
- **Persistence**: AOF enabled

```bash
docker-compose up -d redis
docker-compose exec redis redis-cli ping
```

## Production Deployment

### SSL Configuration

#### Option 1: Nginx Reverse Proxy with Let's Encrypt

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Option 2: Traefik with Auto SSL

```yaml
version: '3.8'
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "443:443"
    volumes:
      - ./letsencrypt:/letsencrypt
```

### Scaling

#### Horizontal Scaling with Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml ooumph
docker service scale ooumph_backend=3
```

#### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ooumph-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ooumph-backend
  template:
    spec:
      containers:
      - name: backend
        image: ooumph-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ooumph-secrets
              key: database-url
```

### Monitoring

#### Prometheus + Grafana Stack

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### Health Check Monitoring

```bash
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

### Backup Strategy

#### Database Backup

```bash
docker-compose exec db pg_dump -U ooumph ooumph > backup_$(date +%Y%m%d).sql
```

#### Automated Daily Backups

```bash
0 2 * * * docker-compose exec -T db pg_dump -U ooumph ooumph | gzip > /backups/ooumph_$(date +\%Y\%m\%d).sql.gz
```

#### Restore from Backup

```bash
gunzip -c backup.sql.gz | docker-compose exec -T db psql -U ooumph ooumph
```

### Security Hardening

1. **Change Default Passwords**
   ```bash
   POSTGRES_PASSWORD=$(openssl rand -base64 32)
   SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Enable Firewall**
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

3. **Limit Resource Usage**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

## Development Deployment

### Using Docker Compose Dev

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Local Development Without Docker

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error**: `Connection refused to database`

**Solution**:
```bash
docker-compose ps db
docker-compose logs db
docker-compose restart db
```

#### 2. Redis Connection Issues

**Error**: `Redis connection error`

**Solution**:
```bash
docker-compose exec redis redis-cli ping
docker-compose restart redis
```

#### 3. OpenAI API Errors

**Error**: `Invalid API key`

**Solution**:
- Verify `OPENAI_API_KEY` in `.env`
- Check API key is active at platform.openai.com
- Ensure sufficient API credits

#### 4. Frontend Build Fails

**Error**: `Build failed with errors`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 5. Backend Container Crashes

**Error**: `Container exited immediately`

**Solution**:
```bash
docker-compose logs backend
docker-compose exec backend python -c "from app.main import app"
```

#### 6. CORS Errors

**Error**: `CORS policy blocked`

**Solution**:
- Set `FRONTEND_URL` correctly in `.env`
- For development, set `ENVIRONMENT=development`

#### 7. Port Already in Use

**Error**: `Port 8000 already in use`

**Solution**:
```bash
lsof -i :8000
kill -9 <PID>
docker-compose up -d
```

#### 8. Volume Permission Issues

**Error**: `Permission denied` on volumes

**Solution**:
```bash
sudo chown -R $USER:$USER ./backend/uploads
docker-compose down -v
docker-compose up -d
```

### Log Analysis

```bash
docker-compose logs -f --tail=100 backend
docker-compose logs -f --tail=100 frontend
docker-compose logs -f --tail=100 db
```

### Reset Everything

```bash
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

## Maintenance

### Update Images

```bash
docker-compose pull
docker-compose up -d
```

### View Resource Usage

```bash
docker stats
```

### Clean Up Unused Resources

```bash
docker system prune -a --volumes
```
