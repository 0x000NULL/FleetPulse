#!/usr/bin/env python3
"""FleetPulse MCP Server - Model Context Protocol server for fleet management data.

This MCP server provides conversational access to FleetPulse fleet management data
through the Model Context Protocol, allowing Claude Desktop and other MCP clients 
to interact with fleet data naturally.

Usage:
    python server.py

Configuration:
    Set FLEETPULSE_API_URL environment variable (defaults to http://localhost:8080/api)
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
import traceback

import requests
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fleetpulse-mcp")

# Configuration
API_BASE_URL = os.getenv("FLEETPULSE_API_URL", "http://localhost:8080/api")
REQUEST_TIMEOUT = 10  # seconds


class FleetPulseAPI:
    """Client for FleetPulse API endpoints."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API endpoint."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {url} - {e}")
            raise Exception(f"Failed to fetch data from {endpoint}: {str(e)}")
    
    def _make_post_request(self, endpoint: str, data: Dict) -> Dict:
        """Make HTTP POST request to API endpoint."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(
                url, 
                json=data, 
                timeout=REQUEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {url} - {e}")
            raise Exception(f"Failed to post data to {endpoint}: {str(e)}")
    
    def get_fleet_overview(self) -> Dict:
        """Get fleet overview statistics."""
        return self._make_request("/dashboard/overview")
    
    def get_vehicles(self) -> List[Dict]:
        """Get list of all vehicles."""
        return self._make_request("/vehicles/")
    
    def get_vehicle_details(self, vehicle_id: str) -> Dict:
        """Get details for specific vehicle."""
        return self._make_request(f"/vehicles/{vehicle_id}")
    
    def get_safety_scores(self) -> List[Dict]:
        """Get safety scores for all drivers."""
        return self._make_request("/safety/scores")
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get recent alerts, optionally filtered by severity."""
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        return self._make_request("/alerts/", params)
    
    def get_location_stats(self, location: Optional[str] = None) -> List[Dict]:
        """Get location statistics."""
        data = self._make_request("/dashboard/locations")
        if location:
            # Filter by location name (case-insensitive partial match)
            location_lower = location.lower()
            return [loc for loc in data if location_lower in loc.get('name', '').lower()]
        return data
    
    def get_leaderboard(self) -> List[Dict]:
        """Get gamification leaderboard."""
        return self._make_request("/gamification/leaderboard")
    
    def query_fleet(self, question: str) -> Dict:
        """Process natural language query about fleet data."""
        payload = {"message": question}
        return self._make_post_request("/ai/query", payload)
    
    def get_recommendations(self) -> List[Dict]:
        """Get AI-generated fleet optimization recommendations."""
        return self._make_request("/ai/insights")
    
    def get_analytics_summary(self) -> Dict:
        """Get comprehensive analytics summary."""
        return self._make_request("/ai/analytics/summary")


def format_table(headers: List[str], rows: List[List[str]], max_width: int = 100) -> str:
    """Format data as a markdown table."""
    if not headers or not rows:
        return "_No data available_"
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Truncate if table would be too wide
    total_width = sum(col_widths) + len(headers) * 3 - 1
    if total_width > max_width:
        # Reduce column widths proportionally
        reduction = (total_width - max_width) / len(col_widths)
        col_widths = [max(8, int(w - reduction)) for w in col_widths]
    
    # Build table
    lines = []
    
    # Header
    header_line = "|" + "|".join(f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)) + "|"
    lines.append(header_line)
    
    # Separator
    sep_line = "|" + "|".join(f" {'-' * col_widths[i]} " for i in range(len(headers))) + "|"
    lines.append(sep_line)
    
    # Rows
    for row in rows:
        row_cells = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)[:col_widths[i]]  # Truncate if needed
                row_cells.append(f" {cell_str:<{col_widths[i]}} ")
        lines.append("|" + "|".join(row_cells) + "|")
    
    return "\n".join(lines)


def format_fleet_overview(data: Dict) -> str:
    """Format fleet overview data as markdown."""
    result = "# Fleet Overview\n\n"
    
    # Vehicle status summary
    result += "## Vehicle Status\n"
    status_rows = [
        ["Active", str(data.get('active', 0))],
        ["Idle", str(data.get('idle', 0))],
        ["Parked", str(data.get('parked', 0))],
        ["Offline", str(data.get('offline', 0))],
        ["**Total**", f"**{data.get('total_vehicles', 0)}**"]
    ]
    result += format_table(["Status", "Count"], status_rows) + "\n\n"
    
    # Trip metrics
    result += "## Today's Metrics\n"
    metrics_rows = [
        ["Total Trips", str(data.get('total_trips_today', 0))],
        ["Total Distance", f"{data.get('total_distance_km', 0):.1f} km"],
        ["Avg Trip Duration", f"{data.get('avg_trip_duration_min', 0):.1f} min"],
        ["Avg Trip Distance", f"{data.get('avg_trip_distance_km', 0):.1f} km"]
    ]
    result += format_table(["Metric", "Value"], metrics_rows) + "\n\n"
    
    return result


