<![CDATA[# 🚗 FleetPulse — Multi-Location Fleet Intelligence Dashboard

> **GeoTab Vibe Coding Competition Entry**
> Real-time fleet monitoring, safety scoring, and driver gamification for Budget Rent a Car Las Vegas (8 locations)

![Dashboard Preview](docs/screenshots/dashboard.png)

## 🎯 What is FleetPulse?

FleetPulse transforms raw Geotab telematics data into actionable fleet intelligence. Built for a car rental company managing 8 locations across Las Vegas, it combines:

- **📊 Real-time Fleet Dashboard** — Live vehicle positions, status, and KPIs
- **🛡️ Safety Scoring** — Per-vehicle and per-driver safety scores (0-100) based on exception events
- **🏆 Driver Gamification** — Leaderboards, badges, and weekly challenges that make safe driving fun
- **🚨 Agentic Monitoring** — Anomaly detection with configurable alert rules
- **📍 Multi-Location Analytics** — Per-site breakdown across all 8 Budget locations

## 📍 Covered Locations

| # | Location | Address |
|---|----------|---------|
| 1 | W Sahara | 3029 W Sahara Ave, Las Vegas, NV 89102 |
| 2 | Golden Nugget | 129 E Fremont St, Las Vegas, NV 89101 |
| 3 | Center Strip | 3735 S Las Vegas Blvd, Las Vegas, NV 89109 |
| 4 | Tropicana | 3801 S Las Vegas Blvd, Las Vegas, NV 89109 |
| 5 | LAS Airport | 7135 Gilespie St, Las Vegas, NV 89119 |
| 6 | Gibson | 7120 S Haven St, Las Vegas, NV 89119 |
| 7 | Henderson Executive | 3500 Executive Terminal Dr, Henderson, NV 89052 |
| 8 | Losee | 2430 Losee Rd, North Las Vegas, NV 89030 |

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React + Vite  │────▶│  FastAPI Backend  │────▶│   Geotab API    │
│   Tailwind CSS  │     │  Python 3.11+     │     │  my.geotab.com  │
│   Leaflet Maps  │     │  Pydantic Models  │     │                 │
│   Recharts      │     │  Async Services   │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Geotab account credentials

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
cp ../.env.example ../.env  # Edit with your Geotab creds
uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Setup Geofences
```bash
cd scripts
python setup_zones.py   # Creates geofences for all 8 locations
python seed_drivers.py  # Seeds driver profiles
```

## 🏆 Gamification Features

- **Points System** — Earn points for safe driving, lose them for incidents
- **Badges** — "Speed Demon Free" 🏅, "Smooth Operator" 🎯, "Eco Champion" 🌿
- **Weekly Challenges** — Compete for top driver of the week
- **Location vs Location** — Which Budget site has the safest fleet?

## 📸 Screenshots

> _Screenshots coming soon — the dashboard is live and beautiful!_

| Dashboard | Fleet Map | Leaderboard |
|-----------|-----------|-------------|
| ![](docs/screenshots/dashboard.png) | ![](docs/screenshots/map.png) | ![](docs/screenshots/leaderboard.png) |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Maps | Leaflet + React-Leaflet |
| Charts | Recharts |
| Backend | FastAPI, Python 3.11 |
| Telematics | Geotab SDK (mygeotab) |
| Data | Pydantic v2 models |

## 📄 License

MIT — Built with ❤️ for the GeoTab Vibe Coding Competition
]]>