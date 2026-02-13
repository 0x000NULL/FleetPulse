# 🚗 FleetPulse — Multi-Location Fleet Intelligence Platform

**GeoTab Hackathon 2026 Entry** | Budget Rent a Car Las Vegas Demo

FleetPulse is an intelligent fleet management dashboard for multi-location rental operations. It connects to GeoTab's telematics API to provide real-time vehicle tracking, safety scoring, gamification, and **autonomous anomaly detection** across 8 Budget Rent a Car locations in Las Vegas.

![FleetPulse](https://img.shields.io/badge/Status-Live-green) ![GeoTab](https://img.shields.io/badge/GeoTab-Integrated-blue) ![Vehicles](https://img.shields.io/badge/Vehicles-50-orange)

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   React + Vite Frontend              │
│  Dashboard │ Fleet Map │ Leaderboard │ Agent Monitor │
└────────────────────────┬─────────────────────────────┘
                         │ /api/* (Vite proxy)
┌────────────────────────▼─────────────────────────────┐
│                FastAPI Backend (8080)                 │
│  /dashboard │ /vehicles │ /safety │ /gamification    │
│  /alerts │ /monitor (agentic)                        │
├──────────────────────────────────────────────────────┤
│              Agentic Monitor (background)            │
│  Speed anomalies │ Idle detection │ Off-route alerts │
│  After-hours │ Fleet patterns │ Location imbalances  │
└────────────────────────┬─────────────────────────────┘
                         │ mygeotab SDK
                    ┌────▼────┐
                    │ GeoTab  │
                    │   API   │
                    └─────────┘
```

## ✨ Key Features

### 🤖 Agentic Monitor (Key Differentiator)
An autonomous intelligence layer that continuously analyzes fleet telemetry:
- **Speed Anomaly Detection** — Flags vehicles exceeding speed thresholds with severity levels
- **Excessive Idle Detection** — Identifies vehicles idle for extended periods
- **Off-Route Alerts** — Detects vehicles leaving the Las Vegas metro area
- **After-Hours Monitoring** — Flags activity during 11 PM – 5 AM
- **Fleet Pattern Analysis** — Identifies unusual fleet-wide activity patterns
- **Location Inventory Balancing** — Alerts when locations have zero or excess vehicles
- Runs every 60 seconds with full alert history and pattern tracking

### 🏆 FleetChamp Gamification
- Driver safety scoring with points (base 1000 × safety %, -50 per incident)
- Badges: 🏅 Speed Demon Free, 🎯 Smooth Operator, 🌿 Eco Champion, ⭐ Perfect Week
- Per-driver and per-location leaderboards
- Location vs location competition rankings
- Weekly challenges (Safe Week, Zero Speeding)

### 📊 Real-Time Dashboard
- KPI cards: total vehicles, active, idle, parked, trips, distance, avg duration
- Dark Leaflet map with vehicle markers (color-coded by status) and location zones
- Alert feed with severity-based styling (critical/high/medium/low)
- Safety scorecard with trend indicators and progress bars
- 30-second vehicle refresh, 15-second alert refresh

### 📍 8 Budget Rent a Car Locations
W Sahara · Golden Nugget · Center Strip · Tropicana · LAS Airport · Gibson · Henderson Executive · Losee

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- GeoTab credentials (set in `~/.openclaw/.env.geotab` or project `.env`)
- **Optional**: Anthropic API key for Claude AI integration

### Environment Variables

#### Basic Setup (`.env` file in backend/)
```env
GEOTAB_DATABASE=demo_fleetpulse
GEOTAB_USERNAME=your_username
GEOTAB_PASSWORD=your_password
GEOTAB_SERVER=my.geotab.com
```

#### AI-Enhanced Setup (Optional - choose one)
```env
# Option 1: OpenRouter (connects Claude Max/Pro subscriptions)
OPENROUTER_API_KEY=your-key-here

# Option 2: Anthropic Direct API (pay-per-use)  
ANTHROPIC_API_KEY=your-key-here
```

### Backend
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (includes anthropic SDK)
pip install -r requirements.txt

# Copy and edit environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# Start the backend
cd backend
uvicorn app:app --port 8080
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies API calls to the backend on port 8080.

## 🧠 AI Integration

FleetPulse supports **three AI modes** for enhanced fleet intelligence:

### 1. OpenRouter (Recommended 🌟)
- **Use your Claude Max ($100/mo) or Pro ($20/mo) subscription** 
- Connect existing subscription via OpenRouter for free tier usage
- Same Claude model quality without additional per-use charges
- Free tier credits available even without subscription

**Setup:**
1. Visit [openrouter.ai](https://openrouter.ai) and create an account
2. Generate an API key in your dashboard
3. Optionally: Connect your Claude subscription for enhanced usage
4. Configure the key in FleetPulse settings

### 2. Anthropic Direct API
- **Pay-per-use** pricing (~$3 per million tokens)
- Direct access to Anthropic's API
- Most reliable option with full feature set
- Best for high-volume usage with predictable costs

**Setup:**
1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Add credit to your account for billing
3. Configure the key in FleetPulse settings

### 3. Demo Mode
- **No API key required** — works out of the box
- Uses intelligent pattern matching for common fleet queries
- Great for testing and basic fleet analysis
- Automatically activated when no API key is configured

**Features in both modes:**
- Natural language fleet queries
- Data visualizations (charts, graphs)
- Safety analysis and recommendations
- Maintenance predictions
- Cost optimization insights
- Real-time fleet status integration

**Example queries:**
- "Which location has the best safety scores?"
- "Show me vehicles with high idle time"
- "What are the cost-saving recommendations?"
- "How is our fuel efficiency trending?"
- "Any vehicles need maintenance soon?"

## 🤖 Claude Desktop Integration (MCP)

FleetPulse includes a **Model Context Protocol (MCP) server** that allows Claude Desktop and other MCP clients to interact with fleet data conversationally.

### Features
- **Natural Language Queries**: "Which location has the best safety scores?" or "Show me vehicles with high idle time"
- **Rich Formatted Responses**: Markdown tables, insights, and contextual information
- **Real-time Data**: Direct access to live fleet information through the FastAPI backend
- **Fleet Summary Resource**: Claude can read current fleet status for context

### Available MCP Tools
| Tool | Description |
|------|-------------|
| `get_fleet_overview` | Vehicle counts, active/idle status, trip metrics |
| `get_vehicles` | List all vehicles with positions, status, speed, driver |
| `get_vehicle_details(vehicle_id)` | Deep dive into specific vehicle |
| `get_safety_scores` | All drivers' safety scores with violation breakdowns |
| `get_alerts(severity?, limit?)` | Recent alerts with filtering options |
| `get_location_stats(location?)` | Per-location metrics and statistics |
| `get_leaderboard` | Gamification rankings and achievements |
| `query_fleet(question)` | Natural language query processing with AI insights |
| `get_recommendations` | AI-generated cost-saving and safety recommendations |

### Setup Instructions

1. **Start FleetPulse backend** (must be running on localhost:8080):
   ```bash
   cd backend && uvicorn app:app --port 8080
   ```

2. **Test the MCP server**:
   ```bash
   cd mcp-server
   source venv/bin/activate
   python test_server.py
   ```

3. **Configure Claude Desktop**:
   
   **Linux**: `~/.config/claude-desktop/config.json`
   
   **macOS**: `~/Library/Application Support/Claude/config.json`
   
   ```json
   {
     "mcpServers": {
       "fleetpulse": {
         "command": "python",
         "args": ["mcp-server/server.py"],
         "cwd": "/path/to/FleetPulse",
         "env": {
           "FLEETPULSE_API_URL": "http://localhost:8080/api"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** and look for "FleetPulse" in the MCP servers list

### Example Queries
- "Show me the current fleet status"
- "Which vehicles are currently active?"
- "What are the safety scores for all drivers?"
- "Give me recommendations to improve efficiency"
- "Show alerts from the last hour"
- "Which location has the most idle time?"

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/dashboard/overview` | Fleet KPIs |
| `GET /api/dashboard/locations` | Per-location stats |
| `GET /api/vehicles/` | All vehicles with positions |
| `GET /api/vehicles/{id}` | Single vehicle |
| `GET /api/safety/scores` | Safety scores per vehicle |
| `GET /api/alerts/recent` | Exception-based alerts |
| `GET /api/gamification/leaderboard` | Driver rankings |
| `GET /api/gamification/challenges` | Active challenges |
| `GET /api/gamification/location-rankings` | Location competition |
| `GET /api/monitor/alerts` | Agentic monitor alerts |
| `GET /api/monitor/status` | Monitor status & patterns |
| `POST /api/monitor/check` | Trigger manual check |
| **🧠 AI Endpoints** |
| `POST /api/ai/chat` | **Claude AI-powered chat** (with conversation history) |
| `POST /api/ai/chat/stream` | **Streaming AI responses** (Server-Sent Events) |
| `GET /api/ai/config` | Get AI configuration status |
| `POST /api/ai/config` | Set Anthropic API key (memory only) |
| `POST /api/ai/query` | Legacy natural language queries (pattern matching fallback) |
| `GET /api/ai/insights` | AI-generated recommendations |

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, mygeotab SDK, Pydantic v2
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Leaflet, Recharts
- **Telemetry:** GeoTab API (50 vehicles, real-time DeviceStatusInfo, Trips, ExceptionEvents)
- **Architecture:** REST API with background agentic monitoring thread

## 📂 Project Structure

```
FleetPulse/
├── backend/
│   ├── app.py                    # FastAPI app with CORS, router registration
│   ├── geotab_client.py          # GeoTab API wrapper with auth caching
│   ├── models.py                 # Pydantic v2 response models
│   ├── routers/                  # API route handlers
│   │   ├── dashboard.py
│   │   ├── vehicles.py
│   │   ├── safety.py
│   │   ├── gamification.py
│   │   ├── alerts.py
│   │   ├── monitor.py            # Agentic monitor endpoints
│   │   └── ai_chat.py            # Natural language query processing
│   └── services/                 # Business logic
│       ├── fleet_service.py      # Vehicle tracking, fleet overview
│       ├── safety_service.py     # Safety scoring, trend analysis
│       ├── gamification_service.py # Points, badges, leaderboards
│       ├── alert_service.py      # Exception-based alerting
│       └── monitor_service.py    # 🤖 Agentic anomaly detection
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # Main layout
│   │   ├── hooks/useGeotab.ts    # Data fetching hooks with auto-refresh
│   │   ├── types/fleet.ts        # TypeScript interfaces
│   │   └── components/           # UI components
│   │       ├── Dashboard.tsx     # KPI cards
│   │       ├── FleetMap.tsx      # Leaflet map
│   │       ├── AlertFeed.tsx     # Alert stream
│   │       ├── SafetyScorecard.tsx
│   │       ├── Leaderboard.tsx
│   │       ├── VehicleList.tsx
│   │       ├── LocationCard.tsx
│   │       └── AgenticMonitor.tsx # 🤖 Monitor UI
│   └── vite.config.ts            # Proxy → backend:8080
├── mcp-server/                   # 🤖 Model Context Protocol server
│   ├── server.py                 # MCP server for Claude Desktop integration
│   ├── test_server.py            # Test suite for MCP functionality
│   ├── claude_desktop_config.json # Claude Desktop configuration example
│   └── venv/                     # Python virtual environment
├── scripts/                      # Setup scripts (zones, drivers)
├── requirements.txt
└── README.md
```

## 👥 Team

Built by **Vex** for the GeoTab Hackathon 2026.

## 📜 License

MIT

---

## 🔌 MyGeotab Add-In

FleetPulse includes a MyGeotab Add-In that runs **inside** the MyGeotab portal.

### Installation

1. In MyGeotab, go to **Administration → System Settings → Add-Ins**
2. Click **New Add-In** and paste the contents of `addin/config.json`
   - Or, if hosting the add-in files on a server, update the `url` fields to point to your hosted `addin/fleetpulse/` directory
3. Save and refresh MyGeotab — "FleetPulse" will appear in the navigation

### How It Works

- When loaded inside MyGeotab, the add-in receives the `api` and `state` objects from the SDK
- It calls the Geotab API directly (Get Device, Get Trip, Get ExceptionEvent) to render KPIs, vehicle lists, and safety data
- A "Full Dashboard" mode embeds the live FleetPulse web app in an iframe
- Works in standalone mode too (fetches from the FleetPulse API)

### Files

| File | Purpose |
|------|---------|
| `addin/config.json` | MyGeotab Add-In manifest (pages, icons, navigation) |
| `addin/fleetpulse/index.html` | The Add-In page (HTML/JS/CSS, no build step) |

---

## 📊 Data Connector Integration

FleetPulse integrates with the **Geotab Data Connector** (OData v4) for pre-aggregated fleet analytics.

### Activation

The Data Connector must be activated on your database:

1. In MyGeotab → **Administration → System Settings → Add-Ins**
2. Add: `{"url": "https://app.geotab.com/addins/geotab/dataConnector/manifest.json"}`
3. Save and wait 2-3 hours for the data pipeline to backfill

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/data-connector/tables` | List available OData tables |
| `GET /api/data-connector/vehicle-kpis?days=14` | Per-vehicle utilization: distance, drive/idle hours, trips, fuel |
| `GET /api/data-connector/safety-scores?days=14` | Fleet and vehicle safety scores |
| `GET /api/data-connector/fault-trends?days=14` | Fault code frequency and trends |
| `GET /api/data-connector/trip-summary?days=14` | Trip aggregates per vehicle |

### Frontend

Navigate to the **Connector** tab in the FleetPulse dashboard to see:
- Fleet utilization KPIs (distance, drive hours, idle hours, utilization %)
- Per-vehicle utilization table
- Aggregated safety scores
- Fault code trends
