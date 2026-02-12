import type { Vehicle } from '../types/fleet'

interface Props {
  vehicles: Vehicle[] | null
  loading: boolean
}

const statusBadge: Record<string, string> = {
  active: 'bg-emerald-500/20 text-emerald-400',
  idle: 'bg-amber-500/20 text-amber-400',
  parked: 'bg-indigo-500/20 text-indigo-400',
  offline: 'bg-gray-500/20 text-gray-400',
}

export default function VehicleList({ vehicles, loading }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl shadow-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800">
        <h2 className="font-semibold">🚗 Vehicles</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-800/50 text-gray-400">
            <tr>
              <th className="px-4 py-2 text-left">Name</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Location</th>
              <th className="px-4 py-2 text-right">Speed</th>
              <th className="px-4 py-2 text-right">Last Contact</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {loading && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Loading…</td></tr>
            )}
            {vehicles?.slice(0, 50).map(v => (
              <tr key={v.id} className="hover:bg-gray-800/40 transition-colors">
                <td className="px-4 py-2 font-medium">{v.name}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge[v.status]}`}>
                    {v.status}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-400">{v.location_name || '—'}</td>
                <td className="px-4 py-2 text-right">{v.position?.speed ?? 0} km/h</td>
                <td className="px-4 py-2 text-right text-gray-500 text-xs">
                  {v.last_contact ? new Date(v.last_contact).toLocaleTimeString() : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
