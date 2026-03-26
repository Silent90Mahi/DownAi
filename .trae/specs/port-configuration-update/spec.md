# Port Configuration Update Spec

## Why
The project currently uses default ports (3000, 8000, 5432, 6379) that This needs to be changed to custom ports (6001-6003) for deployment flexibility and security, and to avoid port conflicts with other services on the server.

## What Changes
- Update all port references across the entire codebase
- Frontend: 3000 → 6001
- Backend API: 8000 → 6002
- PostgreSQL: 5432 → 6003
- Redis: 6379 → 6004

## Impact
- Affected specs: All network communication, deployment configuration
- Affected code: docker-compose.yml, frontend configuration, backend configuration, nginx configs, test files, documentation

## ADDED Requirements
### Requirement: Port Configuration
The system SHALL use configurable ports for all services to enable flexible deployment.

#### Scenario: Custom Port Configuration
- **WHEN** user deploys the application
- **THEN** all services must run on user-configured ports (6001, 6002, 6003, 6004)

## MODIFIED Requirements
### Requirement: Docker Compose Ports
All service ports in docker-compose.yml SHALL be updated to use new port mappings:
- Frontend: "3000:80" → "6001:80"
- Backend: "8000:8000" → "6002:8000"
- PostgreSQL: "5432:5432" → "6003:5432"
- Redis: "6379:6379" → "6004:6379"

### Requirement: Frontend API Configuration
The frontend SHALL connect to the backend API on port 6002.

### Requirement: Backend CORS Configuration
The backend CORS settings SHALL allow requests from frontend on port 6001.

### Requirement: Documentation Updates
All documentation and deployment guides SHALL reflect the new port configuration.
