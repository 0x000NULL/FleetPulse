# FleetPulse - Vibe Coding Journey: AI Prompts Used

This document captures the "vibe coding" process behind FleetPulse—a chronicle of human-AI collaboration that built a production-grade fleet management platform in under 3 weeks.

---

## 🎯 Project Genesis (Feb 12, 2026)

### Initial Concept Prompt
**To:** Claude (Anthropic)

```
I'm entering the Geotab Vibe Coding Competition. I run 8 Budget Rent a Car locations 
in Las Vegas with 50 vehicles. I want to build a fleet intelligence dashboard that:

1. Shows real-time vehicle locations on a map
2. Tracks safety scores per driver and location
3. Has an autonomous AI monitor that detects anomalies 24/7
4. Allows managers to ask questions in natural language ("Which location needs coaching?")
5. Gamifies driver safety with leaderboards and badges

Tech stack: Python backend (FastAPI), React frontend, Geotab API.

Help me architect this. What's the minimal viable structure to win the "Vibe Master" prize?
```

**Response:** Claude generated the project structure, FastAPI skeleton, React component hierarchy, and a 3-phase implementation roadmap (data layer → AI layer → UI polish).

---

## 🏗️ Phase 1: Backend Foundation (Week 1)

### Geotab API Client
**Prompt:**
```
Create a Python wrapper for the Geotab API using mygeotab library. It should:
- Authenticate once and cache the session
- Have helper methods for Get Device, Get Trip, Get ExceptionEvent
- Handle rate limiting gracefully
- Load credentials from environment variables (.env file)

Include type hints and error handling.
```

**Output:** `backend/geotab_client.py` (150 lines, production-ready auth caching)

### FastAPI Router Structure
**Prompt:**
```
Scaffold FastAPI routers for:
1. /api/dashboard (fleet KPIs)
2. /api/vehicles (vehicle list + details)
3. /api/safety (safety scores)
4. /api/gamification (leaderboards, badges, challenges)
5. /api/monitor (agentic anomaly detection)

Use Pydantic v2 for request/response models. Enable CORS for localhost:5173.
Group related endpoints into separate router files.
```

**Output:** 6 router files + `backend/app.py` with clean separation of concerns

---

## 🤖 Phase 2: Agentic Intelligence (Week 2)

### Autonomous Anomaly Detection
**Prompt:**
```
Build an agentic monitor service that runs in a background thread and checks every 60 seconds for:

1. Speed anomalies (vehicles exceeding 75 mph)
2. Excessive idle (>30 min in one spot)
3. Off-route detection (vehicles leaving Las Vegas metro area)
4. After-hours activity (11 PM - 5 AM)
5. Fleet pattern analysis (unusual spikes in trips/distance)
6. Location inventory imbalance (zero or >15 vehicles at one location)

Store alerts in memory with severity levels (critical/high/medium/low).
Include pattern tracking to avoid duplicate alerts.
```

**Output:** `backend/services/monitor_service.py` (300+ lines, fully autonomous)

### Natural Language Query Processing
**Prompt:**
```
Create an AI chat interface that answers fleet questions using pattern matching + Claude API fallback.

Pattern handlers for:
- "Which location has best/worst safety scores?"
- "Show vehicles with high idle time"
- "Cost optimization opportunities"
- "Vehicles needing maintenance"
- "Compare locations"

Response format: { text, chart_data, insights, confidence }
Generate Recharts-compatible data structures for visualization.
```

**Output:** `backend/routers/ai_chat.py` with 7 specialized query handlers

---

## 🎨 Phase 3: UI/UX Polish (Week 3)

### React Dashboard Components
**Prompt:**
```
Build a professional dark-themed fleet dashboard with:

1. Animated KPI cards (smooth counter animations, sparklines)
2. Interactive Leaflet map with vehicle markers (color-coded by status)
3. Real-time alert feed (severity-based styling)
4. Safety scorecard with trend indicators
5. Framer Motion page transitions
6. Mobile-responsive layout (Tailwind CSS)

Use TypeScript. Fetch data via custom hooks with 30-sec auto-refresh.
```

**Output:** 12 React components + `hooks/useGeotab.ts` for data fetching