def format_vehicles_list(data: List[Dict]) -> str:
    """Format vehicles list as markdown table."""
    result = "# Vehicle Fleet Status\n\n"
    
    if not data:
        return result + "_No vehicles found_\n"
    
    rows = []
    for vehicle in data:
        position = vehicle.get('position', {})
        speed = f"{position.get('speed', 0):.0f} km/h" if position else "0 km/h"
        location = vehicle.get('location_name') or 'Unknown'
        last_contact = vehicle.get('last_contact', 'Never')
        if last_contact != 'Never' and 'T' in str(last_contact):
            last_contact = str(last_contact).split('T')[0]  # Show just date
        
        rows.append([
            vehicle.get('id', 'N/A'),
            vehicle.get('name', 'Unnamed'),
            vehicle.get('status', 'unknown').title(),
            location,
            speed,
            last_contact
        ])
    
    result += format_table(
        ["ID", "Name", "Status", "Location", "Speed", "Last Contact"], 
        rows
    ) + "\n\n"
    
    result += f"**Total Vehicles:** {len(data)}\n"
    
    return result


def format_vehicle_details(data: Dict) -> str:
    """Format single vehicle details as markdown."""
    result = f"# Vehicle Details: {data.get('name', 'Unknown')}\n\n"
    
    # Basic info
    basic_info = [
        ["ID", data.get('id', 'N/A')],
        ["Name", data.get('name', 'Unnamed')],
        ["Status", data.get('status', 'unknown').title()],
        ["Odometer", f"{data.get('odometer_km', 0):.1f} km"]
    ]
    result += "## Basic Information\n"
    result += format_table(["Field", "Value"], basic_info) + "\n\n"
    
    # Position info if available
    position = data.get('position')
    if position:
        result += "## Current Position\n"
        position_info = [
            ["Latitude", f"{position.get('latitude', 0):.6f}"],
            ["Longitude", f"{position.get('longitude', 0):.6f}"],
            ["Speed", f"{position.get('speed', 0):.1f} km/h"],
            ["Bearing", f"{position.get('bearing', 0):.0f}°"]
        ]
        result += format_table(["Field", "Value"], position_info) + "\n\n"
    
    if data.get('location_name'):
        result += f"**Current Location:** {data['location_name']}\n\n"
    
    if data.get('last_contact'):
        result += f"**Last Contact:** {data['last_contact']}\n\n"
    
    return result


def format_safety_scores(data: List[Dict]) -> str:
    """Format safety scores as markdown."""
    result = "# Driver Safety Scores\n\n"
    
    if not data:
        return result + "_No safety data available_\n"
    
    # Sort by score (highest first)
    sorted_data = sorted(data, key=lambda x: x.get('score', 0), reverse=True)
    
    rows = []
    for driver in sorted_data:
        breakdown = driver.get('breakdown', {})
        total_violations = sum([
            breakdown.get('speeding', 0),
            breakdown.get('harsh_braking', 0), 
            breakdown.get('harsh_acceleration', 0),
            breakdown.get('harsh_cornering', 0)
        ])
        
        trend = driver.get('trend', 'stable').replace('_', ' ').title()
        score = driver.get('score', 0)
        score_emoji = "🟢" if score >= 90 else "🟡" if score >= 80 else "🔴"
        
        rows.append([
            driver.get('vehicle_name', 'Unknown'),
            f"{score_emoji} {score:.1f}%",
            str(total_violations),
            trend
        ])
    
    result += format_table(
        ["Vehicle/Driver", "Score", "Violations", "Trend"], 
        rows
    ) + "\n\n"
    
    # Summary stats
    avg_score = sum(d.get('score', 0) for d in data) / len(data)
    total_violations = sum(d.get('event_count', 0) for d in data)
    
    result += f"**Fleet Average:** {avg_score:.1f}% | **Total Violations:** {total_violations}\n\n"
    
    return result


