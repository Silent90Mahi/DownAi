# Remove Upload Media Feature Spec

## Why
The upload media feature (images and audio/voice) is causing permission errors and adds unnecessary complexity. Removing it will simplify the application and eliminate the `PermissionError: [Errno 13] Permission denied: 'uploads/audio'` error.

## What Changes
- Remove voice/audio transcription and synthesis (Agent Vaani voice features)
- Remove image upload functionality from products
- Remove image/video fields from posts and comments
- Remove profile image support
- Remove static file serving for uploads
- Remove uploads directory creation

## Impact
- Affected specs: Agent Vaani voice interface
- Affected code: 
  - Backend: main.py, voice.py, voice_service.py, products.py, posts.py, models.py, schemas.py
  - Frontend: VoiceButton.jsx, VoiceInputOverlay.jsx, AudioFeedback.jsx, SellProduct.jsx, ProductEdit.jsx, ChatAssistant.jsx, api.js

## ADDED Requirements

### Requirement: Remove Voice Features
The system SHALL remove all voice/audio features including:
- Voice transcription endpoint (`/api/voice/transcribe`)
- Voice synthesis endpoint (`/api/voice/synthesize`)
- Voice service module
- Voice-related frontend components

### Requirement: Remove Image Upload
The system SHALL remove all image upload features including:
- Product image upload
- Post images and video URLs
- Comment image URLs
- Profile images
- Static file serving for uploads

### Requirement: Remove Uploads Directory
The system SHALL remove the uploads directory creation and static file mounting from main.py

## REMOVED Requirements

### Requirement: Agent Vaani Voice Interface
**Reason**: Voice features causing permission errors and adding complexity
**Migration**: Users will use text input only

### Requirement: Image Upload for Products
**Reason**: Simplifying product creation flow
**Migration**: Products will be created without images

### Requirement: Media in Posts/Comments
**Reason**: Simplifying community features
**Migration**: Posts and comments will be text-only
