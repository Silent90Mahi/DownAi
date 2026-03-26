# Tasks - Agent Vani Enhancement

## Phase 1: Backend Agent Enhancement

- [x] Task 1: Enhance Agent System Prompts
  - [x] SubTask 1.1: Update JODI (Order Assistant) system prompt with action capabilities
  - [x] SubTask 1.2: Update VISHWAS (Finance Assistant) system prompt with balance queries
  - [x] SubTask 1.3: Update SAMAGRI (Supplier Advisor) system prompt with quote requests
  - [x] SubTask 1.4: Update BAZAAR (Market Expert) system prompt with price analysis
  - [x] SubTask 1.5: Update SAMPARK (Community Guide) system prompt with community actions
  - [x] SubTask 1.6: Update VAANI (General) system prompt to be more helpful
  - [x] SubTask 1.7: Update SUPPORT (Support Bot) system prompt with navigation help

- [x] Task 2: Implement Action Handler Functions
  - [x] SubTask 2.1: Create `get_user_orders_context()` function to fetch user orders
  - [x] SubTask 2.2: Create context injection for delivery address changes
  - [x] SubTask 2.3: Create `get_user_wallet_context()` function to fetch balance/transactions
  - [x] SubTask 2.4: Create context for order cancellation
  - [x] SubTask 2.5: Create `get_user_profile_context()` function for supplier search

- [x] Task 3: Add Context Injection to Agents
  - [x] SubTask 3.1: Inject user's recent orders into agent context
  - [x] SubTask 3.2: Inject user's wallet balance into agent context
  - [x] SubTask 3.3: Inject user's trust score and badge into agent context
  - [x] SubTask 3.4: Inject user's district and location into agent context

- [x] Task 4: Enhance Agent Routing
  - [x] SubTask 4.1: Add "address" keyword to JODI routing
  - [x] SubTask 4.2: Add "update" keyword detection with context
  - [x] SubTask 4.3: Add "change" keyword detection with context
  - [x] SubTask 4.4: Improve keyword-based routing accuracy

## Phase 2: Response Enhancement

- [x] Task 5: Improve Fallback Responses
  - [x] SubTask 5.1: Create action-aware fallback for order queries
  - [x] SubTask 5.2: Create action-aware fallback for wallet queries
  - [x] SubTask 5.3: Create action-aware fallback for address queries
  - [x] SubTask 5.4: Create action-aware fallback for supplier queries

- [x] Task 6: Add Response Formatting
  - [x] SubTask 6.1: Format order status responses with emojis and structure
  - [x] SubTask 6.2: Format wallet responses with balance breakdown
  - [x] SubTask 6.3: Format action confirmation responses clearly
  - [x] SubTask 6.4: Add quick action suggestions to responses

## Phase 3: Frontend Enhancement

- [x] Task 7: Enhance ChatAssistant Component
  - [x] SubTask 7.1: Add action buttons for common tasks (Track Order, Check Balance)
  - [x] SubTask 7.2: Display agent-specific action suggestions
  - [x] SubTask 7.3: Add loading states for action execution
  - [x] SubTask 7.4: Show success/error messages for actions

- [x] Task 8: Test All Agent Responses
  - [x] SubTask 8.1: Test VAANI with general queries
  - [x] SubTask 8.2: Test JODI with order/address queries
  - [x] SubTask 8.3: Test VISHWAS with wallet/balance queries
  - [x] SubTask 8.4: Test SAMAGRI with supplier queries
  - [x] SubTask 8.5: Test BAZAAR with market queries
  - [x] SubTask 8.6: Test SAMPARK with community queries
  - [x] SubTask 8.7: Test SUPPORT with help queries

---

# Task Dependencies

- [Task 2: Action Handlers] depends on [Task 1: System Prompts] ✅
- [Task 3: Context Injection] depends on [Task 2: Action Handlers] ✅
- [Task 5: Fallback Responses] depends on [Task 2: Action Handlers] ✅
- [Task 6: Response Formatting] depends on [Task 5: Fallback Responses] ✅
- [Task 7: Frontend Enhancement] depends on [Task 6: Response Formatting] ✅
- [Task 8: Testing] depends on [Task 7: Frontend Enhancement] ✅

---

# Parallel Execution Groups

**Group A (Can run in parallel):** ✅ COMPLETED
- Task 1: System Prompts
- Task 4: Agent Routing

**Group B (After Group A):** ✅ COMPLETED
- Task 2: Action Handlers
- Task 3: Context Injection

**Group C (After Group B):** ✅ COMPLETED
- Task 5: Fallback Responses
- Task 6: Response Formatting

**Group D (After Group C):** ✅ COMPLETED
- Task 7: Frontend Enhancement

**Group E (Final):** ✅ COMPLETED
- Task 8: Testing