def format_alerts(data: List[Dict]) -> str:
    """Format alerts list as markdown."""
    result = "# Recent Fleet Alerts\n\n"
    
    if not data:
        return result + "_No alerts found_\n"
    
    # Group by severity
    by_severity = {"critical": [], "high": [], "medium": [], "low": []}
    for alert in data:
        severity = alert.get('severity', 'low')
        by_severity[severity].append(alert)
    
    for severity in ["critical", "high", "medium", "low"]:
        alerts = by_severity[severity]
        if not alerts:
            continue
            
        emoji = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "ℹ️"}
        result += f"## {emoji[severity]} {severity.upper()} Alerts ({len(alerts)})\n\n"
        
        rows = []
        for alert in alerts[:10]:  # Limit to 10 per severity
            timestamp = alert.get('timestamp', 'Unknown')
            if isinstance(timestamp, str) and 'T' in timestamp:
                timestamp = timestamp.split('T')[0] + ' ' + timestamp.split('T')[1][:8]
            
            status = "✅" if alert.get('acknowledged', False) else "🔴"
            
            rows.append([
                alert.get('vehicle_name', 'Unknown'),
                alert.get('alert_type', 'Unknown'),
                alert.get('message', 'No message'),
                str(timestamp),
                status
            ])
        
        result += format_table(
            ["Vehicle", "Type", "Message", "Time", "Status"], 
            rows
        ) + "\n\n"
    
    return result


def format_location_stats(data: List[Dict]) -> str:
    """Format location statistics as markdown."""
    result = "# Location Statistics\n\n"
    
    if not data:
        return result + "_No location data available_\n"
    
    rows = []
    for location in data:
        safety_score = location.get('safety_score', 0)
        safety_emoji = "🟢" if safety_score >= 90 else "🟡" if safety_score >= 80 else "🔴"
        
        rows.append([
            location.get('name', 'Unknown'),
            str(location.get('vehicle_count', 0)),
            str(location.get('active', 0)),
            f"{safety_emoji} {safety_score:.1f}%"
        ])
    
    result += format_table(
        ["Location", "Total Vehicles", "Active", "Safety Score"], 
        rows
    ) + "\n\n"
    
    total_vehicles = sum(loc.get('vehicle_count', 0) for loc in data)
    active_vehicles = sum(loc.get('active', 0) for loc in data)
    avg_safety = sum(loc.get('safety_score', 0) for loc in data) / len(data)
    
    result += f"**Summary:** {total_vehicles} vehicles across {len(data)} locations | "
    result += f"{active_vehicles} active | Average safety: {avg_safety:.1f}%\n\n"
    
    return result


def format_leaderboard(data: List[Dict]) -> str:
    """Format gamification leaderboard as markdown."""
    result = "# Fleet Gamification Leaderboard\n\n"
    
    if not data:
        return result + "_No leaderboard data available_\n"
    
    rows = []
    for i, driver in enumerate(data, 1):
        rank_emoji = {"1": "🥇", "2": "🥈", "3": "🥉"}.get(str(i), f"#{i}")
        badge_count = len(driver.get('badges', []))
        badge_text = f"({badge_count} badges)" if badge_count > 0 else ""
        
        rows.append([
            rank_emoji,
            driver.get('driver_name', 'Unknown'),
            str(driver.get('points', 0)),
            f"{driver.get('safety_score', 0):.1f}%",
            badge_text
        ])
    
    result += format_table(
        ["Rank", "Driver", "Points", "Safety Score", "Badges"], 
        rows
    ) + "\n\n"
    
    return result


def format_query_response(data: Dict) -> str:
    """Format AI query response as markdown."""
    result = "# Fleet Query Response\n\n"
    
    response_text = data.get('response', 'No response')
    result += f"{response_text}\n\n"
    
    # Include insights if available
    insights = data.get('insights', [])
    if insights:
        result += "## Key Insights\n\n"
        for insight in insights:
            result += f"• {insight}\n"
        result += "\n"
    
    # Include data if available and it's structured
    query_data = data.get('data', [])
    if query_data and isinstance(query_data, list) and query_data:
        result += "## Data\n\n"
        
        # Try to format as table if data has consistent structure
        if isinstance(query_data[0], dict):
            headers = list(query_data[0].keys())
            rows = []
            for item in query_data[:20]:  # Limit to 20 rows
                row = [str(item.get(h, '')) for h in headers]
                rows.append(row)
            result += format_table(headers, rows) + "\n\n"
        else:
            # Fallback to simple list
            for item in query_data[:10]:
                result += f"• {item}\n"
            result += "\n"
    
    confidence = data.get('confidence', 0)
    result += f"**Confidence:** {confidence * 100:.0f}%\n\n"
    
    return result


def format_recommendations(data: List[Dict]) -> str:
    """Format AI recommendations as markdown."""
    result = "# AI Fleet Optimization Recommendations\n\n"
    
    if not data:
        return result + "_No recommendations available_\n"
    
    for i, rec in enumerate(data, 1):
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get('priority', 'medium'), "ℹ️")
        
        result += f"## {i}. {priority_emoji} {rec.get('title', 'Untitled')} ({rec.get('priority', 'medium').upper()})\n\n"
        result += f"**Type:** {rec.get('type', 'general').title()}\n"
        result += f"**Impact:** {rec.get('impact', 'Not specified')}\n"
        result += f"**Action:** {rec.get('action', 'No action specified')}\n\n"
        result += f"{rec.get('message', 'No details available')}\n\n"
        result += "---\n\n"
    
    return result


