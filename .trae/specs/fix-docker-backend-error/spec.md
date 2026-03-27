# Fix Docker Backend Error Spec

## Why
The The backend container is failing to start due to code errors after removing voice/image upload features. The logs show errors related to missing voice router and static files mount.

## What Changes
- Fix `main.py` - remove voice router import and StaticFiles mount
- Fix `schemas.py` - remove voice-related schemas (if any)
- Fix `products.py` - remove image upload functionality
- Fix `posts.py` - remove media fields from posts/comments schemas

## Impact
- Affected specs: remove-upload-media
- Affected code: backend/app/main.py, backend/app/routers/voice.py, backend/app/services/voice_service.py, backend/app/routers/products.py, backend/app/schemas.py

## ADDED Requirements
None

## MODIFIED Requirements
None

## REMOVED Requirements
### Requirement: Voice Router
**Reason**: Voice feature has completely removed
**Migration**: Not needed - feature is deleted

### Requirement: Voice Service
**Reason**: Voice feature completely removed
**Migration**: Not needed - feature deleted

### Requirement: Image Upload in Products
**Reason**: Upload media feature removed from entire web app
**Migration**: Products now work without image_url field

### Requirement: Static Files Mount
**Reason**: No longer needed without uploads feature
**Migration**: Remove StaticFiles middleware

### Requirement: Voice Schemas
**Reason**: Voice feature removed
**Migration**: Remove voice-related schemas from schemas.py
