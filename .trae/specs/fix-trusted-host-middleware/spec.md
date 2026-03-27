# Fix TrustedHostMiddleware for IP Address Access Spec

## Why
The backend is deployed with `ENVIRONMENT=production` which enables `TrustedHostMiddleware`. This middleware only allows specific hostnames (`ooumph.com`, `*.ooumph.com`, `localhost`) and blocks requests with IP address hosts like `135.222.42.174`, causing "Invalid host header" errors.

## What Changes
- Update `TrustedHostMiddleware` in `backend/app/main.py` to allow IP addresses in addition to hostnames
- Update `.env.docker` to use `ENVIRONMENT=development` for testing OR keep production with proper host configuration

## Impact
- Affected code: `backend/app/main.py`, `.env.docker`
- Affected functionality: Admin login, all API endpoints

## ADDED Requirements
### Requirement: IP Address Host Support
The system SHALL accept requests with IP address hosts in addition to domain names.

#### Scenario: Access via IP address
- **WHEN** user accesses the API via IP address (e.g., `http://135.222.42.174:6001`)
- **THEN** the request is processed without "Invalid host header" error

## MODIFIED Requirements
### Requirement: TrustedHostMiddleware Configuration
The TrustedHostMiddleware SHALL allow:
- Domain names: `ooumph.com`, `*.ooumph.com`
- Localhost: `localhost`, `127.0.0.1`
- Any IP address pattern for development/staging deployments