# Create MCP server instance
server = Server("fleetpulse")
api_client = FleetPulseAPI(API_BASE_URL)


@server.list_resources()
async def list_resources() -> List[types.Resource]:
    """List available MCP resources."""
    return [
        types.Resource(
            uri="fleetpulse://fleet-summary",
            name="Fleet Summary",
            description="Current fleet overview and key metrics",
            mimeType="text/markdown"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read MCP resource content."""
    if uri == "fleetpulse://fleet-summary":
        try:
            overview = api_client.get_fleet_overview()
            vehicles = api_client.get_vehicles()
            
            result = "# FleetPulse Summary\n\n"
            result += format_fleet_overview(overview)
            
            # Add quick vehicle status
            active_vehicles = [v for v in vehicles if v.get('status') == 'active']
            result += f"## Currently Active Vehicles ({len(active_vehicles)})\n\n"
            
            if active_vehicles:
                rows = []
                for v in active_vehicles[:10]:  # Show first 10
                    location = v.get('location_name', 'Unknown')
                    rows.append([v.get('name', 'Unnamed'), location])
                result += format_table(["Vehicle", "Location"], rows)
                if len(active_vehicles) > 10:
                    result += f"\n_... and {len(active_vehicles) - 10} more_"
            else:
                result += "_No vehicles currently active_"
            
            result += f"\n\n**Last Updated:** {json.dumps(overview, indent=2)}\n"
            
            return result
            
        except Exception as e:
            return f"# FleetPulse Summary\n\n**Error:** Could not fetch fleet summary: {str(e)}\n"
    
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available MCP tools."""
    return [
        types.Tool(
            name="get_fleet_overview",
            description="Get fleet overview with vehicle counts, trip statistics, and key metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_vehicles",
            description="Get list of all vehicles with their current status, location, and details",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_vehicle_details",
            description="Get detailed information for a specific vehicle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vehicle_id": {
                        "type": "string",
                        "description": "Vehicle ID to get details for"
                    }
                },
                "required": ["vehicle_id"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_safety_scores",
            description="Get safety scores and violation breakdown for all drivers",
            inputSchema={
                "type": "object", 
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_alerts",
            description="Get recent fleet alerts, optionally filtered by severity",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Filter alerts by severity level"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "description": "Maximum number of alerts to return"
                    }
                },
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_location_stats",
            description="Get statistics for fleet locations",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Filter by specific location name (partial match)"
                    }
                },
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_leaderboard", 
            description="Get gamification leaderboard showing driver rankings and achievements",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="query_fleet",
            description="Ask natural language questions about fleet data and get AI-powered responses",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about fleet operations, safety, efficiency, etc."
                    }
                },
                "required": ["question"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_recommendations",
            description="Get AI-generated fleet optimization and cost-saving recommendations",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle MCP tool calls."""
    
    try:
        if name == "get_fleet_overview":
            data = api_client.get_fleet_overview()
            formatted = format_fleet_overview(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_vehicles":
            data = api_client.get_vehicles()
            formatted = format_vehicles_list(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_vehicle_details":
            vehicle_id = arguments.get("vehicle_id")
            if not vehicle_id:
                return [types.TextContent(type="text", text="Error: vehicle_id is required")]
            
            data = api_client.get_vehicle_details(vehicle_id)
            formatted = format_vehicle_details(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_safety_scores":
            data = api_client.get_safety_scores()
            formatted = format_safety_scores(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_alerts":
            severity = arguments.get("severity")
            limit = arguments.get("limit", 50)
            data = api_client.get_alerts(severity=severity, limit=limit)
            formatted = format_alerts(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_location_stats":
            location = arguments.get("location")
            data = api_client.get_location_stats(location=location)
            formatted = format_location_stats(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_leaderboard":
            data = api_client.get_leaderboard()
            formatted = format_leaderboard(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "query_fleet":
            question = arguments.get("question")
            if not question:
                return [types.TextContent(type="text", text="Error: question is required")]
            
            data = api_client.query_fleet(question)
            formatted = format_query_response(data)
            return [types.TextContent(type="text", text=formatted)]
            
        elif name == "get_recommendations":
            data = api_client.get_recommendations()
            formatted = format_recommendations(data)
            return [types.TextContent(type="text", text=formatted)]
            
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return [types.TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for the MCP server."""
    
    # Standard stdio server (for Claude Desktop)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    logger.info("Starting FleetPulse MCP Server...")
    logger.info(f"API Base URL: {API_BASE_URL}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)