# Fix All Agents for Genuine Dynamic Responses Spec

## Why
All 7 agents (VAANI, BAZAAR, JODI, SAMAGRI, SAMPARK, VISHWAS, SUPPORT) are returning generic/hardcoded responses. They need to be genuinely intelligent - responding dynamically based on actual platform data for ANY query the user asks, not just specific query patterns.

## What Changes
- Update all agents to use `safe_openai_call` wrapper for consistent error handling
- Fetch comprehensive platform data for each agent's domain
- Include ALL fetched data in OpenAI system prompt for intelligent responses
- Create data-rich fallback responses with actual database content
- Remove silent exception handling - add proper error logging
- Make agents respond naturally to any query using available data

## Impact
- Affected specs: agent-vani-enhancement, chatgpt-assistant-with-fallback
- Affected code: backend/app/services/orchestrator.py

## ADDED Requirements
### Requirement: Genuine Agent Intelligence
Each agent SHALL act as an intelligent assistant that uses real platform data to answer ANY user query in its domain.

#### Scenario: Dynamic Query Handling
- **WHEN** user asks ANY question in the agent's domain
- **THEN** the agent analyzes available data and provides a relevant, contextual response

### Requirement: Comprehensive Data Fetching
Each agent SHALL fetch ALL relevant data from its domain (not filtered/limited).

### Requirement: Data-Rich OpenAI Context
All fetched data SHALL be included in the OpenAI system prompt for intelligent analysis.

### Requirement: Data-Rich Fallbacks
Fallback responses SHALL display actual fetched data when OpenAI is unavailable.

## Agent-Specific Requirements

### VAANI (General Assistant)
- Fetch: products, orders, wallet, community posts, suppliers
- Respond intelligently to ANY general query using this context

### BAZAAR (Market Expert)
- Fetch: ALL products with prices, categories, demand data
- Answer ANY market/pricing/product question dynamically

### JODI (Order Assistant)
- Fetch: ALL orders with full details (products, quantities, statuses, dates)
- Respond to ANY order-related question with actual order data

### SAMAGRI (Supplier Advisor)
- Fetch: ALL suppliers and materials with prices
- Answer ANY supplier/material question dynamically

### SAMPARK (Community Guide)
- Fetch: ALL community posts, user's federation details, district info
- Respond to ANY community/federation question

### VISHWAS (Finance Assistant)
- Fetch: actual wallet balance, ALL recent transactions
- Answer ANY balance/wallet/transaction question with real data

### SUPPORT (Navigation Help)
- Provide contextual help based on user's profile and available features

## MODIFIED Requirements
### Requirement: No Hardcoded Responses
Agents SHALL NOT use hardcoded fallback messages like "No data available" or generic templates.

## REMOVED Requirements
None
