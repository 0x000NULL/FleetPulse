import { useCallback } from 'react'
import Dashboard from './components/Dashboard'
import FleetMap from './components/FleetMap'
import VehicleList from './components/VehicleList'
import SafetyScorecard from './components/SafetyScorecard'
import Leaderboard from './components/Leaderboard'
import AlertFeed from './components/AlertFeed'
import LocationCard from './components/LocationCard'
import AgenticMonitor from './components/AgenticMonitor'
import { useFleetOverview, useVehicles, useSafetyScores, useLeaderboard, useAlerts, useLocations, useMonitorAlerts, useMonitorStatus } from './hooks/useGeotab'

export default function App() {
  const overview = useFleetOverview()
  const vehicles = useVehicles()
  const safety = useSafetyScores()
  const leaderboard = useLeaderboard()
  const alerts = useAlerts()
  const locations = useLocations()
  const monitorAlerts = useMonitorAlerts()
  const monitorStatus = useMonitorStatus()

  const triggerCheck = useCallback(() => {
    fetch('/api/monitor/check', { method: 'POST' }).then(() => {
      monitorAlerts.refresh()
      monitorStatus.refresh()
    })
  }, [monitorAlerts, monitorStatus])

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🚗</span>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
              FleetPulse
            </h1>
            <p className="text-xs text-gray-500">Budget Rent a Car · Las Vegas · 8 Locations</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Live
        </div>
      </header>

      <main className="p-6 space-y-6 max-w-[1600px] mx-auto">
        {/* KPI Cards */}
        <Dashboard overview={overview.data} loading={overview.loading} />

        {/* Map + Alerts row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <FleetMap vehicles={vehicles.data} locations={locations.data} />
          </div>
          <AlertFeed alerts={alerts.data} loading={alerts.loading} />
        </div>

        {/* Agentic Monitor */}
        <AgenticMonitor
          alerts={monitorAlerts.data}
          status={monitorStatus.data}
          loading={monitorAlerts.loading}
          onTriggerCheck={triggerCheck}
        />

        {/* Safety + Leaderboard row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SafetyScorecard scores={safety.data} loading={safety.loading} />
          <Leaderboard drivers={leaderboard.data} loading={leaderboard.loading} />
        </div>

        {/* Vehicles */}
        <VehicleList vehicles={vehicles.data} loading={vehicles.loading} />

        {/* Location Cards */}
        <div>
          <h2 className="text-lg font-semibold mb-4">📍 Locations</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {locations.data?.map(loc => (
              <LocationCard key={loc.name} location={loc} />
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
