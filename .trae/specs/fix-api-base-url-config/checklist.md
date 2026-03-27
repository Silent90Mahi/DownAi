# Checklist

- [x] api.js uses `import.meta.env.VITE_API_BASE_URL` for baseURL
- [x] Fallback to `http://localhost:6002` is implemented when env variable is missing
- [x] All existing API exports (authAPI, productsAPI, etc.) remain unchanged
- [x] Request interceptor (auth token, FormData handling) remains unchanged
- [x] Response interceptor (401 error handling) remains unchanged
- [x] `.env.example` file created with `VITE_API_BASE_URL` configuration
- [x] Frontend `.env` file updated with correct `VITE_API_BASE_URL`
- [x] `.env.production.example` file created with production template
- [x] Dockerfile updated to support build-time `VITE_API_BASE_URL` injection
- [x] Code has no comments (as per project rules)
