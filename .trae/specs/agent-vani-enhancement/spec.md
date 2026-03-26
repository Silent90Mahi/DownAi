# Agent Vani Enhancement Spec

## Why
The AI agents (Vaani and 6 other specialized agents) are not responding properly to user queries. For example, when a user asks "update delivery address", the agents don't provide appropriate responses or actions. The agents need to understand user intent and either execute actions or provide helpful guidance.

## What Changes
- Enhance agent system prompts with action-aware responses
- Add function calling capability for agents to perform actions
- Implement context-aware responses based on user's current data
- Add proper fallback responses for action requests
- Ensure each agent handles its domain-specific queries correctly

## Impact
- Affected specs: Chat Assistant, Order Management, User Profile
- Affected code: 
  - `backend/app/services/orchestrator.py`
  - `backend/app/routers/chat.py`
  - `frontend/src/components/ChatAssistant.jsx`

## ADDED Requirements

### Requirement: Action-Aware Agent Responses
The system SHALL provide agents with the ability to understand action requests and either execute them or guide users to the correct location.

#### Scenario: User requests delivery address update
- **WHEN** user sends "update delivery address" or similar request
- **THEN** Order Assistant (JODI) agent SHALL recognize the intent and either:
  - Execute the address update if order ID is provided
  - Guide user to Orders page to select the order first
  - Ask for clarification on which order to update

#### Scenario: User asks about order status
- **WHEN** user sends "where is my order" or "track order"
- **THEN** Order Assistant (JODI) agent SHALL fetch and display order tracking information

#### Scenario: User requests wallet balance
- **WHEN** user sends "what is my balance" or "trust coins"
- **THEN** Finance Assistant (VISHWAS) agent SHALL fetch and display current balance

### Requirement: Context-Aware Responses
The system SHALL provide agents with user context (orders, wallet, profile) to give personalized responses.

#### Scenario: Personalized order help
- **WHEN** user asks about orders
- **THEN** agent SHALL include user's actual order count and recent order status

#### Scenario: Personalized wallet help
- **WHEN** user asks about trust coins or wallet
- **THEN** agent SHALL include user's actual balance and transaction count

### Requirement: Proper Agent Routing
The system SHALL correctly route user queries to the appropriate specialized agent.

#### Scenario: Order-related query routing
- **WHEN** user mentions "order", "delivery", "shipping", "address", "cancel"
- **THEN** query SHALL be routed to JODI (Order Assistant) agent

#### Scenario: Wallet/finance query routing
- **WHEN** user mentions "balance", "coins", "wallet", "payment", "redeem"
- **THEN** query SHALL be routed to VISHWAS (Finance Assistant) agent

#### Scenario: Supplier query routing
- **WHEN** user mentions "supplier", "raw material", "bulk", "quote"
- **THEN** query SHALL be routed to SAMAGRI (Supplier Advisor) agent

### Requirement: Action Execution Capability
The system SHALL allow agents to execute certain actions on behalf of users.

#### Scenario: Cancel order action
- **WHEN** user requests to cancel an order with valid order ID
- **THEN** JODI agent SHALL execute cancellation and confirm

#### Scenario: Update address action
- **WHEN** user provides order ID and new address
- **THEN** JODI agent SHALL update delivery address and confirm

## MODIFIED Requirements

### Requirement: Enhanced System Prompts
Each agent SHALL have detailed system prompts that include:
- Available actions they can perform
- Database query capabilities
- Proper response formatting
- Action execution instructions

### Requirement: Fallback Response Enhancement
Fallback responses SHALL be action-aware and guide users appropriately instead of generic responses.

## REMOVED Requirements
None - this is purely additive.
