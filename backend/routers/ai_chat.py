"""AI Chat Router - Intelligent fleet query processing."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta
import json

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    timestamp: Optional[datetime] = None


class ChatResponse(BaseModel):
    response: str
    data: Optional[List[Dict[str, Any]]] = None
    chart_type: Optional[str] = None
    insights: Optional[List[str]] = None
    confidence: float = 0.95


class FleetInsight(BaseModel):
    type: str
    priority: str
    title: str
    message: str
    impact: str
    action: str


# Mock fleet data for intelligent responses
FLEET_DATA = {
    "safety_scores": [
        {"location": "Downtown", "score": 94, "incidents": 1, "trend": "improving"},
        {"location": "Fremont", "score": 93, "incidents": 1, "trend": "stable"},
        {"location": "McCarran", "score": 92, "incidents": 2, "trend": "stable"},
        {"location": "Henderson", "score": 91, "incidents": 2, "trend": "improving"},
        {"location": "Summerlin", "score": 89, "incidents": 3, "trend": "declining"},
        {"location": "The Strip", "score": 88, "incidents": 4, "trend": "stable"},
        {"location": "W Sahara", "score": 87, "incidents": 4, "trend": "concerning"},
        {"location": "N Las Vegas", "score": 85, "incidents": 5, "trend": "needs_attention"},
    ],
    "idle_analysis": [
        {"location": "W Sahara", "avg_idle_minutes": 180, "vehicles_affected": 8, "cost_impact": 2400},
        {"location": "N Las Vegas", "avg_idle_minutes": 165, "vehicles_affected": 6, "cost_impact": 1980},
        {"location": "The Strip", "avg_idle_minutes": 120, "vehicles_affected": 9, "cost_impact": 1620},
        {"location": "Summerlin", "avg_idle_minutes": 95, "vehicles_affected": 7, "cost_impact": 950},
        {"location": "McCarran", "avg_idle_minutes": 75, "vehicles_affected": 5, "cost_impact": 750},
        {"location": "Henderson", "avg_idle_minutes": 65, "vehicles_affected": 4, "cost_impact": 520},
        {"location": "Downtown", "avg_idle_minutes": 45, "vehicles_affected": 3, "cost_impact": 360},
        {"location": "Fremont", "avg_idle_minutes": 35, "vehicles_affected": 2, "cost_impact": 280},
    ],
    "fuel_efficiency": [
        {"date": "2024-02-05", "efficiency": 8.2, "cost_per_100km": 12.30},
        {"date": "2024-02-06", "efficiency": 7.8, "cost_per_100km": 11.70},
        {"date": "2024-02-07", "efficiency": 8.5, "cost_per_100km": 12.75},
        {"date": "2024-02-08", "efficiency": 8.1, "cost_per_100km": 12.15},
        {"date": "2024-02-09", "efficiency": 7.9, "cost_per_100km": 11.85},
        {"date": "2024-02-10", "efficiency": 8.3, "cost_per_100km": 12.45},
        {"date": "2024-02-11", "efficiency": 8.6, "cost_per_100km": 12.90},
    ],
    "maintenance_predictions": [
        {"vehicle_id": "V023", "type": "brake_pads", "days_until_service": 5, "confidence": 0.92, "cost_estimate": 280},
        {"vehicle_id": "V045", "type": "oil_change", "days_until_service": 2, "confidence": 0.98, "cost_estimate": 65},
        {"vehicle_id": "V031", "type": "tire_rotation", "days_until_service": 12, "confidence": 0.87, "cost_estimate": 120},
        {"vehicle_id": "V018", "type": "transmission", "days_until_service": 15, "confidence": 0.74, "cost_estimate": 850},
    ],
    "utilization_patterns": [
        {"hour": "06:00", "utilization": 24, "demand": "low", "cost_per_hour": 45},
        {"hour": "08:00", "utilization": 56, "demand": "medium", "cost_per_hour": 78},
        {"hour": "10:00", "utilization": 70, "demand": "medium", "cost_per_hour": 95},
        {"hour": "12:00", "utilization": 84, "demand": "high", "cost_per_hour": 125},
        {"hour": "14:00", "utilization": 76, "demand": "high", "cost_per_hour": 110},
        {"hour": "16:00", "utilization": 90, "demand": "peak", "cost_per_hour": 145},
        {"hour": "18:00", "utilization": 64, "demand": "medium", "cost_per_hour": 85},
        {"hour": "20:00", "utilization": 36, "demand": "low", "cost_per_hour": 55},
    ]
}

# Advanced pattern matching for natural language queries
QUERY_PATTERNS = [
    {
        "patterns": [r"safety|safest|dangerous|accident|incident|score", r"location|where|which"],
        "handler": "safety_analysis",
        "confidence": 0.95
    },
    {
        "patterns": [r"idle|idling|waste|stationary|parked"],
        "handler": "idle_analysis", 
        "confidence": 0.92
    },
    {
        "patterns": [r"fuel|gas|efficiency|consumption|mpg|cost"],
        "handler": "fuel_analysis",
        "confidence": 0.90
    },
    {
        "patterns": [r"maintenance|repair|service|predict|due"],
        "handler": "maintenance_predictions",
        "confidence": 0.93
    },
    {
        "patterns": [r"utilization|busy|active|peak|usage|demand"],
        "handler": "utilization_analysis",
        "confidence": 0.88
    },
    {
        "patterns": [r"recommend|suggest|optimize|save|cost.?saving"],
        "handler": "cost_optimization",
        "confidence": 0.91
    },
    {
        "patterns": [r"vehicle.*\d+|specific.*vehicle|vehicle.*#"],
        "handler": "vehicle_specific",
        "confidence": 0.85
    }
]


def analyze_query(message: str) -> tuple[str, float]:
    """Analyze user query and determine the best handler."""
    message_lower = message.lower()
    
    best_handler = "general"
    best_confidence = 0.3
    
    for pattern_group in QUERY_PATTERNS:
        matches = 0
        for pattern in pattern_group["patterns"]:
            if re.search(pattern, message_lower):
                matches += 1
        
        if matches > 0:
            confidence = pattern_group["confidence"] * (matches / len(pattern_group["patterns"]))
            if confidence > best_confidence:
                best_handler = pattern_group["handler"]
                best_confidence = confidence
    
    return best_handler, best_confidence


def safety_analysis_handler(message: str) -> ChatResponse:
    """Handle safety-related queries."""
    data = FLEET_DATA["safety_scores"]
    
    # Sort by score for better insights
    sorted_data = sorted(data, key=lambda x: x["score"], reverse=True)
    
    insights = [
        f"Best performers: {sorted_data[0]['location']} ({sorted_data[0]['score']}%) and {sorted_data[1]['location']} ({sorted_data[1]['score']}%)",
        f"Attention needed: {sorted_data[-1]['location']} with {sorted_data[-1]['score']}% - {sorted_data[-1]['incidents']} incidents this month",
        f"Fleet average safety score: {sum(loc['score'] for loc in data) / len(data):.1f}%"
    ]
    
    # Check for specific location mentions
    message_lower = message.lower()
    mentioned_location = None
    for location_data in data:
        if location_data["location"].lower().replace(" ", "").replace(".", "") in message_lower.replace(" ", ""):
            mentioned_location = location_data
            break
    
    if mentioned_location:
        response = f"Safety analysis for {mentioned_location['location']}: {mentioned_location['score']}% safety score with {mentioned_location['incidents']} incidents. Status: {mentioned_location['trend'].replace('_', ' ')}"
    else:
        response = f"Safety score analysis across all {len(data)} locations. Here's the current ranking:"
    
    return ChatResponse(
        response=response,
        data=[{"location": loc["location"], "score": loc["score"], "color": "#10b981" if loc["score"] >= 90 else "#f59e0b" if loc["score"] >= 85 else "#ef4444"} for loc in sorted_data],
        chart_type="bar",
        insights=insights,
        confidence=0.95
    )


def idle_analysis_handler(message: str) -> ChatResponse:
    """Handle idle time queries."""
    data = FLEET_DATA["idle_analysis"]
    
    # Check for specific time threshold
    time_threshold = None
    time_matches = re.search(r"(\d+)\s*(min|minute|hour)", message.lower())
    if time_matches:
        time_threshold = int(time_matches.group(1))
        if "hour" in time_matches.group(2):
            time_threshold *= 60
    
    if time_threshold:
        filtered_vehicles = [loc for loc in data if loc["avg_idle_minutes"] > time_threshold]
        total_affected = sum(loc["vehicles_affected"] for loc in filtered_vehicles)
        response = f"Found {total_affected} vehicles across {len(filtered_vehicles)} locations with idle time exceeding {time_threshold} minutes:"
    else:
        response = "Idle time analysis across all locations. W Sahara and N Las Vegas need immediate attention:"
    
    insights = [
        f"Highest idle time: {data[0]['location']} with {data[0]['avg_idle_minutes']} minutes average",
        f"Total monthly cost impact: ${sum(loc['cost_impact'] for loc in data):,}",
        f"Quick win: Focus on {data[0]['location']} - potential ${data[0]['cost_impact']:,}/month savings"
    ]
    
    return ChatResponse(
        response=response,
        data=[{"location": loc["location"], "minutes": loc["avg_idle_minutes"], "color": "#ef4444" if loc["avg_idle_minutes"] > 120 else "#f59e0b" if loc["avg_idle_minutes"] > 60 else "#10b981"} for loc in data[:8]],
        chart_type="bar",
        insights=insights,
        confidence=0.92
    )


def fuel_analysis_handler(message: str) -> ChatResponse:
    """Handle fuel efficiency queries."""
    data = FLEET_DATA["fuel_efficiency"]
    
    avg_efficiency = sum(day["efficiency"] for day in data) / len(data)
    avg_cost = sum(day["cost_per_100km"] for day in data) / len(data)
    
    insights = [
        f"7-day average efficiency: {avg_efficiency:.1f} L/100km (${avg_cost:.2f}/100km)",
        f"Best day: {min(data, key=lambda x: x['efficiency'])['date']} with {min(data, key=lambda x: x['efficiency'])['efficiency']} L/100km",
        f"Trend: {'Improving' if data[-1]['efficiency'] > data[0]['efficiency'] else 'Stable' if abs(data[-1]['efficiency'] - data[0]['efficiency']) < 0.2 else 'Declining'}"
    ]
    
    return ChatResponse(
        response="Fuel efficiency analysis for the past 7 days:",
        data=[{"day": day["date"][-5:], "efficiency": day["efficiency"]} for day in data],
        chart_type="line",
        insights=insights,
        confidence=0.90
    )


def maintenance_predictions_handler(message: str) -> ChatResponse:
    """Handle maintenance prediction queries."""
    data = FLEET_DATA["maintenance_predictions"]
    
    # Sort by urgency
    sorted_data = sorted(data, key=lambda x: x["days_until_service"])
    
    total_cost = sum(item["cost_estimate"] for item in data)
    urgent_count = len([item for item in data if item["days_until_service"] <= 7])
    
    insights = [
        f"Urgent maintenance needed: {urgent_count} vehicles within 7 days",
        f"Most urgent: Vehicle {sorted_data[0]['vehicle_id']} - {sorted_data[0]['type']} in {sorted_data[0]['days_until_service']} days",
        f"Total predicted maintenance cost: ${total_cost:,} over next 30 days"
    ]
    
    return ChatResponse(
        response=f"Predictive maintenance analysis for {len(data)} vehicles:",
        data=[{"vehicle": item["vehicle_id"], "type": item["type"], "days": item["days_until_service"], "confidence": item["confidence"] * 100, "color": "#ef4444" if item["days_until_service"] <= 3 else "#f59e0b" if item["days_until_service"] <= 7 else "#10b981"} for item in sorted_data],
        chart_type="bar",
        insights=insights,
        confidence=0.93
    )


def utilization_analysis_handler(message: str) -> ChatResponse:
    """Handle utilization pattern queries."""
    data = FLEET_DATA["utilization_patterns"]
    
    peak_hour = max(data, key=lambda x: x["utilization"])
    low_hour = min(data, key=lambda x: x["utilization"])
    
    insights = [
        f"Peak utilization: {peak_hour['utilization']}% at {peak_hour['hour']}",
        f"Lowest utilization: {low_hour['utilization']}% at {low_hour['hour']} (maintenance window opportunity)",
        f"Daily revenue potential: ${sum(hour['cost_per_hour'] for hour in data):,} at current rates"
    ]
    
    return ChatResponse(
        response="Fleet utilization patterns throughout the day:",
        data=[{"hour": hour["hour"], "rate": hour["utilization"]} for hour in data],
        chart_type="line",
        insights=insights,
        confidence=0.88
    )


def cost_optimization_handler(message: str) -> ChatResponse:
    """Handle cost optimization and recommendation queries."""
    recommendations = [
        {"category": "Route Optimization", "savings": 2400, "color": "#10b981"},
        {"category": "Idle Reduction", "savings": 1800, "color": "#3b82f6"},
        {"category": "Maintenance Scheduling", "savings": 1200, "color": "#8b5cf6"},
        {"category": "Driver Training", "savings": 900, "color": "#f59e0b"},
        {"category": "Fuel Management", "savings": 600, "color": "#06b6d4"},
    ]
    
    total_savings = sum(rec["savings"] for rec in recommendations)
    
    insights = [
        f"Total monthly savings potential: ${total_savings:,}",
        f"Top opportunity: {recommendations[0]['category']} - ${recommendations[0]['savings']}/month",
        f"ROI timeline: 3-6 months payback on optimization investments"
    ]
    
    return ChatResponse(
        response="AI-generated cost optimization recommendations based on current fleet data:",
        data=recommendations,
        chart_type="pie",
        insights=insights,
        confidence=0.91
    )


def vehicle_specific_handler(message: str) -> ChatResponse:
    """Handle vehicle-specific queries."""
    # Extract vehicle number from message
    vehicle_match = re.search(r"(?:vehicle|#)\s*(\d+)", message.lower())
    if vehicle_match:
        vehicle_num = vehicle_match.group(1)
        # Generate mock vehicle data
        vehicle_data = {
            "id": f"V{vehicle_num.zfill(3)}",
            "status": "active",
            "location": "W Sahara",
            "idle_time": 120,
            "fuel_efficiency": 8.4,
            "safety_score": 87,
            "last_maintenance": "2024-01-15",
            "next_service": "2024-02-20"
        }
        
        return ChatResponse(
            response=f"Vehicle #{vehicle_num} analysis:",
            data=[vehicle_data],
            insights=[
                f"Current status: {vehicle_data['status']} at {vehicle_data['location']}",
                f"Performance: {vehicle_data['fuel_efficiency']} L/100km, Safety score {vehicle_data['safety_score']}%",
                f"Service due: {vehicle_data['next_service']}"
            ],
            confidence=0.85
        )
    
    return general_handler(message)


def general_handler(message: str) -> ChatResponse:
    """Handle general queries that don't match specific patterns."""
    return ChatResponse(
        response="I understand you're asking about fleet operations. I can help you with safety scores, idle time analysis, fuel efficiency, maintenance predictions, utilization patterns, and cost optimization recommendations. Try asking something like 'Which location has the best safety scores?' or 'Show me vehicles with high idle time.'",
        confidence=0.3
    )


