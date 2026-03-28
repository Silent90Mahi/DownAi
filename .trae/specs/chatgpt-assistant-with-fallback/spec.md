# ChatGPT Assistant with Platform-Only Responses and Fallback

## Why
The chat assistant needs to prioritize platform-specific data responses and only offer global search when no relevant platform data exists. Additionally, a robust local fallback system is required when ChatGPT API fails, ensuring the assistant remains functional at all times.

## What Changes
- Add platform data detection logic to check if relevant data exists
- Implement "Ask to search globally" flow when no platform data is found
- Enhance all 6 agents (VAANI, BAZAAR, JODI, SAMAGRI, SAMPARK, VISHWAS) with platform-first behavior
- Add SUPPORT agent for navigation help
- Create comprehensive local fallback responses for all agents
- Add graceful degradation when OpenAI API is unavailable
- Store and use the provided ChatGPT API key

## Impact
- Affected specs: Chat Assistant, Agent Orchestrator
- Affected code:
  - `backend/app/services/orchestrator.py`
  - `backend/app/routers/chat.py`
  - `backend/core/config.py`
  - `frontend/src/components/ChatAssistant.jsx`

## ADDED Requirements

### Requirement: Platform-Only Response Mode
The system SHALL prioritize responding only about platform data by default.

#### Scenario: Platform data available
- **WHEN** user asks about orders, products, wallet, etc.
- **AND** relevant data exists in the platform
- **THEN** agent SHALL respond with platform-specific information

#### Scenario: No platform data available
- **WHEN** user asks a question
- **AND** no relevant platform data is found
- **THEN** agent SHALL ask: "I couldn't find relevant information in your platform data. Would you like me to search globally?"
- **AND** wait for user confirmation before global search

### Requirement: Global Search with Confirmation
The system SHALL allow global search only after explicit user confirmation.

#### Scenario: User confirms global search
- **WHEN** agent asks about global search
- **AND** user confirms with "yes", "sure", "okay", etc.
- **THEN** agent SHALL proceed with global knowledge search using ChatGPT

#### Scenario: User declines global search
- **WHEN** agent asks about global search
- **AND** user declines with "no", "cancel", etc.
- **THEN** agent SHALL suggest alternative platform actions

### Requirement: Robust Local Fallback System
The system SHALL maintain full functionality when ChatGPT API is unavailable.

#### Scenario: OpenAI API failure
- **WHEN** ChatGPT API call fails (timeout, rate limit, invalid key, network error)
- **THEN** system SHALL use local fallback responses
- **AND** response SHALL be contextual and helpful
- **AND** user SHALL NOT experience service interruption

#### Scenario: OpenAI API key invalid
- **WHEN** OpenAI API key is missing or invalid
- **THEN** system SHALL continue operating with local fallback
- **AND** log warning about API key issue

### Requirement: Six Specialized Agents with Platform Focus
The system SHALL provide 6 specialized agents (plus SUPPORT) that only respond about platform data.

#### Scenario: VAANI (General Assistant)
- **WHEN** user asks general questions
- **THEN** VAANI SHALL only answer about marketplace topics
- **AND** redirect non-marketplace questions appropriately

#### Scenario: BAZAAR (Market Expert)
- **WHEN** user asks about market/pricing
- **THEN** BAZAAR SHALL provide platform market data
- **AND** offer global search only if no platform data exists

#### Scenario: JODI (Order Assistant)
- **WHEN** user asks about orders
- **THEN** JODI SHALL fetch and display user's actual orders
- **AND** guide to Orders page for actions

#### Scenario: SAMAGRI (Supplier Advisor)
- **WHEN** user asks about suppliers/materials
- **THEN** SAMAGRI SHALL search platform suppliers first
- **AND** offer global search if no local suppliers found

#### Scenario: SAMPARK (Community Guide)
- **WHEN** user asks about community/federation
- **THEN** SAMPARK SHALL provide platform community info
- **AND** offer global search if no relevant community data

#### Scenario: VISHWAS (Finance Assistant)
- **WHEN** user asks about wallet/coins
- **THEN** VISHWAS SHALL display actual wallet data from platform
- **AND** guide to Wallet page for transactions

### Requirement: Enhanced Error Handling
The system SHALL gracefully handle all error scenarios.

#### Scenario: Database connection error
- **WHEN** platform database is unavailable
- **THEN** agent SHALL inform user and offer global search
- **AND** continue providing general assistance

#### Scenario: Partial data available
- **WHEN** some platform data is available but incomplete
- **THEN** agent SHALL provide available data
- **AND** note any limitations

## MODIFIED Requirements

### Requirement: Enhanced System Prompts
Each agent SHALL have system prompts that enforce platform-only responses with global search as opt-in.

### Requirement: Improved Fallback Responses
Fallback responses SHALL be contextually rich and action-oriented, not generic.

## REMOVED Requirements
None - this is purely additive.
