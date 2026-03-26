# Deployment Guide

#Complete guide for deploying the Ooumph SHG Smart Market Linkage Platform.

## Prerequisites

- Docker 20.10+ and Docker Compose 1.0+
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
curl http://localhost:6002/health
curl http://localhost:6001/health
```

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
| `DATABASE_URL` | No | `postgresql://db:5432/ooumph_db` | Database connection URL (Docker) |
| `POSTGRES_DB` | No | `ooumph` | PostgreSQL database name |
| `POSTGRES_USER` | No | `ooumph` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password (change in production!) |

### Redis Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | `redis://redis:6379/0` | Redis connection URL (Docker) |

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
| `FRONTEND_URL` | No | `http://localhost:6001` | Frontend URL for CORS |
### Payment Gateway (Razorpay)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RAZORPAY_KEY_ID` | No | - | Razorpay Key ID |
    `RAZORPAY_KEY_SECRET` | No | - | Razorpay Key Secret |

## Docker Services
### Backend (FastAPI)
- **Image**: Python 3.9-slim
- **Port**: 6002
- **Workers**: 4 (Gunicorn + 1 UVicorn)
- **Health Check**: `/health` endpoint

- **Build**: Production Dockerfile
- **Environment**: From `.env.docker` file

### Frontend (React + Nginx)
- **Image**: Node 20-alpine
- **Port**: 6001
- **Build**: Production Dockerfile
- **Health Check**: `/health` endpoint
- **Environment**: `VITE_API_URL` from build args

### Database (PostgreSQL)
- **Image**: postgres:15-alpine
- **Port**: 6003 (internal: 5432)
- **Volume**: `postgres-data`
- **Health Check**: `pg_isready`

### Redis
- **Image**: redis:7-alpine
- **Port**: 6004 (internal: 6379)
- **Volume**: `redis-data`
- **Health Check**: `redis-cli ping`

## Useful Commands

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Services
```bash
docker-compose up -d --build
```

### Clean Start (with fresh database)
```bash
docker-compose down -v
docker-compose up -d --build
```

### Seed Database
```bash
docker exec ooumph-backend python /app/seed_database.py
```

## Accessing the Application
| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:6001 | 6001 |
| Backend API | http://localhost:6002 | 6002 |
| API Documentation | http://localhost:6002/docs | 6002 |
| PostgreSQL | localhost:6003 | 6003 |
| Redis | localhost:6004 | 6004 |

## Troubleshooting
### Database Connection Failed
```bash
docker-compose ps db
docker-compose logs db
docker-compose restart db
```
**Error**: `Connection refused to database`
**Solution**: Check database logs, restart database service

### Redis Connection Issues
```bash
docker-compose exec redis redis-cli ping
docker-compose restart redis
```
**Error**: `Redis connection error`
**Solution**: Check Redis logs, restart Redis service
### OpenAI API Errors
```bash
# Verify API key is active
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```
**Error**: `Invalid API key`
**Solution**: Verify `OPENAI_API_KEY` in `.env` and ensure API key is active at platform.openai.com
### Frontend Build Fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```
**Error**: `Build failed with errors`
**Solution**: Check build logs, fix errors in code
### Backend Container Crashes
```bash
docker-compose logs backend
docker-compose restart backend
```
**Error**: `Container exited immediately`
**Solution**: Check backend logs, restart backend service
### CORS Errors
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:6001" http://localhost:6002/api/auth/me
```
**Error**: `CORS policy blocked`
**Solution**: Set `FRONTEND_URL` correctly in `.env` (for production, set `ENVIRONMENT=production`)
### Port already in use
```bash
# Check if port is in use
lsof -i :6002 | kill -9 <PID>
docker-compose up -d
```
**Error**: `Port 6002 already in use`
**Solution**: Change the backend port in `docker-compose.yml` to `6003:6002` and restart.
### Volume Permission Issues
```bash
# Check permissions
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

### Clean up unused resources
```bash
docker system prune -a --volumes
```
