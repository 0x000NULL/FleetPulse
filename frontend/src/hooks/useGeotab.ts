import { useState, useEffect, useCallback } from 'react'
import type { FleetOverview, Vehicle, VehicleSafetyScore, DriverScore, Alert, LocationStats } from '../types/fleet'

const API = '/api'

function useFetch<T>(url: string, interval = 30000) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(url)
      if (!res.ok) throw new Error(`${res.status}`)
      setData(await res.json())
      setError(null)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [url])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, interval)
    return () => clearInterval(id)
  }, [fetchData, interval])

  return { data, loading, error, refresh: fetchData }
}

export function useFleetOverview() {
  return useFetch<FleetOverview>(`${API}/dashboard/overview`)
}

export function useVehicles() {
  return useFetch<Vehicle[]>(`${API}/vehicles/`)
}

export function useSafetyScores() {
  return useFetch<VehicleSafetyScore[]>(`${API}/safety/scores`)
}

export function useLeaderboard() {
  return useFetch<DriverScore[]>(`${API}/gamification/leaderboard`)
}

export function useAlerts() {
  return useFetch<Alert[]>(`${API}/alerts/recent`, 15000)
}

export function useLocations() {
  return useFetch<LocationStats[]>(`${API}/dashboard/locations`)
}
