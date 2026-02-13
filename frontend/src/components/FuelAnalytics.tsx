import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Fuel, TrendingDown, TrendingUp, DollarSign, Gauge, AlertTriangle } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'

interface FuelSummary {
  period_30d: { total_miles: number; total_gallons: number; total_cost: number; avg_mpg: number; cost_per_mile: number }
  period_7d: { total_miles: number; total_gallons: number; total_cost: number; avg_mpg: number; cost_per_mile: number }
  waste: { harsh_events: number; wasted_gallons: number; wasted_cost: number }
  fleet_size: number
  cost_per_vehicle_30d: number
  fuel_price: number
}

interface FuelTrend {
  date: string
  miles: number
  gallons: number
  cost: number
}

interface VehicleEfficiency {
  vehicle_id: string
  vehicle_name: string
  miles: number
  est_mpg: number
  est_gallons: number
  est_cost: number
  harsh_events: number
  efficiency_grade: string
}

export default function FuelAnalytics() {
  const [summary, setSummary] = useState<FuelSummary | null>(null)
  const [trends, setTrends] = useState<FuelTrend[]>([])
  const [efficiency, setEfficiency] = useState<VehicleEfficiency[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/fuel/summary').then(r => r.json()),
      fetch('/api/fuel/trends').then(r => r.json()),
      fetch('/api/fuel/efficiency').then(r => r.json()),
    ]).then(([s, t, e]) => {
      setSummary(s)
      setTrends(t)
      setEfficiency(e)
    }).finally(() => setLoading(false))
  }, [])

  const gradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-emerald-400 bg-emerald-500/20'
      case 'B': return 'text-blue-400 bg-blue-500/20'
      case 'C': return 'text-amber-400 bg-amber-500/20'
      default: return 'text-red-400 bg-red-500/20'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-5">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase mb-2">
            <DollarSign className="w-4 h-4" /> 30-Day Fuel Cost
          </div>
          <div className="text-2xl font-bold text-emerald-400">${summary?.period_30d.total_cost.toLocaleString()}</div>
          <div className="text-xs text-gray-500 mt-1">${summary?.cost_per_vehicle_30d}/vehicle</div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-5">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase mb-2">
            <Gauge className="w-4 h-4" /> Fleet Avg MPG
          </div>
          <div className="text-2xl font-bold text-blue-400">{summary?.period_30d.avg_mpg}</div>
          <div className="text-xs text-gray-500 mt-1">{summary?.period_30d.total_gallons.toLocaleString()} gal used</div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-5">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase mb-2">
            <TrendingUp className="w-4 h-4" /> Miles Driven (30d)
          </div>
          <div className="text-2xl font-bold text-purple-400">{summary?.period_30d.total_miles.toLocaleString()}</div>
          <div className="text-xs text-gray-500 mt-1">${summary?.period_30d.cost_per_mile}/mile</div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-5">
          <div className="flex items-center gap-2 text-gray-400 text-xs uppercase mb-2">
            <AlertTriangle className="w-4 h-4" /> Fuel Waste
          </div>
          <div className="text-2xl font-bold text-amber-400">${summary?.waste.wasted_cost.toFixed(0)}</div>
          <div className="text-xs text-gray-500 mt-1">{summary?.waste.harsh_events} harsh events</div>
        </motion.div>
      </div>

      {/* Fuel Cost Trend Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6"
      >
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingDown className="w-5 h-5 text-emerald-400" />
          Daily Fuel Cost Trend (30 Days)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={trends}>
            <defs>
              <linearGradient id="fuelGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#6b7280" tick={{ fontSize: 11 }}
              tickFormatter={(v) => v.slice(5)} />
            <YAxis stroke="#6b7280" tick={{ fontSize: 11 }}
              tickFormatter={(v) => `$${v}`} />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#9ca3af' }}
              formatter={(value: number) => [`$${value.toFixed(0)}`, 'Cost']}
            />
            <Area type="monotone" dataKey="cost" stroke="#10b981" fill="url(#fuelGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Vehicle Efficiency Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6"
      >
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Fuel className="w-5 h-5 text-blue-400" />
          Vehicle Fuel Efficiency (7 Days)
        </h3>
        {efficiency.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase border-b border-gray-800">
                  <th className="text-left py-3 px-2">Vehicle</th>
                  <th className="text-right py-3 px-2">Miles</th>
                  <th className="text-right py-3 px-2">Est. MPG</th>
                  <th className="text-right py-3 px-2">Gallons</th>
                  <th className="text-right py-3 px-2">Cost</th>
                  <th className="text-center py-3 px-2">Grade</th>
                </tr>
              </thead>
              <tbody>
                {efficiency.slice(0, 15).map((v, i) => (
                  <motion.tr
                    key={v.vehicle_id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.7 + i * 0.03 }}
                    className="border-b border-gray-800/50 hover:bg-gray-800/20"
                  >
                    <td className="py-3 px-2 font-medium">{v.vehicle_name}</td>
                    <td className="py-3 px-2 text-right text-gray-300">{v.miles.toLocaleString()}</td>
                    <td className="py-3 px-2 text-right text-gray-300">{v.est_mpg}</td>
                    <td className="py-3 px-2 text-right text-gray-300">{v.est_gallons}</td>
                    <td className="py-3 px-2 text-right text-gray-300">${v.est_cost}</td>
                    <td className="py-3 px-2 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${gradeColor(v.efficiency_grade)}`}>
                        {v.efficiency_grade}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">No efficiency data available yet</p>
        )}
      </motion.div>
    </div>
  )
}
