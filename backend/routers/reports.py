"""PDF Fleet Report generation endpoints."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from fastapi import APIRouter, Response
from typing import Any

from geotab_client import GeotabClient
from _cache import get_cached, set_cached

router = APIRouter()


def _build_html_report(fleet_data: dict[str, Any], period: str) -> str:
    """Build an HTML fleet report that can be rendered as PDF on the frontend."""
    now = datetime.now(timezone.utc)
    
    devices = fleet_data.get("devices", [])
    trips = fleet_data.get("trips", [])
    exceptions = fleet_data.get("exceptions", [])
    
    total_vehicles = len(devices)
    total_trips = len(trips)
    
    # Calculate total distance
    total_distance_km = sum(
        (t.get("distance", 0) or 0) for t in trips
    )
    total_distance_mi = total_distance_km * 0.621371
    
    # Exception breakdown
    exception_counts: dict[str, int] = {}
    for ex in exceptions:
        rule = ex.get("rule", {})
        name = rule.get("name", "Unknown") if isinstance(rule, dict) else str(rule)
        exception_counts[name] = exception_counts.get(name, 0) + 1
    
    top_exceptions = sorted(exception_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Vehicle utilization
    active_device_ids = set()
    for t in trips:
        dev = t.get("device", {})
        if isinstance(dev, dict):
            active_device_ids.add(dev.get("id", ""))
    
    utilization_pct = (len(active_device_ids) / total_vehicles * 100) if total_vehicles else 0
    
    # Build vehicle summary rows
    vehicle_rows = ""
    device_trip_counts: dict[str, dict] = {}
    for t in trips:
        dev = t.get("device", {})
        dev_id = dev.get("id", "") if isinstance(dev, dict) else ""
        if dev_id not in device_trip_counts:
            device_trip_counts[dev_id] = {"trips": 0, "distance": 0}
        device_trip_counts[dev_id]["trips"] += 1
        device_trip_counts[dev_id]["distance"] += (t.get("distance", 0) or 0)
    
    for d in devices[:20]:  # Top 20 vehicles
        d_id = d.get("id", "")
        d_name = d.get("name", "Unknown")
        stats = device_trip_counts.get(d_id, {"trips": 0, "distance": 0})
        dist_mi = stats["distance"] * 0.621371
        vehicle_rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #e5e7eb">{d_name}</td>
            <td style="padding:8px;border-bottom:1px solid #e5e7eb;text-align:center">{stats['trips']}</td>
            <td style="padding:8px;border-bottom:1px solid #e5e7eb;text-align:right">{dist_mi:,.0f} mi</td>
        </tr>"""
    
    exception_rows = ""
    for name, count in top_exceptions:
        exception_rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #e5e7eb">{name}</td>
            <td style="padding:8px;border-bottom:1px solid #e5e7eb;text-align:center">{count}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>FleetPulse Report - {period}</title>
<style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; color: #1f2937; margin: 0; padding: 40px; background: white; }}
    .header {{ background: linear-gradient(135deg, #1e40af, #7c3aed); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
    .header h1 {{ margin: 0; font-size: 28px; }}
    .header p {{ margin: 5px 0 0; opacity: 0.8; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }}
    .kpi-card {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; text-align: center; }}
    .kpi-value {{ font-size: 32px; font-weight: bold; color: #1e40af; }}
    .kpi-label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }}
    .section {{ margin-bottom: 30px; }}
    .section h2 {{ font-size: 18px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: #f3f4f6; padding: 10px 8px; text-align: left; font-size: 12px; text-transform: uppercase; color: #6b7280; }}
    .footer {{ text-align: center; color: #9ca3af; font-size: 11px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
    .badge-green {{ background: #d1fae5; color: #065f46; }}
    .badge-yellow {{ background: #fef3c7; color: #92400e; }}
    .badge-red {{ background: #fee2e2; color: #991b1b; }}
    @media print {{ body {{ padding: 20px; }} .header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body>
    <div class="header">
        <h1>🚗 FleetPulse Report</h1>
        <p>Budget Rent a Car · Las Vegas · {period} Report</p>
        <p>Generated: {now.strftime('%B %d, %Y at %I:%M %p UTC')}</p>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">{total_vehicles}</div>
            <div class="kpi-label">Total Vehicles</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{total_trips}</div>
            <div class="kpi-label">Total Trips</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{total_distance_mi:,.0f}</div>
            <div class="kpi-label">Miles Driven</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{utilization_pct:.0f}%</div>
            <div class="kpi-label">Fleet Utilization</div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Vehicle Activity Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Vehicle</th>
                    <th style="text-align:center">Trips</th>
                    <th style="text-align:right">Distance</th>
                </tr>
            </thead>
            <tbody>{vehicle_rows if vehicle_rows else '<tr><td colspan="3" style="padding:20px;text-align:center;color:#9ca3af">No trip data for this period</td></tr>'}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>⚠️ Safety Exception Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Exception Type</th>
                    <th style="text-align:center">Count</th>
                </tr>
            </thead>
            <tbody>{exception_rows if exception_rows else '<tr><td colspan="2" style="padding:20px;text-align:center;color:#9ca3af">No exceptions for this period</td></tr>'}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>📈 Fleet Health Overview</h2>
        <p>During this {period.lower()} period, the fleet maintained a <span class="badge {'badge-green' if utilization_pct > 70 else 'badge-yellow' if utilization_pct > 40 else 'badge-red'}">{utilization_pct:.0f}% utilization rate</span>.</p>
        <p>A total of <strong>{len(exceptions)}</strong> safety exceptions were recorded across <strong>{total_trips}</strong> trips, 
        resulting in an exception rate of <strong>{(len(exceptions)/max(total_trips,1)*100):.1f}%</strong> per trip.</p>
    </div>

    <div class="footer">
        <p>FleetPulse · Powered by Geotab · Budget Rent a Car Las Vegas</p>
        <p>This report was auto-generated. For questions, contact fleet operations.</p>
    </div>
</body>
</html>"""
    return html


@router.get("/generate")
async def generate_report(period: str = "weekly"):
    """Generate fleet report data as HTML (rendered to PDF on frontend via print)."""
    cache_key = f"report:{period}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    try:
        client = GeotabClient.get()
        now = datetime.now(timezone.utc)
        
        if period == "daily":
            from_date = now - timedelta(days=1)
        elif period == "monthly":
            from_date = now - timedelta(days=30)
        else:  # weekly
            from_date = now - timedelta(days=7)
        
        devices = client.get_devices()
        trips = client.get_trips(from_date=from_date, to_date=now)
        exceptions = client.get_exception_events(from_date=from_date, to_date=now)
        
        fleet_data = {
            "devices": devices,
            "trips": trips,
            "exceptions": exceptions,
        }
        
        html = _build_html_report(fleet_data, period.capitalize())
        
        result = {
            "html": html,
            "period": period,
            "generated_at": now.isoformat(),
            "summary": {
                "total_vehicles": len(devices),
                "total_trips": len(trips),
                "total_exceptions": len(exceptions),
                "total_distance_mi": sum((t.get("distance", 0) or 0) for t in trips) * 0.621371,
            }
        }
        
        set_cached(cache_key, result, ttl=300)
        return result
        
    except Exception as e:
        return {
            "html": f"<h1>Report Generation Error</h1><p>{str(e)}</p>",
            "period": period,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {},
            "error": str(e)
        }
