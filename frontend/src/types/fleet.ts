export type VehicleStatus = 'active' | 'idle' | 'parked' | 'offline'
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical'
export type TrendDirection = 'improving' | 'declining' | 'stable'

export interface VehiclePosition {
  latitude: number
  longitude: number
  bearing: number
  speed: number
}

export interface Vehicle {
  id: string
  name: string
  status: VehicleStatus
  position: VehiclePosition | null
  location_name: string | null
  odometer_km: number
  last_contact: string | null
}

export interface FleetOverview {
  total_vehicles: number
  active: number
  idle: number
  parked: number
  offline: number
  total_trips_today: number
  total_distance_km: number
  avg_trip_duration_min: number
  avg_trip_distance_km: number
}

export interface LocationStats {
  name: string
  address: string
  latitude: number
  longitude: number
  vehicle_count: number
  active: number
  safety_score: number
}

export interface SafetyBreakdown {
  speeding: number
  harsh_braking: number
  harsh_acceleration: number
  harsh_cornering: number
}

export interface VehicleSafetyScore {
  vehicle_id: string
  vehicle_name: string
  score: number
  breakdown: SafetyBreakdown
  trend: TrendDirection
  event_count: number
}

export interface Badge {
  id: string
  name: string
  description: string
  icon: string
  earned: boolean
  earned_at: string | null
}

export interface DriverScore {
  driver_id: string
  driver_name: string
  points: number
  safety_score: number
  badges: Badge[]
  rank: number
}

export interface Alert {
  id: string
  vehicle_id: string
  vehicle_name: string
  alert_type: string
  severity: AlertSeverity
  message: string
  timestamp: string
  acknowledged: boolean
}

export interface LocationRanking {
  location_name: string
  avg_safety_score: number
  total_points: number
  rank: number
}
