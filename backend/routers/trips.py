"""Trip and route replay endpoints."""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from geotab_client import GeotabClient

router = APIRouter()


@router.get("/vehicle/{vehicle_id}")
async def get_vehicle_trips(
    vehicle_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """Get all trips for a vehicle on a given date."""
    try:
        # Parse the date
        trip_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        from_date = trip_date
        to_date = trip_date + timedelta(days=1)
        
        client = GeotabClient.get()
        
        # Get trips for the vehicle on the specified date
        trips = client.api.get('Trip', search={
            'deviceSearch': {'id': vehicle_id},
            'fromDate': from_date.isoformat(),
            'toDate': to_date.isoformat()
        })
        
        # Format trip data for the frontend
        formatted_trips = []
        for trip in trips:
            formatted_trip = {
                'id': trip.get('id'),
                'start': {
                    'timestamp': trip.get('start'),
                    'latitude': trip.get('startLatitude'),
                    'longitude': trip.get('startLongitude')
                },
                'stop': {
                    'timestamp': trip.get('stop'),
                    'latitude': trip.get('stopLatitude'),
                    'longitude': trip.get('stopLongitude')
                },
                'distance_km': trip.get('distance', 0) / 1000,  # Convert m to km
                'duration_min': None,
                'driver_id': trip.get('driver', {}).get('id') if trip.get('driver') else None,
                'driver_name': trip.get('driver', {}).get('name') if trip.get('driver') else 'Unknown'
            }
            
            # Calculate duration if we have start/stop times
            if trip.get('start') and trip.get('stop'):
                start_time = datetime.fromisoformat(trip['start'].replace('Z', '+00:00'))
                stop_time = datetime.fromisoformat(trip['stop'].replace('Z', '+00:00'))
                duration = (stop_time - start_time).total_seconds() / 60
                formatted_trip['duration_min'] = round(duration, 1)
            
            formatted_trips.append(formatted_trip)
        
        return {
            'vehicle_id': vehicle_id,
            'date': date,
            'trips': formatted_trips,
            'total_trips': len(formatted_trips),
            'total_distance_km': sum(trip['distance_km'] for trip in formatted_trips),
            'total_duration_min': sum(trip['duration_min'] for trip in formatted_trips if trip['duration_min'])
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trips: {str(e)}")


@router.get("/vehicle/{vehicle_id}/route")
async def get_vehicle_route(
    vehicle_id: str,
    from_time: str = Query(..., alias="from", description="Start time in ISO format"),
    to_time: str = Query(..., alias="to", description="End time in ISO format")
):
    """Get GPS breadcrumb trail for a vehicle during a specific time period."""
    try:
        # Parse the ISO timestamps
        from_date = datetime.fromisoformat(from_time.replace('Z', '+00:00'))
        to_date = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
        
        client = GeotabClient.get()
        
        # Get LogRecord data (GPS breadcrumbs)
        log_records = client.api.get('LogRecord', search={
            'deviceSearch': {'id': vehicle_id},
            'fromDate': from_date.isoformat(),
            'toDate': to_date.isoformat()
        })
        
        # Format GPS points for the frontend
        route_points = []
        for record in log_records:
            if record.get('latitude') and record.get('longitude'):
                route_points.append({
                    'timestamp': record.get('dateTime'),
                    'latitude': record.get('latitude'),
                    'longitude': record.get('longitude'),
                    'speed_kmh': record.get('speed', 0) * 3.6 if record.get('speed') else 0  # Convert m/s to km/h
                })
        
        # Sort by timestamp
        route_points.sort(key=lambda x: x['timestamp'])
        
        return {
            'vehicle_id': vehicle_id,
            'from': from_time,
            'to': to_time,
            'points': route_points,
            'total_points': len(route_points)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid ISO timestamp format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching route: {str(e)}")


@router.get("/vehicle/{vehicle_id}/speed")
async def get_vehicle_speed_data(
    vehicle_id: str,
    from_time: str = Query(..., alias="from", description="Start time in ISO format"),
    to_time: str = Query(..., alias="to", description="End time in ISO format")
):
    """Get speed data over time for a vehicle trip (for speed graph overlay)."""
    try:
        # Parse the ISO timestamps
        from_date = datetime.fromisoformat(from_time.replace('Z', '+00:00'))
        to_date = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
        
        client = GeotabClient.get()
        
        # Get StatusData for speed diagnostic
        # We'll look for speed diagnostic data
        status_data = client.api.get('StatusData', search={
            'deviceSearch': {'id': vehicle_id},
            'fromDate': from_date.isoformat(),
            'toDate': to_date.isoformat(),
            'diagnosticSearch': {'id': 'DiagnosticSpeedId'}  # This might need adjustment based on Geotab setup
        })
        
        # If speed diagnostic doesn't work, fall back to LogRecord data
        if not status_data:
            # Use LogRecord as fallback
            log_records = client.api.get('LogRecord', search={
                'deviceSearch': {'id': vehicle_id},
                'fromDate': from_date.isoformat(),
                'toDate': to_date.isoformat()
            })
            
            speed_data = []
            for record in log_records:
                if record.get('speed') is not None:
                    speed_data.append({
                        'timestamp': record.get('dateTime'),
                        'speed_kmh': record.get('speed', 0) * 3.6  # Convert m/s to km/h
                    })
        else:
            # Format StatusData
            speed_data = []
            for record in status_data:
                if record.get('data') is not None:
                    speed_data.append({
                        'timestamp': record.get('dateTime'),
                        'speed_kmh': float(record.get('data', 0))
                    })
        
        # Sort by timestamp
        speed_data.sort(key=lambda x: x['timestamp'])
        
        # Calculate speed statistics
        speeds = [point['speed_kmh'] for point in speed_data if point['speed_kmh'] > 0]
        max_speed = max(speeds) if speeds else 0
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        return {
            'vehicle_id': vehicle_id,
            'from': from_time,
            'to': to_time,
            'speed_data': speed_data,
            'total_points': len(speed_data),
            'max_speed_kmh': round(max_speed, 1),
            'avg_speed_kmh': round(avg_speed, 1)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid ISO timestamp format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching speed data: {str(e)}")