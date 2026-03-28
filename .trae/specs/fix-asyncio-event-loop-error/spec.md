# Fix AsyncIO Event Loop Error Spec

## Why
The backend container crashes on startup with `RuntimeError: There is no current event loop in thread 'MainThread'`. This is caused by `asyncio.Lock()` being instantiated at module import time in `orchestrator.py`, before any event loop exists.

## What Changes
- Fix `orchestrator.py` - Defer `asyncio.Lock()` creation using lazy initialization pattern in `FallbackMonitor` class

## Impact
- Affected specs: None
- Affected code: backend/app/services/orchestrator.py

## ADDED Requirements
None

## MODIFIED Requirements
### Requirement: FallbackMonitor Lock Initialization
The `FallbackMonitor` class SHALL lazily initialize its asyncio lock on first use instead of at instantiation time, to prevent event loop errors when the module is imported.

#### Scenario: Module Import Without Event Loop
- **WHEN** the orchestrator module is imported during application startup
- **THEN** no asyncio.Lock() is created until the lock is actually needed

#### Scenario: Lock Usage During Request
- **WHEN** `record_request()` is called
- **THEN** the lock is created if it doesn't exist, within an async context

## REMOVED Requirements
None
