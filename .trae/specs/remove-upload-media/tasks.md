# Tasks

## Backend Tasks

- [ ] Task 1: Remove voice router and service from backend
  - [ ] SubTask 1.1: Delete `/backend/app/routers/voice.py`
  - [ ] SubTask 1.2: Delete `/backend/app/services/voice_service.py`
  - [ ] SubTask 1.3: Remove voice router import from main.py
  - [ ] SubTask 1.4: Remove voice-related schemas from schemas.py

- [ ] Task 2: Remove image upload from products router
  - [ ] SubTask 2.1: Remove UploadFile, File imports from products.py
  - [ ] SubTask 2.2: Remove image parameter from create_product endpoint
  - [ ] SubTask 2.3: Remove image parameter from update_product endpoint
  - [ ] SubTask 2.4: Remove image_url handling logic

- [ ] Task 3: Remove media fields from posts router
  - [ ] SubTask 3.1: Remove images, video_url from PostCreate schema
  - [ ] SubTask 3.2: Remove image_url from CommentCreate schema
  - [ ] SubTask 3.3: Remove images, video_url from PostResponse
  - [ ] SubTask 3.4: Remove image_url from CommentResponse

- [ ] Task 4: Remove uploads directory and static files from main.py
  - [ ] SubTask 4.1: Remove uploads_dir variable and os.makedirs calls
  - [ ] SubTask 4.2: Remove StaticFiles import and mount
  - [ ] SubTask 4.3: Remove StaticFiles middleware

- [ ] Task 5: Clean up models.py
  - [ ] SubTask 5.1: Remove profile_image from User model
  - [ ] SubTask 5.2: Remove images from Product model
  - [ ] SubTask 5.3: Remove images from Material model
  - [ ] SubTask 5.4: Remove audio_url from ChatMessage model
  - [ ] SubTask 5.5: Remove images from Post model

## Frontend Tasks

- [ ] Task 6: Remove voice components
  - [ ] SubTask 6.1: Delete `/frontend/src/components/VoiceButton.jsx`
  - [ ] SubTask 6.2: Delete `/frontend/src/components/VoiceInputOverlay.jsx`
  - [ ] SubTask 6.3: Delete `/frontend/src/components/AudioFeedback.jsx`

- [ ] Task 7: Update SellProduct.jsx
  - [ ] SubTask 7.1: Remove image upload state and preview
  - [ ] SubTask 7.2: Remove image upload UI
  - [ ] SubTask 7.3: Remove voice input button
  - [ ] SubTask 7.4: Remove image validation in handleSubmit
  - [ ] SubTask 7.5: Remove image from FormData

- [ ] Task 8: Update api.js
  - [ ] SubTask 8.1: Remove voiceAPI export
  - [ ] SubTask 8.2: Remove voice-related API calls

- [ ] Task 9: Clean up other frontend components
  - [ ] SubTask 9.1: Remove voice imports from ChatAssistant.jsx
  - [ ] SubTask 9.2: Remove image-related code from ProductEdit.jsx
  - [ ] SubTask 9.3: Remove image display from ProductDetail.jsx

# Task Dependencies
- Task 6, 7, 8, 9 can run in parallel
- Task 1, 2, 3, 4, 5 can run in parallel
