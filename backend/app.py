"""FleetPulse — FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import dashboard, vehicles, safety, gamification, alerts

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


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FleetPulse"}
