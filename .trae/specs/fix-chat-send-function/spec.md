# Fix Chat API Send Function Spec

## Why
The `chatAPI.send` function in `frontend/src/services/api.js` is being called with 3 parameters `(query, agentId, language)`, but `ChatAssistant.jsx` passes only `(query, language)`. The causes "za.send is not a function" error.

## What Changes
- Add `send` method to `chatAPI` object that accepts `(query, agentId, language)`
- Update `ChatAssistant.jsx` to use `chatAPI.sendMessage(query, language)` instead

 `chatAPI.send()`

## Impact
- Affected code: `frontend/src/services/api.js`, `frontend/src/components/ChatAssistant.jsx`
- Affected functionality: Chat assistant messaging