### AI Chat Interface
**Prompt:**
```
Create a chat interface similar to ChatGPT but for fleet queries.

Features:
- Message bubbles (user vs assistant)
- Typing indicator while AI processes
- Chart rendering inline (Recharts bar/pie/line charts)
- Insight cards with icons
- Auto-scroll to latest message
- Confidence score display (0-100%)

Dark theme, smooth animations, mobile-friendly.
```

**Output:** `frontend/src/components/AIChatInterface.tsx` (400+ lines)

---

## 🔧 Advanced Features (Week 3 continued)

### Predictive Maintenance
**Prompt:**
```
Add a predictive maintenance system that:
1. Tracks engine hours, distance, last service date
2. Uses simple heuristics to forecast next service
3. Categorizes urgency (overdue, due soon, ok)
4. Generates AI recommendations via Claude API

Cache results for 5 minutes to reduce API calls.
```

**Output:** `backend/routers/maintenance.py` + caching layer

### Driver Coaching Automation
**Prompt:**
```
Build automated driver coaching that:
1. Analyzes safety violations per driver
2. Generates personalized coaching messages using Claude
3. Categorizes coaching needs (speeding, harsh braking, idle time)
4. Stores recommendations in memory for dashboard display

Use batch processing to reduce API costs.
```

**Output:** `frontend/src/components/DriverCoaching.tsx` + backend logic

### MyGeotab Add-In
**Prompt:**
```
Create a MyGeotab Add-In that embeds FleetPulse inside the MyGeotab portal.

Requirements:
- Single HTML file (no build step)
- Uses MyGeotab SDK (api.call for data fetching)
- Standalone mode fallback (calls FleetPulse API directly)
- Shows KPIs, vehicle list, safety scores
- "Full Dashboard" button to open live FleetPulse in iframe

Inline CSS (dark theme), vanilla JS only.
```

**Output:** `addin/fleetpulse/index.html` (350 lines, production-ready)

---

## 🧩 MCP (Model Context Protocol) Integration

### MCP Server for Claude Desktop
**Prompt:**
```
Build an MCP server for Claude Desktop integration.

Tools to expose:
1. get_fleet_overview() → vehicle counts, trips, distance
2. get_vehicles() → list all vehicles with status
3. get_safety_scores() → driver rankings
4. get_alerts(severity?) → recent alerts
5. get_location_stats(location?) → per-location metrics
6. get_leaderboard() → gamification rankings
7. query_fleet(question) → natural language processing

Use mcp Python library. Server should proxy requests to FastAPI backend running on localhost:8080.
Include resource for fleet summary (read-only context for Claude).
```

**Output:** `mcp-server/server.py` (200+ lines, 27 tools total)

---

## 🐛 Debugging & Optimization

### Performance Issues
**Prompt:**
```
My maintenance endpoints are slow (5+ seconds). Here's the code:
[pasted maintenance router code]

How can I add caching without external dependencies? Target 5-minute TTL.
```

**Response:** Claude suggested in-memory cache with timestamp tracking. Implemented in 15 minutes. Page load dropped from 5.2s → 0.3s.

### Route Replay Feature
**Prompt:**
```
Add a route replay feature that shows historical trip paths on the map.

User selects a vehicle → sees list of recent trips → clicks trip → 
animated route appears on map with breadcrumb markers.

Use Leaflet polylines. Include back button and loading spinner.
```

**Output:** `frontend/src/components/RouteReplay.tsx` with smooth animations

---

## 🎨 UI/UX Refinements

### Dark/Light Mode Toggle
**Prompt:**
```
Add a theme toggle button (sun/moon icon) that switches between dark and light mode.
Persist preference in localStorage. Use Tailwind's dark: variant for styling.

Smooth transition animation (300ms) when switching themes.
```

**Output:** `frontend/src/components/ThemeToggle.tsx` + Tailwind config updates

### PWA (Progressive Web App)
**Prompt:**
```
Make FleetPulse installable as a PWA.

Requirements:
1. Service worker for offline caching
2. manifest.json with icons
3. Install prompt component (appears on mobile)
4. Offline indicator (shows when connection drops)

Use Vite PWA plugin for automatic service worker generation.
```

**Output:** PWA config + 2 new React components

---

## 📊 Data Connector Integration

