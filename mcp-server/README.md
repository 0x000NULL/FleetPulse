# FleetPulse MCP Server

Model Context Protocol server for conversational access to FleetPulse fleet management data.

## Setup

1. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Test the server**:
   ```bash
   python test_server.py
   ```

3. **Configure Claude Desktop**:
   
   Copy `claude_desktop_config.json` content to your Claude Desktop config:
   
   - **Linux**: `~/.config/claude-desktop/config.json`
   - **macOS**: `~/Library/Application Support/Claude/config.json`
   
   Update the `cwd` path to your FleetPulse installation directory.

4. **Restart Claude Desktop**

## Available Tools

- `get_fleet_overview` - Vehicle counts and metrics
- `get_vehicles` - List all vehicles with status
- `get_vehicle_details(vehicle_id)` - Specific vehicle info
- `get_safety_scores` - Driver safety scores
- `get_alerts(severity?, limit?)` - Recent alerts
- `get_location_stats(location?)` - Location statistics  
- `get_leaderboard` - Gamification rankings
- `query_fleet(question)` - Natural language queries
- `get_recommendations` - AI optimization suggestions

## Example Queries

- "Show me the current fleet status"
- "Which vehicles are currently active?"
- "What are the safety scores for all drivers?"
- "Give me recommendations to improve efficiency"
- "Show critical alerts from today"
- "Which location has the most idle time?"

## Requirements

- FleetPulse backend running on http://localhost:8080
- Python 3.10+
- Claude Desktop or other MCP client