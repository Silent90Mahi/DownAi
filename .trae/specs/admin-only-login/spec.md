# Admin-Only Login Spec

## Why
The application needs to be locked down to admin-only access with predefined credentials, removing all public registration capabilities for security and controlled access purposes.

## What Changes
- Remove all registration UI elements from Login.jsx
- Set default admin credentials (admin@ooumphshg.com / password@123)
- Disable registration API endpoints
- Create default admin user in database
- Implement auto-fill functionality for credentials
- Add validation for admin-only login

## Impact
- Affected specs: Authentication system, User management
- Affected code: 
  - frontend/src/components/Login.jsx
  - backend/app/routers/auth.py
  - backend/seed_database.py (or migration)

## ADDED Requirements

### Requirement: Admin-Only Authentication
The system SHALL only allow login with predefined admin credentials.

#### Scenario: Admin Login Success
- **WHEN** user enters admin@ooumphshg.com and password@123
- **THEN** user is authenticated and redirected to dashboard

#### Scenario: Invalid Credentials Rejected
- **WHEN** user enters any other credentials
- **THEN** login is rejected with error message

### Requirement: No Registration Access
The system SHALL completely disable all registration capabilities.

#### Scenario: Registration UI Removed
- **WHEN** user views login page
- **THEN** no registration options, links, or buttons are visible

#### Scenario: Registration API Disabled
- **WHEN** request is made to registration endpoints
- **THEN** request is rejected with 403 Forbidden

### Requirement: Default Credentials Auto-Fill
The system SHALL pre-populate login fields with admin credentials.

#### Scenario: First Login Attempt
- **WHEN** user clicks login for first time with empty fields
- **THEN** fields are auto-filled with admin credentials

## MODIFIED Requirements

### Requirement: Login Component
The Login.jsx component SHALL display only login functionality with pre-filled admin credentials and no registration options.

### Requirement: Authentication Endpoints
The auth router SHALL reject all registration requests and only authenticate the predefined admin user.

## REMOVED Requirements

### Requirement: Public User Registration
**Reason**: System is now admin-only
**Migration**: Existing users can still login but new registration is disabled
