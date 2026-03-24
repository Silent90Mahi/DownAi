=============================================================================
                    TECHNICAL REQUIREMENT DOCUMENT (TRD)
               PROJECT: SHG SMART MARKET LINKAGE ECOSYSTEM (OOUMPH)
               VERSION: 1.0 | DATE: October 26, 2023
=============================================================================

-----------------------------------------------------------------------------
1. PROJECT OVERVIEW
-----------------------------------------------------------------------------
Project Name   : Ooumph SHG Agentic AI Ecosystem
Description    : A sovereign, voice-first, multilingual market linkage 
                 platform for Self-Help Groups (SHGs) to connect with 
                 buyers, source raw materials, and access market intelligence.
Target Audience: SHG Members (Rural/Urban Women), Admins (MEPMA/SERP), Buyers.
Tech Stack     : Backend: Python (FastAPI), Frontend: React.js
AI Stack       : OpenAI API (GPT-4o/Whisper/TTS) for logic/voice simulation.

-----------------------------------------------------------------------------
2. UI/UX DESIGN GUIDELINES & MNC GRADE STANDARDS
-----------------------------------------------------------------------------
Design Philosophy: "The Last Human Network" - Inclusive, Trust-Driven, 
                   and Hyper-Local.

2.1 Visual Design Language
    - Color Palette:
        * Primary   : Deep Saffron (#FF9933) - representing energy and India.
        * Secondary : Forest Green (#138808) - representing agriculture/growth.
        * Accent    : Trust Blue (#000080) - representing reliability.
        * Background: Off-White (#F9F9F9) for readability in sunlight.
    - Typography:
        * Headings  : Poppins (Sans-serif, Bold).
        * Body Text : Inter (High legibility, supports Telugu/Hindi scripts).
        * Minimum Font Size: 16px for body text (accessibility standard).
    - Iconography:
        * Use large, labeled icons (48x48px minimum).
        * Avoid abstract icons; use intuitive metaphors (e.g., a basket for 
          products, a handshake for deals).

2.2 Accessibility & Inclusivity (MNC Grade)
    - Voice-First Navigation: Every screen must have a floating "Mic" button 
      that is always visible.
    - Contrast Ratios: Adhere to WCAG 2.1 AA standards (4.5:1 for text).
    - Multilingual Support: Interface defaults to device language; supports 
      Telugu, Hindi, Urdu, and English.
    - Low-Bandwidth Mode: A toggle in settings to disable images and heavy 
      animations for 2G/3G networks.

2.3 User Experience (UX) Flows
    - Onboarding: OTP-based login (simulated) -> Voice guided profile setup.
    - Dashboard: Card-based layout. Large "Action Cards" (e.g., "Sell Product",
      "Buy Raw Material") instead of complex menus.
    - Feedback: Immediate visual and audio confirmation for every action 
      (e.g., "Your listing is live").

-----------------------------------------------------------------------------
3. FEATURE SPECIFICATIONS (END-TO-END)
-----------------------------------------------------------------------------

3.1 CORE MODULE 1: THE AGENTIC AI SYSTEM (BACKEND)
The backend must simulate an "Agentic Orchestration Layer" where different 
AI personas handle specific requests.

Feature 3.1.1: Agent Vaani (Voice Interface)
    - Description: Speech-to-Text (STT) and Text-to-Speech (TTS) gateway.
    - Input: Audio files (WAV/MP3) or text queries.
    - Output: Text response + Audio URL.
    - Logic: 
        1. Receive audio -> Transcribe using OpenAI Whisper.
        2. Detect intent (e.g., "selling", "buying", "help").
        3. Route to specific agent -> Generate response.
        4. Convert response to audio using OpenAI TTS.

Feature 3.1.2: Agent Bazaar Buddhi (Market Intelligence)
    - Description: Predicts demand and suggests pricing.
    - Input: Product category, location.
    - Output: Demand score (High/Med/Low), Recommended Price Range.
    - Mock Logic: Use a Python function that simulates federated learning 
      insights by randomizing demand based on season/location seed.

Feature 3.1.3: Agent Jodi (Buyer Matching)
    - Description: Matches SHG products to buyers/mandis.
    - Input: Product details, Quantity, Trust Score.
    - Output: List of matched buyers (Name, Location, Offer Price).
    - Mock Logic: Filter mock database of buyers.

Feature 3.1.4: Agent Samagri (Raw Material Procurement)
    - Description: Recommends raw material suppliers.
    - Input: Material requirement list.
    - Output: Sorted list of suppliers by Price and Trust Score.

Feature 3.1.5: Agent Vishwas (Trust Scoring)
    - Description: Calculates the "Trust Score" for SHGs and Buyers.
    - Formula: 
      Score = (Quality * 0.25) + (Delivery * 0.20) + (Finance * 0.20) + 
               (Community * 0.15) + (Sustainability * 0.10) + (Digital * 0.10).
    - Feature: Generates a "Trust Badge" (Bronze/Silver/Gold) on profile.

Feature 3.1.6: Agent Sampark (Community Orchestration)
    - Description: Manages the hierarchy (SHG -> SLF -> TLF).
    - Feature: Allows TLF leaders to view aggregate data of their SHGs.

3.2 CORE MODULE 2: SHG MEMBER WEB APP (FRONTEND - REACT)
    - Dashboard: Shows Trust Score, Active Listings, and Revenue.
    - Voice Assistant Button: Triggers Vaani agent.
    - Product Management: "Add Product" form with image upload and voice 
      input for description.
    - Order Management: Track orders status (Placed, Shipped, Delivered).
    - Marketplace: Browse raw materials (Samagri) or view buyer requests 
      (Jodi).

3.3 CORE MODULE 3: ADMIN PORTAL (FRONTEND - REACT)
    - User Roles: District Project Director (DPD), Mission Director.
    - Oversight: View aggregate stats (Total SHGs, Total Volume, Trust 
      Score Distribution).
    - Audit Logs: View logs generated by Agent Vishwas.

-----------------------------------------------------------------------------
4. TECHNICAL ARCHITECTURE
-----------------------------------------------------------------------------
Architecture Pattern: REST API (Monolithic for MVP, Modular structure).
Data Format: JSON.

4.1 Backend Architecture (Python - FastAPI)
    - Main Server: `main.py` (Entry point).
    - Routers:
        * `routes/auth.py`: Login/Register.
        * `routes/voice.py`: STT/TTS endpoints.
        * `routes/market.py`: Buyer matching logic.
        * `routes/trust.py`: Score calculation.
    - Services (Agentic Layer):
        * `services/vaani_service.py`: Wrapper for OpenAI Audio API.
        * `services/bazaar_service.py`: Mock logic for market trends.
        * `services/llm_orchestrator.py`: The "Brain" that decides which 
          agent to call using OpenAI GPT-4.

4.2 Frontend Architecture (React.js)
    - State Management: React Context API or Redux Toolkit.
    - UI Library: Tailwind CSS (for custom styling) or Material UI.
    - Key Components:
        * `VoiceButton.js`: Component to record audio and send to backend.
        * `ProductCard.js`: Display product with Trust Badge.
        * `TrustMeter.js`: Visual gauge for Trust Score.

4.3 Database Schema (Mock SQL/NoSQL structure)
    - Users Table:
        * id, phone, name, role (SHG/Buyer/Admin), trust_score, location.
    - Products Table:
        * id, user_id, name, category, price, image_url, stock.
    - Transactions Table:
        * id, buyer_id, seller_id, product_id, status, timestamp.
    - AuditLogs Table:
        * id, action, actor_id, details, timestamp.

-----------------------------------------------------------------------------
5. API INTEGRATION SPECIFICATIONS
-----------------------------------------------------------------------------
Constraint: No real external APIs (Payment/Gateways). Only OpenAI for AI 
features.

5.1 OpenAI API Usage
    - Model: GPT-4o (Orchestration & Text), Whisper (STT), TTS-1 (Voice).
    - Prompt Engineering:
        System Prompt: "You are the Ooumph Agentic Ecosystem. You represent 
        agents Vaani, Bazaar Buddhi, Jodi, Samagri, and Vishwas. Analyze the 
        user query and route it to the correct agent logic. Respond in the 
        user's language (Telugu/Hindi/English)."

5.2 Mock API Handlers
    - Payment Gateway: Function returns `{ "status": "SUCCESS", "txn_id": 
      "MOCK_TXN_123" }` without calling a real gateway.
    - GeM/ONDC Integration: Mock data returned from a local JSON file 
      containing dummy government tenders.

-----------------------------------------------------------------------------
6. SECURITY & COMPLIANCE (SIMULATED)
-----------------------------------------------------------------------------
- Data Privacy: Simulate "Data Stays Local". Store data in local DB. 
  Do not send sensitive PII to external logs.
- Authentication: JWT (JSON Web Tokens) for session management.
- Audit Trail: Every transaction must create an entry in the `AuditLogs` 
  table (Agent Vishwas responsibility).

-----------------------------------------------------------------------------
7. DEVELOPER IMPLEMENTATION GUIDE (STEP-BY-STEP)
-----------------------------------------------------------------------------

Step 1: Setup Environment
    - Python 3.10+, Node.js 18+.
    - Install libraries: `fastapi`, `uvicorn`, `openai`, `python-multipart`, 
      `react`, `axios`.

Step 2: Backend Development
    - Create `server.py`. Setup CORS.
    - Implement `/api/voice/process` endpoint:
        1. Accept audio blob.
        2. Call OpenAI Whisper API to transcribe.
        3. Pass transcript to GPT-4o with Agent System Prompt.
        4. Get JSON/Text response.
        5. If text, call OpenAI TTS API to return audio.
    - Implement Trust Score Logic (Python calculation function).

Step 3: Frontend Development
    - Create React App.
    - Build Audio Recorder Component (use `react-media-recorder`).
    - Build Dashboard UI with Tailwind CSS.
    - Connect to Backend API.

Step 4: Integration
    - Connect "Sell" button -> Agent Jodi API.
    - Connect "Buy Material" button -> Agent Samagri API.

-----------------------------------------------------------------------------
8. SUCCESS METRICS (FOR AGENT TESTING)
-----------------------------------------------------------------------------
1. Voice Interaction: User can speak in Telugu ("Naku pickles ammalivi 
   kavali") and receive a relevant audio response in Telugu.
2. Trust Score: A new user starts with a score, and completing a mock 
   transaction updates the score automatically.
3. Buyer Matching: Uploading a product returns a list of 3 mock buyers.

=============================================================================
                           END OF DOCUMENT
=============================================================================