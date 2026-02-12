import type { FleetOverview } from '../types/fleet'

interface Props {
  overview: FleetOverview | null
  loading: boolean
}

const cards = [
  { key: 'total_vehicles', label: 'Total Vehicles', icon: '🚗', color: 'from-blue-500 to-blue-700' },
  { key: 'active', label: 'Active', icon: '🟢', color: 'from-emerald-500 to-emerald-700' },
  { key: 'idle', label: 'Idle', icon: '🟡', color: 'from-amber-500 to-amber-700' },
  { key: 'parked', label: 'Parked', icon: '🔵', color: 'from-slate-500 to-slate-700' },
  { key: 'total_trips_today', label: 'Trips Today', icon: '📊', color: 'from-purple-500 to-purple-700' },
  { key: 'total_distance_km', label: 'Distance (km)', icon: '🛣️', color: 'from-cyan-500 to-cyan-700' },
  { key: 'avg_trip_duration_min', label: 'Avg Duration (min)', icon: '⏱️', color: 'from-rose-500 to-rose-700' },
  { key: 'avg_trip_distance_km', label: 'Avg Distance (km)', icon: '📏', color: 'from-indigo-500 to-indigo-700' },
] as const

export default function Dashboard({ overview, loading }: Props) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      {cards.map(c => (
        <div
          key={c.key}
          className={`bg-gradient-to-br ${c.color} rounded-xl p-4 shadow-lg`}
        >
          <div className="text-lg">{c.icon}</div>
          <div className="text-2xl font-bold mt-1">
            {loading ? '—' : (overview as any)?.[c.key] ?? 0}
          </div>
          <div className="text-xs text-white/70 mt-1">{c.label}</div>
        </div>
      ))}
    </div>
  )
}
