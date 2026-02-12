import type { DriverScore } from '../types/fleet'

interface Props {
  drivers: DriverScore[] | null
  loading: boolean
}

const rankEmoji = ['🥇', '🥈', '🥉']

export default function Leaderboard({ drivers, loading }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl shadow-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800">
        <h2 className="font-semibold">🏆 Driver Leaderboard</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-800/50 text-gray-400">
            <tr>
              <th className="px-4 py-2 text-left w-12">#</th>
              <th className="px-4 py-2 text-left">Driver</th>
              <th className="px-4 py-2 text-right">Points</th>
              <th className="px-4 py-2 text-right">Safety</th>
              <th className="px-4 py-2 text-left">Badges</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {loading && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Loading…</td></tr>
            )}
            {drivers?.slice(0, 15).map(d => (
              <tr key={d.driver_id} className="hover:bg-gray-800/40 transition-colors">
                <td className="px-4 py-2 text-lg">
                  {d.rank <= 3 ? rankEmoji[d.rank - 1] : d.rank}
                </td>
                <td className="px-4 py-2 font-medium">{d.driver_name}</td>
                <td className="px-4 py-2 text-right font-mono text-emerald-400">
                  {d.points.toLocaleString()}
                </td>
                <td className="px-4 py-2 text-right">{d.safety_score}</td>
                <td className="px-4 py-2">
                  {d.badges.filter(b => b.earned).map(b => (
                    <span key={b.id} title={b.name} className="mr-1">{b.icon}</span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
