import type { Alert } from '../types/fleet'

interface Props {
  alerts: Alert[] | null
  loading: boolean
}

const severityStyle: Record<string, string> = {
  critical: 'border-l-red-500 bg-red-500/5',
  high: 'border-l-orange-500 bg-orange-500/5',
  medium: 'border-l-amber-500 bg-amber-500/5',
  low: 'border-l-blue-500 bg-blue-500/5',
}

const severityBadge: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400',
  high: 'bg-orange-500/20 text-orange-400',
  medium: 'bg-amber-500/20 text-amber-400',
  low: 'bg-blue-500/20 text-blue-400',
}

export default function AlertFeed({ alerts, loading }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl shadow-lg overflow-hidden flex flex-col">
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
        <h2 className="font-semibold">🚨 Alert Feed</h2>
        {alerts && (
          <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">
            {alerts.length}
          </span>
        )}
      </div>
      <div className="flex-1 overflow-y-auto max-h-[370px] p-2 space-y-2">
        {loading && <p className="text-gray-500 text-center py-8">Loading…</p>}
        {alerts?.slice(0, 30).map(a => (
          <div
            key={a.id}
            className={`border-l-2 rounded-r-lg p-3 ${severityStyle[a.severity]}`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className={`text-xs px-1.5 py-0.5 rounded ${severityBadge[a.severity]}`}>
                {a.severity}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(a.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <p className="text-sm">{a.message}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
