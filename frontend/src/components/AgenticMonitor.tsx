import { useState } from 'react'
import type { Alert } from '../types/fleet'

interface MonitorStatus {
  running: boolean
  total_alerts: number
  patterns: {
    last_check?: string
    total_vehicles?: number
    active_vehicles?: number
    alerts_generated?: number
    checks_run?: number
    location_vehicle_counts?: Record<string, number>
  }
}

interface Props {
  alerts: Alert[] | null
  status: MonitorStatus | null
  loading: boolean
  onTriggerCheck: () => void
}

const severityStyle: Record<string, string> = {
  critical: 'border-l-red-500 bg-red-500/10',
  high: 'border-l-orange-500 bg-orange-500/10',
  medium: 'border-l-amber-500 bg-amber-500/10',
  low: 'border-l-blue-500 bg-blue-500/10',
}

const severityBadge: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400',
  high: 'bg-orange-500/20 text-orange-400',
  medium: 'bg-amber-500/20 text-amber-400',
  low: 'bg-blue-500/20 text-blue-400',
}

export default function AgenticMonitor({ alerts, status, loading, onTriggerCheck }: Props) {
  const [expanded, setExpanded] = useState(true)
  const patterns = status?.patterns || {}

  return (
    <div className="bg-gray-900 rounded-xl shadow-lg overflow-hidden border border-purple-500/30">
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between bg-gradient-to-r from-purple-900/30 to-blue-900/30">
        <div className="flex items-center gap-2">
          <span className="text-lg">🤖</span>
          <h2 className="font-semibold">Agentic Monitor</h2>
          {status?.running && (
            <span className="flex items-center gap-1 text-xs text-emerald-400">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onTriggerCheck}
            className="text-xs bg-purple-600 hover:bg-purple-500 text-white px-3 py-1 rounded-lg transition-colors"
          >
            Run Check
          </button>
          <button onClick={() => setExpanded(!expanded)} className="text-gray-400 text-xs">
            {expanded ? '▼' : '▶'}
          </button>
        </div>
      </div>

      {expanded && (
        <>
          {/* Pattern Summary */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 border-b border-gray-800">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">
                {patterns.checks_run ?? '—'}
              </div>
              <div className="text-xs text-gray-500">Checks Active</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">
                {patterns.total_vehicles ?? '—'}
              </div>
              <div className="text-xs text-gray-500">Monitored</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-400">
                {patterns.active_vehicles ?? '—'}
              </div>
              <div className="text-xs text-gray-500">Active Now</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-400">
                {status?.total_alerts ?? '—'}
              </div>
              <div className="text-xs text-gray-500">Total Alerts</div>
            </div>
          </div>

          {/* Location Inventory Mini-Grid */}
          {patterns.location_vehicle_counts && (
            <div className="px-4 py-3 border-b border-gray-800">
              <div className="text-xs text-gray-400 mb-2">📍 Location Inventory</div>
              <div className="grid grid-cols-4 gap-2">
                {Object.entries(patterns.location_vehicle_counts).map(([name, count]) => (
                  <div key={name} className="text-center">
                    <div className={`text-sm font-bold ${count === 0 ? 'text-red-400' : 'text-gray-200'}`}>
                      {count}
                    </div>
                    <div className="text-[10px] text-gray-500 truncate">{name}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alert List */}
          <div className="max-h-[300px] overflow-y-auto p-2 space-y-2">
            {loading && <p className="text-gray-500 text-center py-4">Loading…</p>}
            {alerts && alerts.length === 0 && (
              <p className="text-gray-500 text-center py-4">✅ No anomalies detected</p>
            )}
            {alerts?.slice(0, 20).map(a => (
              <div key={a.id} className={`border-l-2 rounded-r-lg p-3 ${severityStyle[a.severity]}`}>
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

          {/* Last check */}
          {patterns.last_check && (
            <div className="px-4 py-2 text-xs text-gray-600 border-t border-gray-800">
              Last check: {new Date(patterns.last_check).toLocaleTimeString()}
            </div>
          )}
        </>
      )}
    </div>
  )
}
