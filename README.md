<![CDATA[<div align="center">

# 🚗💨 FleetPulse

### **Real-Time Fleet Intelligence for the Streets of Las Vegas**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com)
[![Geotab](https://img.shields.io/badge/Geotab_API-FF6B00?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2Zy8+&logoColor=white)](https://developers.geotab.com)

---

**FleetPulse** is a multi-location fleet intelligence platform built for the [Geotab Vibe Coding Competition 2026](https://www.geotab.com).  
It monitors **8 Budget Rent a Car locations across Las Vegas** in real time — combining live vehicle tracking, AI-powered anomaly detection, and driver gamification into a single, beautiful dashboard.

> *"We don't just track vehicles. We make fleets smarter, drivers safer, and operations effortless."*

[🚀 Quick Start](#-quick-start) · [📖 Features](#-the-three-pillars) · [🏗️ Architecture](#%EF%B8%8F-architecture) · [📡 API Docs](#-api-documentation)

</div>

---

## 🏆 The Three Pillars

FleetPulse is built around three core experiences:

### 1️⃣ Fleet Intelligence Dashboard
> *Complete operational awareness at a glance*

A real-time command center showing all 8 Budget locations on an interactive map. Track every vehicle's position, status, speed, and location assignment — updated live from the Geotab API.

- 🗺️ **Live Map** — Leaflet-powered map with vehicle markers, geofences, and location clusters
- 📊 **Fleet Overview** — Active/idle/parked/offline counts, trip stats, distance metrics
- 📍 **Per-Location Breakdown** — Vehicle counts, safety scores, and activity per branch
- 🔍 **Vehicle Detail** — Drill into any vehicle for position, odometer, last contact, and trip history

### 2️⃣ Agentic Fleet Monitor
> *Intelligent alerts that think before they scream*

A rules-based anomaly detection engine that monitors exception events from Geotab and surfaces actionable alerts — not noise.

- 🚨 **Smart Alerts** — Speed violations, geofence breaches, after-hours usage, extended idling
- ⚙️ **Configurable Rules** — Enable/disable rules, adjust thresholds via API
- 📈 **Severity Tiers** — Low → Medium → High → Critical, with intelligent categorization
- 🔔 **Real-Time Feed** — Latest 100 alerts with vehicle context, sorted by recency

### 3️⃣ FleetChamp — Driver Gamification
> *Turn safe driving into a competition worth winning*

A gamification layer that scores drivers on safety, awards badges, runs weekly challenges, and ranks locations against each other.

- 🏅 **Driver Leaderboard** — Points-based ranking derived from safety scores
- 🎖️ **Badge System** — Speed Demon Free 🏅, Smooth Operator 🎯, Eco Champion 🌿, Perfect Week ⭐, Road Warrior 🛣️
- 🎯 **Weekly Challenges** — "Zero Speeding" and "Safe Week" challenges with progress tracking
- 🏢 **Location Rankings** — Which Budget branch has the safest drivers? Now there's a scoreboard.

---

## 🖼️ Screenshots

<div align="center">

| | |
|:---:|:---:|
| ![Dashboard](https://via.placeholder.com/600x350/1a1a2e/00d4aa?text=Fleet+Intelligence+Dashboard) | ![Map View](https://via.placeholder.com/600x350/1a1a2e/ff6b6b?text=Live+Vehicle+Map) |
| **Fleet Intelligence Dashboard** — Real-time overview of all 8 locations with KPI cards, trip stats, and fleet status breakdown | **Live Vehicle Map** — Interactive Leaflet map showing vehicle positions, geofences, and location clusters across Las Vegas |
| ![Safety](https://via.placeholder.com/600x350/1a1a2e/ffd93d?text=Safety+Scorecard) | ![Leaderboard](https://via.placeholder.com/600x350/1a1a2e/6bcb77?text=FleetChamp+Leaderboard) |
| **Safety Scorecard** — Per-vehicle safety scores with incident breakdowns, trend indicators, and risk rankings | **FleetChamp Leaderboard** — Driver rankings, earned badges, weekly challenges, and inter-location competition |
| ![Alerts](https://via.placeholder.com/600x350/1a1a2e/4ecdc4?text=Alert+Feed) | ![Locations](https://via.placeholder.com/600x350/1a1a2e/ff8a5c?text=Location+Cards) |
| **Alert Feed** — Real-time anomaly alerts with severity badges, vehicle context, and configurable rules | **Location Cards** — Per-branch stats showing vehicle counts, active units, and safety performance |

</div>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FleetPulse Platform                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  React + TypeScript Frontend              │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │   │
│   │  │Dashboard │ │ FleetMap │ │  Safety  │ │FleetChamp │  │   │
│   │  │ Overview │ │ (Leaflet)│ │Scorecard │ │Leaderboard│  │   │
│   │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │   │
│   │       └─────────────┴────────────┴─────────────┘         │   │
│   │                        Tailwind CSS                       │   │
│   └──────────────────────────┬──────────────────────────────┘   │
│                              │ HTTP/REST                         │
│   ┌──────────────────────────▼──────────────────────────────┐   │
│   │                   FastAPI Backend                         │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │   │
│   │  │Dashboard │ │ Vehicle  │ │  Safety  │ │  Alert    │  │   │
│   │  │ Router   │ │  Router  │ │  Router  │ │  Router   │  │   │
│   │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │   │
│   │       └─────────────┴────────────┴─────────────┘         │   │
│   │                    Service Layer                          │   │
│   │  ┌────────────┐ ┌────────────┐ ┌─────────────────────┐  │   │
│   │  │   Fleet    │ │   Safety   │ │   Gamification      │  │   │
│   │  │  Service   │ │  Service   │ │     Service         │  │   │
│   │  └────────────┘ └────────────┘ └─────────────────────┘  │   │
│   └──────────────────────────┬──────────────────────────────┘   │
│                              │ mygeotab SDK                      │
│   ┌──────────────────────────▼──────────────────────────────┐   │
│   │              GeotabClient (Singleton)                     │   │
│   │     Auto-auth • Session caching • Re-auth on expiry      │   │
│   └──────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
└──────────────────────────────┼──────────────────────────────────┘
                               │ HTTPS
                    ┌──────────▼──────────┐
                    │   Geotab MyGeotab   │
                    │   Cloud Platform    │
                    │  (my.geotab.com)    │
                    └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | Interactive SPA |
| **Styling** | Tailwind CSS | Utility-first responsive design |
| **Mapping** | Leaflet + React Leaflet | Live vehicle map with geofences |
| **Backend** | FastAPI (Python 3.12) | High-performance async REST API |
| **Telematics** | Geotab SDK (`mygeotab`) | Vehicle data, trips, exceptions, zones |
| **Validation** | Pydantic v2 | Request/response models with strict typing |
| **Build** | Vite | Lightning-fast frontend builds |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Geotab account with API access

### 1. Clone & configure

```bash
git clone https://github.com/0x000NULL/FleetPulse.git
cd FleetPulse

# Create your environment file
cp .env.example .env
# Edit .env with your Geotab credentials:
#   GEOTAB_DATABASE=your_database
#   GEOTAB_USERNAME=your_email
#   GEOTAB_PASSWORD=your_password
#   GEOTAB_SERVER=my.geotab.com
```

### 2. Start the backend

```bash
pip install -r requirements.txt

# (Optional) Set up geofences and seed driver data
python scripts/setup_zones.py
python scripts/seed_drivers.py

# Run the API server
cd backend
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the dashboard

Navigate to **http://localhost:5173** — you're live! 🎉

---

## 📡 API Documentation

Once the backend is running, visit **http://localhost:8080/docs** for the interactive Swagger UI.

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health check |
| `GET` | `/api/dashboard/overview` | Fleet-wide KPIs and trip statistics |
| `GET` | `/api/dashboard/locations` | Per-location vehicle counts and safety scores |
| `GET` | `/api/vehicles/` | All vehicles with position, status, and location |
| `GET` | `/api/vehicles/{id}` | Single vehicle detail |
| `GET` | `/api/safety/scores?days=7` | Per-vehicle safety scores with trend analysis |
| `GET` | `/api/gamification/leaderboard` | Driver leaderboard with points and badges |
| `GET` | `/api/gamification/challenges` | Active weekly challenges |
| `GET` | `/api/gamification/location-rankings` | Inter-location safety competition |
| `GET` | `/api/alerts/recent?hours=24` | Recent anomaly alerts |
| `GET` | `/api/alerts/rules` | Configured alert rules |
| `PATCH` | `/api/alerts/rules/{id}` | Update alert rule (enable/disable, threshold) |

---

## 🏅 Prize Categories

FleetPulse is designed to compete across multiple categories:

### 🎨 Vibe Master
> *Best overall experience and polish*

FleetPulse delivers a cohesive, beautiful experience — from the real-time map to the gamification leaderboard. Every screen is designed with Tailwind CSS for a modern, responsive feel.

### 💡 Innovator
> *Most creative use of the Geotab platform*

We go beyond basic tracking: safety scoring algorithms, driver gamification with badges and challenges, multi-location competition, and intelligent alert classification — all powered by Geotab exception events and device telemetry.

### 🤝 Most Collaborative
> *Best team effort and community contribution*

Built as a fully open-source solution that any multi-location fleet can deploy. Clean architecture, typed APIs, and comprehensive documentation make FleetPulse easy to extend and contribute to.

---

## 🏢 The Real Fleet Behind FleetPulse

<div align="center">

**This isn't a demo — it's built for a real fleet.**

</div>

FleetPulse was built by **Ethan Aldrich**, CTO of **Budget Rent a Car Las Vegas**, to solve a real problem: managing vehicles across **8 rental locations** spread across the Las Vegas metro area.

| # | Location | Area |
|---|----------|------|
| 1 | W Sahara | West Las Vegas |
| 2 | Golden Nugget | Downtown / Fremont |
| 3 | Center Strip | The Strip |
| 4 | Tropicana | South Strip |
| 5 | LAS Airport | McCarran / Harry Reid |
| 6 | Gibson | Southeast |
| 7 | Henderson Executive | Henderson |
| 8 | Losee | North Las Vegas |

When you're running a fleet across 8 locations in a city that never sleeps, you need more than a spreadsheet. You need **FleetPulse**.

---

## 🙏 Credits & Acknowledgments

- **[Geotab](https://www.geotab.com)** — For the incredible telematics platform and SDK that makes this possible
- **[Geotab Vibe Coding Competition 2026](https://www.geotab.com)** — For inspiring builders to push fleet tech forward
- **[Google Cloud](https://cloud.google.com)** — Infrastructure and compute
- The open-source community behind FastAPI, React, Leaflet, Tailwind, and every dependency that powers this project

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with 🎰 in Las Vegas**

*FleetPulse — Because every mile matters.*

</div>
]]>