### OData v4 Endpoints
**Prompt:**
```
Integrate Geotab Data Connector (OData v4) for pre-aggregated analytics.

Endpoints needed:
1. /api/data-connector/tables → list available tables
2. /api/data-connector/vehicle-kpis?days=14 → utilization metrics
3. /api/data-connector/safety-scores?days=14 → aggregated safety data
4. /api/data-connector/fault-trends?days=14 → fault code frequency

Use httpx for async requests. Handle 2-3 hour activation delay gracefully.
```

**Output:** `backend/routers/data_connector.py` with error handling for unactivated databases

---

## 🏆 Competition-Specific Optimizations

### Submission Video Script
**Prompt:**
```
Write a 3-minute demo video script that showcases FleetPulse for the Geotab Vibe Coding Competition.

Highlights:
- Autonomous AI monitoring (key differentiator)
- Natural language queries with charts
- Safety gamification
- Professional UI/UX
- MyGeotab Add-In + MCP integration

Target audience: Geotab judges evaluating for "Vibe Master" prize.
```

**Output:** Structured 3-min script with timestamps (see SUBMISSION_CHECKLIST.md)

### README Enhancement
**Prompt:**
```
Rewrite the README to be competition-worthy.

Sections:
1. Hero (badges, screenshot, tagline)
2. Architecture diagram (ASCII art)
3. Key features (with emojis)
4. Quick start (minimal steps)
5. API endpoints table
6. Tech stack
7. Prize category alignment

Tone: Professional but approachable. Emphasize AI innovation.
```

**Output:** Complete README rewrite (15KB → comprehensive guide)

---

## 🧠 Key Learnings from Vibe Coding

### What Worked
1. **Incremental Prompting:** Started with "build a dashboard" → evolved to "add AI chat" → "make it autonomous"
2. **Context Sharing:** Pasted error messages directly → Claude debugged faster than StackOverflow
3. **Specification First:** Detailed prompts (with examples) = better code quality
4. **Iterative Refinement:** "Make it more professional" → "Add animations" → "Optimize performance"

### What Didn't Work
1. **Vague Prompts:** "Make it better" → Got generic suggestions instead of actionable code
2. **Too Much at Once:** "Build entire backend" → Overwhelmed AI, had to break into 5 sub-prompts
3. **No Examples:** "Add chart" without specifying library → Claude guessed D3.js instead of Recharts

### Surprise Wins
- **MCP Server:** Asked "Can I make this work with Claude Desktop?" → Claude generated entire MCP spec
- **Agentic Monitor:** One prompt → 300 lines of production-ready autonomous detection logic
- **UI Animations:** "Add smooth transitions" → Got Framer Motion setup + 12 animated components

---

## 📈 Metrics

**Total Development Time:** ~18 days (Feb 12 - Mar 1)  
**AI Prompts Used:** ~150 (estimated)  
**Code Generated by AI:** ~60% (scaffolding, boilerplate, components)  
**Code Written by Human:** ~40% (business logic, integration, polish)  
**AI Tools Used:** Claude (Anthropic), GPT-4 (OpenAI), GitHub Copilot  
**Lines of Code:** ~8,000 (backend + frontend + MCP)  
**Commits:** 56  

---

## 🎯 Competition Alignment

**Vibe Master Prize ($10k):** FleetPulse demonstrates mastery of vibe coding by combining:
- Autonomous AI agents (not just chatbots)
- Multi-modal responses (text + charts + insights)
- Production-ready deployment (not a prototype)
- Complete ecosystem (dashboard + Add-In + MCP + API)

**Innovator Prize ($5k):** Unique features include:
- 24/7 agentic monitoring with pattern recognition
- MCP integration for Claude Desktop conversational fleet management
- Predictive maintenance forecasting with AI-powered recommendations

**Most Collaborative:** Active engagement on r/geotab, sharing learnings, helping other participants

---

**Conclusion:** FleetPulse is a testament to human-AI collaboration. Every feature started as a conversation. The AI handled the tedious parts (boilerplate, type definitions, styling). I focused on the creative parts (architecture, business logic, user experience). Together, we built something neither of us could have built alone.

— Ethan Aldrich, CTO, Budget Rent a Car Las Vegas  
— With Claude (Anthropic) as co-pilot ⚡
