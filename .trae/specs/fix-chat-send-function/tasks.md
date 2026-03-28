# Tasks

- [ ] Task 1: Fix chatAPI.send method in api.js
  - [ ] SubTask 1.1: Rename `send` to `sendMessage` or add new method that accepts agent parameter
  - [ ] SubTask 1.2: Update method to pass all three parameters: `(query, agentId, language)`

- [ ] Task 2: Update ChatAssistant.jsx to use correct API method
  - [ ] SubTask 2.1: Change `chatAPI.send(...)` to `chatAPI.sendMessage(...)`
  - [ ] SubTask 2.2: Remove agent parameter from the call (not used in backend)
