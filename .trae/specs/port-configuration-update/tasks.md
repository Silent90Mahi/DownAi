# Tasks

- [ ] Task 1: Update docker-compose.yml ports
 Update docker-compose.yml port mappings:
  - Frontend: "3000:80" → "6001:80"
  - Backend: "8000:8000" → "6002:8000"
  - PostgreSQL: "5432:5432" → "6003:5432"
    - Redis: "6379:6379" → "6004:6379"

- [ ] Task 2: Update frontend API configuration
  - [ ] SubTask 2.1: Update frontend/src/services/api.js API_BASE_URL
 Change localhost:8000 → localhost:6002
  - [ ] SubTask 2.2: Update frontend/src/components/ChatAssistant.jsx API_BASE_URL
 Change localhost:8000 → localhost:6002
  - [ ] SubTask 2.3: Update frontend/src/components/RealTimeProvider.jsx WebSocket URL
 Change port 8000 to 6002
  - [ ] SubTask 2.4: Update frontend vite.config for environment variable fallback
  - [ ] SubTask 2.5: Update frontend nginx.conf proxy_pass configuration

    - Change proxy_pass from port 8000 to 6002
  - [ ] SubTask 2.6: Update backend CORS configuration in main.py
    - Change allow_origins from port 3000 to 6001
  - [ ] SubTask 2.7: Update backend health check configuration in docker-compose.yml
    - Change health check from port 8000 to 6002

- [ ] Task 3: Update documentation and deployment guides
  - [ ] SubTask 3.1: Update backend/Phase3_STUB_INTEGRATIONS.md
    - [ ] SubTask 3.2: Update backend/Performance/Gui.md (if exists)
    - [ ] SubTask 3.3: Update backend/Start.sh_GUIDed.md (if exists)
    - [ ] SubTask 3.4: Update backend/app/integrations/notifications.py WebSocket URL
    - [ ] SubTask 3.5: Update backend/app/integrations/maps.py MapBox iframe URL

    - [ ] SubTask 3.6: Update docker-compose.dev.yml
    - [ ] SubTask 3.7: Update test files with new ports

    - [ ] SubTask 3.8: Search for any other references to old ports in documentation

    - [ ] SubTask 3.9: Create comprehensive deployment guide document
    - [ ] SubTask 3.10: Update README.md with new ports
    - [ ] SubTask 3.11: Create DEPLOYMENT_COMMANDS.md file with all deployment commands
    - [ ] SubTask 3.12: Update docker-compose.dev.yml for development

    - [ ] SubTask 3.13: Update backend CORS configuration in main.py to port 6001
    - [ ] SubTask 3.14: Verify docker-compose.yml uses correct environment variable names
    - [ ] SubTask 3.15: Verify backend database URL configuration
    - [ ] SubTask 3.16: Verify backend Redis URL configuration
    - [ ] SubTask 3.17: Verify documentation and deployment guide files reflect new ports
    - [ ] SubTask 3.18: Verify nginx.conf uses correct port for API proxy
    - [ ] SubTask 3.19: Verify docker-compose.dev.yml configuration
    - [ ] SubTask 3.20: Verify test files update ports if needed
    - [ ] SubTask 3.21: Run build and verify services work correctly
    - [ ] SubTask 3.22: Clean Docker volumes and rebuild

        ```bash
        docker compose down -v
        docker compose build --no-cache
        docker compose up -d --build
        ```

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 1
