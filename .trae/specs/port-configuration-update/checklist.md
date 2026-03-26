# Port Configuration Update Checklist

- [x] Checkpoint: Docker Compose ports updated
  - Frontend: "3000:80" → "6001:80"
  - Backend: "8000:8000" → "6002:8000"
  - PostgreSQL: "5432:5432" → "6003:5432"
  - Redis: "6379:6379" → "6004:6379"

- [x] Checkpoint: Frontend API base URL updated
  - Verify api.js uses: correct port (6002)
  - Verify Login.jsx uses new port
  - Verify TrustWallet.jsx uses new port
  - Verify ChatAssistant.jsx uses new port
  - Verify RealTimeProvider.jsx uses new port
  - Verify vite.config uses correct port
  - Verify nginx.conf uses correct port for API proxy
  - Verify backend CORS allows port 6001
  - Verify backend health check uses port 6002
  - Verify docker-compose.dev.yml uses port 6002
  - Verify documentation reflects new ports
  - Verify backend README.md reflects new ports
  - Verify frontend README.md reflects new ports
  - Verify DEPLOYMENT.md reflects new ports
  - Run build and verify services work correctly with new ports
  - Test all API endpoints respond correctly
  - Test frontend loads correctly
  - Test backend health check works
  - Test database connection works
  - Test Redis connection works
