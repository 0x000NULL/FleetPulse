import type { LocationStats } from '../types/fleet'

interface Props {
  location: LocationStats
}

function scoreColor(score: number): string {
  if (score >= 90) return 'text-emerald-400'
  if (score >= 70) return 'text-amber-400'
  return 'text-red-400'
}

export default function LocationCard({ location }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 shadow-lg border border-gray-800 hover:border-blue-500/40 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-sm">{location.name}</h3>
          <p className="text-xs text-gray-500 mt-0.5">{location.address}</p>
        </div>
        <div className={`text-xl font-bold ${scoreColor(location.safety_score)}`}>
          {location.safety_score}
        </div>
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>🚗 {location.vehicle_count} vehicles</span>
        <span>🟢 {location.active} active</span>
      </div>
    </div>
  )
}
