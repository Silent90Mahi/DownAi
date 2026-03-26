# Fix Admin Login Spec

## Why
Admin login fails with "Login failed. Please check your credentials." even when using correct credentials (admin@ooumphshg.com / password@123). This was caused by multiple bugs in the backend code.

## What Changes
- Fix typo `settings.ALgorithm` → `settings.ALGORITHM` in auth.py line 36
- Fix invalid enum `HierarchyLevel.DPD` → `HierarchyLevel.NONE` in auth.py line 327
- Increase phone column size from `String(15)` to `String(100)` in models.py to accommodate email-based admin identifier

## Impact
- Affected specs: Admin authentication
- Affected code: 
  - backend/app/routers/auth.py
  - backend/app/models.py
- Database: ALTER TABLE users ALTER COLUMN phone TYPE VARCHAR(100);

## Root Causes
1. **Typo in JWT token creation** (line 36): `settings.ALgorithm` should be `settings.ALGORITHM`
2. **Invalid enum value** (line 327): `HierarchyLevel.DPD` doesn't exist - only SHG, SLF, TLF, NONE are valid
3. **Phone column too short** (models.py line 55): 15 chars too short for email-based admin identifier (21 chars)

## ADDED Requirements
### Requirement: Admin Login JWT Token Creation
The system SHALL use the correct attribute name `ALGORITHM` when creating JWT tokens.

#### Scenario: Admin login succeeds
- **WHEN** admin submits correct credentials (admin@ooumphshg.com / password@123)
- **THEN** JWT token is successfully created and returned
- **AND** admin is authenticated and redirected to dashboard

### Requirement: Admin User Creation
The system SHALL use valid enum values for HierarchyLevel when creating admin user.

### Requirement: Phone Column Storage
The system SHALL support storing email addresses in the phone column for admin users (up to 100 characters).
