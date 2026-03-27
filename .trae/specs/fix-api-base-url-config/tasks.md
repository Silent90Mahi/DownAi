# Tasks

- [x] Task 1: Update axios instance in api.js to use environment variables
  - [x] SubTask 1.1: Replace conditional `API_BASE_URL` logic with `import.meta.env.VITE_API_BASE_URL`
  - [x] SubTask 1.2: Add fallback to `http://localhost:6002` when env variable is missing
  - [x] SubTask 1.3: Keep all interceptors and API exports unchanged

- [x] Task 2: Create frontend .env.example file with VITE_API_BASE_URL configuration
  - [x] SubTask 2.1: Add `VITE_API_BASE_URL=http://localhost:6002` for development reference
  - [x] SubTask 2.2: Include comments explaining production setup

- [x] Task 3: Update existing frontend .env file with correct VITE_API_BASE_URL
  - [x] SubTask 3.1: Set `VITE_API_BASE_URL=http://localhost:6002` for local development

- [x] Task 4: Create frontend .env.production.example file
  - [x] SubTask 4.1: Add `VITE_API_BASE_URL=http://<SERVER_IP>:6002` template
  - [x] SubTask 4.2: Include instructions for Docker deployment

- [x] Task 5: Update frontend Dockerfile to pass VITE_API_BASE_URL as build arg
  - [x] SubTask 5.1: Update ARG and ENV for VITE_API_BASE_URL in build stage
  - [x] SubTask 5.2: Ensure build-time environment variable injection

# Task Dependencies
- [Task 2] can run in parallel with [Task 3]
- [Task 4] can run in parallel with [Task 1]
- [Task 5] depends on [Task 1] being completed first
