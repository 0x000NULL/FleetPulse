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

### Environment Variables
```env
GEOTAB_DATABASE=demo_fleetpulse
GEOTAB_USERNAME=your_username
GEOTAB_PASSWORD=your_password
GEOTAB_SERVER=my.geotab.com
```

### Backend
```bash
pip install -r requirements.txt
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
│   │   └── monitor.py            # Agentic monitor endpoints
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
├── scripts/                      # Setup scripts (zones, drivers)
├── requirements.txt
└── README.md
```

## 👥 Team

Built by **Vex** for the GeoTab Hackathon 2026.

## 📜 License

MIT
