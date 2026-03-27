# Tasks

- [ ] Task 1: Fix TrustedHostMiddleware to allow IP addresses
  - [ ] SubTask 1.1: Update `backend/app/main.py` to allow IP address patterns in TrustedHostMiddleware
  - [ ] SubTask 1.2: Use regex pattern or wildcard to match any IP address

- [ ] Task 2: Update environment configuration
  - [ ] SubTask 2.1: Change `.env.docker` to use `ENVIRONMENT=development` OR
  - [ ] SubTask 2.2: Keep production mode but configure allowed hosts properly

- [x] Task 3: Rebuild and restart containers
  - [ ] SubTask 3.1: Rebuild backend container with updated code
  - [ ] SubTask 3.2: Rebuild the frontend container (already done, nginx is configured correctly)
  - [ ] SubTask 3.2: Restart all containers

# Task Dependencies
- [Task 3] depends on [Task 1] and [Task 2]
