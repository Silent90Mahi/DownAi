# Fix API Base URL Configuration Spec

## Why
The frontend's axios baseURL becomes empty string in production because the current logic checks for `window.location.hostname === 'localhost' && window.location.port === '5173'`, which fails in Docker deployment (port 6001). This causes API calls to hit the frontend domain instead of the backend (port 6002), resulting in failed requests.

## What Changes
- Replace hardcoded/conditional baseURL logic with Vite environment variables
- Use `import.meta.env.VITE_API_BASE_URL` for API base URL configuration
- Add fallback handling when env variable is missing
- Create `.env.development` and `.env.production` example files
- Ensure Docker deployment compatibility

## Impact
- Affected code: `frontend/src/services/api.js`, `frontend/.env*` files
- No changes to existing API structure (authAPI, productsAPI, etc.)
- No changes to interceptors (auth token, FormData handling, error handling)

## ADDED Requirements

### Requirement: Environment-Based API Base URL
The system SHALL use Vite environment variables to configure the API base URL instead of hardcoded conditional logic.

#### Scenario: Development environment
- **WHEN** running in development mode (`npm run dev`)
- **THEN** `VITE_API_BASE_URL` shall default to `http://localhost:6002`

#### Scenario: Production environment
- **WHEN** running in production (Docker deployment)
- **THEN** `VITE_API_BASE_URL` shall be set to `http://<SERVER_IP>:6002`

#### Scenario: Missing environment variable
- **WHEN** `VITE_API_BASE_URL` is not defined
- **THEN** system shall fall back to `http://localhost:6002` for safety

### Requirement: Backward Compatibility
The system SHALL maintain all existing API endpoints and interceptor functionality without modification.

#### Scenario: API endpoints preserved
- **WHEN** updating the axios configuration
- **THEN** all exported APIs (authAPI, chatAPI, productsAPI, ordersAPI, marketAPI, matchingAPI, suppliersAPI, trustAPI, communityAPI, paymentsAPI, analyticsAPI, notificationsAPI, reportsAPI) shall remain unchanged

#### Scenario: Interceptors preserved
- **WHEN** updating the axios configuration
- **THEN** request interceptor (auth token, FormData handling) and response interceptor (401 handling) shall remain unchanged