@router.post("/query", response_model=ChatResponse)
async def process_chat_query(chat_message: ChatMessage):
    """Process a natural language fleet query and return intelligent response."""
    try:
        handler_name, confidence = analyze_query(chat_message.message)
        
        # Route to appropriate handler
        handlers = {
            "safety_analysis": safety_analysis_handler,
            "idle_analysis": idle_analysis_handler,
            "fuel_analysis": fuel_analysis_handler,
            "maintenance_predictions": maintenance_predictions_handler,
            "utilization_analysis": utilization_analysis_handler,
            "cost_optimization": cost_optimization_handler,
            "vehicle_specific": vehicle_specific_handler,
            "general": general_handler
        }
        
        handler = handlers.get(handler_name, general_handler)
        response = handler(chat_message.message)
        
        # Override confidence with pattern matching confidence
        response.confidence = confidence
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/insights", response_model=List[FleetInsight])
async def get_ai_insights():
    """Get current AI-generated fleet insights and recommendations."""
    insights = [
        FleetInsight(
            type="efficiency",
            priority="high",
            title="Idle Time Optimization",
            message="W Sahara location shows 3x higher idle time than fleet average. Driver coaching program could reduce this by 60%.",
            impact="$2,400/month savings",
            action="Schedule Training"
        ),
        FleetInsight(
            type="maintenance",
            priority="medium",
            title="Predictive Maintenance Alert",
            message="Vehicle V023 brake wear patterns indicate service needed in 5-7 days. AI confidence: 92%.",
            impact="Prevent $850 emergency repair",
            action="Schedule Service"
        ),
        FleetInsight(
            type="revenue",
            priority="medium", 
            title="Peak Hour Optimization",
            message="Utilization analysis suggests deploying 3 additional vehicles during 4-6PM peak at Summerlin location.",
            impact="+$450 daily revenue",
            action="Adjust Fleet Distribution"
        ),
        FleetInsight(
            type="safety",
            priority="low",
            title="Best Practice Sharing",
            message="Fremont location drivers show 12% better safety performance. Their techniques could be applied fleet-wide.",
            impact="15% incident reduction",
            action="Analyze Best Practices"
        )
    ]
    
    return insights


@router.get("/analytics/summary")
async def get_analytics_summary():
    """Get comprehensive fleet analytics summary for AI processing."""
    return {
        "fleet_health": {
            "overall_score": 87,
            "safety_trend": "improving",
            "efficiency_trend": "stable",
            "utilization_rate": 74,
            "maintenance_compliance": 92
        },
        "key_metrics": {
            "total_vehicles": 50,
            "active_vehicles": 42,
            "avg_safety_score": 89.6,
            "avg_fuel_efficiency": 8.2,
            "monthly_savings_potential": 6300
        },
        "risk_indicators": [
            {"location": "W Sahara", "risk": "high", "reason": "excessive_idle_time"},
            {"location": "N Las Vegas", "risk": "medium", "reason": "below_avg_safety"},
            {"vehicle": "V023", "risk": "medium", "reason": "maintenance_due"}
        ],
        "optimization_opportunities": [
            {"type": "route", "impact": "high", "savings": 2400},
            {"type": "idle_reduction", "impact": "high", "savings": 1800}, 
            {"type": "maintenance_schedule", "impact": "medium", "savings": 1200}
        ]
    }