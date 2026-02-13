"""FleetPulse — FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import dashboard, vehicles, safety, gamification, alerts, monitor, ai_chat, coaching, maintenance, trips, reports, geofences, fuel, compliance, data_connector

app = FastAPI(
    title="FleetPulse API",
    description="Multi-location fleet intelligence for Budget Rent a Car Las Vegas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(safety.router, prefix="/api/safety", tags=["Safety"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["Gamification"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["Agentic Monitor"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["AI Chat & Intelligence"])
app.include_router(coaching.router, prefix="/api/coaching", tags=["Driver Coaching"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["Predictive Maintenance"])
app.include_router(trips.router, prefix="/api/trips", tags=["Route Replay"])
app.include_router(reports.router, prefix="/api/reports", tags=["Fleet Reports"])
app.include_router(geofences.router, prefix="/api/geofences", tags=["Geofence Management"])
app.include_router(fuel.router, prefix="/api/fuel", tags=["Fuel Analytics"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance & ELD"])
app.include_router(data_connector.router, prefix="/api/data-connector", tags=["Data Connector"])


@app.on_event("startup")
async def startup_event():
    from services.monitor_service import start_monitor
    start_monitor()


@app.on_event("shutdown")
async def shutdown_event():
    from services.monitor_service import stop_monitor
    stop_monitor()


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FleetPulse"}
