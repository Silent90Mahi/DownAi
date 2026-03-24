# 🚀 Ooumph Backend Server - Startup Guide

## ✅ Phase 1 Complete - Security & Infrastructure

All critical security improvements have been implemented! The server is now ready to run with MNC-grade security features.

---

## 📋 Prerequisites

### ✅ Installed
- Python 3.9+
- All required dependencies (Redis, rate limiting, logging, monitoring)

### ⚠️ Required Setup (Before Starting)

**1. Set your OpenAI API Key in `.env`:**
```bash
cd backend
nano .env  # or use your preferred editor

# Find and update this line:
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# For better security, also generate a new SECRET_KEY:
# Run: openssl rand -hex 32
# Then update: SECRET_KEY=<generated-key>
```

**2. Optional - Install Redis for Rate Limiting & Caching:**
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis

# Or skip this - app will use in-memory storage (not recommended for production)
```

---

## 🎯 Starting the Server

### Development Mode
```bash
cd backend
python3 -m uvicorn app.main:app --reload
```

### Production Mode (with Gunicorn)
```bash
cd backend
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

---

## 🔍 Testing the Server

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Ooumph SHG Ecosystem",
  "version": "1.0.0",
  "environment": "development",
  "features": {
    "websocket": true,
    "cache": true,
    "rate_limiting": true
  }
}
```

### 2. API Documentation
Open in browser: http://localhost:8000/docs

### 3. Test CORS (should fail)
```bash
curl -H "Origin: http://malicious.com" http://localhost:8000/health
```
This should be blocked by CORS protection.

---

## 🔧 New Security Features

### ✅ Implemented

1. **Environment-Based Configuration**
   - All secrets loaded from `.env` file
   - No hardcoded secrets in code
   - Validation of critical settings

2. **Fixed CORS Configuration**
   - Only allows requests from configured frontend URL
   - Blocks unauthorized origins

3. **Structured Logging**
   - JSON format for production (parseable by log aggregators)
   - Text format for development
   - Configurable log levels

4. **Rate Limiting**
   - 60 requests per minute (configurable)
   - Per-IP and per-user limits
   - Redis-backed for distributed systems

5. **Security Headers**
   - TrustedHost middleware (production only)
   - GZip compression for responses

---

## 📊 Environment Variables

### Critical (Must Set)
```bash
SECRET_KEY=<generate-with-openssl-rand--hex-32>
OPENAI_API_KEY=<your-openai-api-key>
```

### Optional (For Features)
```bash
# Payment Gateway
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

# Government Portals
ONDC_API_KEY=
GEM_API_KEY=
ESARAS_API_KEY=

# Database (for production)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ooumph

# Redis (for rate limiting & caching)
REDIS_URL=redis://localhost:6379
```

---

## 🎛️ Configuration File: `.env`

The `.env` file has been created with development defaults. Before deploying to production:

1. **Generate secure SECRET_KEY:**
   ```bash
   openssl rand -hex 32
   ```

2. **Set your OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys

3. **Update FRONTEND_URL** if needed
   - Default: `http://localhost:5173`
   - Production: `https://your-frontend-domain.com`

4. **Set ENVIRONMENT=production**
   - This enables additional security features

---

## 🐛 Troubleshooting

### Server won't start?

**Check if port 8000 is already in use:**
```bash
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

**Import errors?**
```bash
# Reinstall dependencies
python3 -m pip install -r requirements.txt --force-reinstall
```

**Redis connection error?**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running:
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

---

## 📈 What's Next?

**Phase 2 Ready to Implement:**
- Database migration to PostgreSQL
- Add database indexes for performance
- Implement pagination
- Fix N+1 queries

**Would you like me to continue with Phase 2?**

---

## 🎉 Success Indicators

✅ Server starts without errors
✅ Health endpoint returns proper JSON
✅ Logs appear in structured format
✅ CORS blocks unauthorized origins
✅ API docs accessible at /docs

---

**Generated:** 2026-03-23
**Status:** Phase 1 Complete ✅
