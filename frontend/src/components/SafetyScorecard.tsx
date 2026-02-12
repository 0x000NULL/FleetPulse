import type { VehicleSafetyScore } from '../types/fleet'

interface Props {
  scores: VehicleSafetyScore[] | null
  loading: boolean
}

function scoreColor(score: number): string {
  if (score >= 90) return 'text-emerald-400'
  if (score >= 70) return 'text-amber-400'
  return 'text-red-400'
}

function scoreBg(score: number): string {
  if (score >= 90) return 'bg-emerald-500'
  if (score >= 70) return 'bg-amber-500'
  return 'bg-red-500'
}

const trendIcon: Record<string, string> = {
  improving: '📈',
  declining: '📉',
  stable: '➡️',
}

export default function SafetyScorecard({ scores, loading }: Props) {
  const sorted = scores ? [...scores].sort((a, b) => b.score - a.score) : []

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800">
        <h2 className="font-semibold">🛡️ Safety Scorecard</h2>
      </div>
      <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto">
        {loading && <p className="text-gray-500 text-center py-8">Loading…</p>}
        {sorted.slice(0, 20).map(s => (
          <div key={s.vehicle_id} className="flex items-center gap-3">
            <div className={`text-2xl font-bold w-14 text-right ${scoreColor(s.score)}`}>
              {s.score}
            </div>
            <div className="flex-1">
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${scoreBg(s.score)}`}
                  style={{ width: `${s.score}%` }}
                />
              </div>
            </div>
            <div className="w-32 truncate text-sm">{s.vehicle_name}</div>
            <div className="text-sm">{trendIcon[s.trend]}</div>
            <div className="text-xs text-gray-500 w-20 text-right">
              {s.event_count} events
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
