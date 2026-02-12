import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Area,
  AreaChart
} from 'recharts'
import { TrendingUp, TrendingDown, Minus, CheckCircle, AlertTriangle, Target, Trophy, Fuel } from 'lucide-react'
import CountUp from 'react-countup'
import { useCoachingDrivers, useCoachingReports, acknowledgeCoaching } from '../hooks/useGeotab'
import type { DriverCoachingProfile, CoachingStatus, CoachingCategory } from '../types/fleet'

// Color schemes for different statuses
const statusConfig = {
  needs_attention: {
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    icon: AlertTriangle,
    label: 'Needs Attention'
  },
  on_track: {
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    icon: Target,
    label: 'On Track'
  },
  improved: {
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: Trophy,
    label: 'Improved!'
  }
}

const categoryLabels = {
  harsh_braking: 'Braking',
  harsh_acceleration: 'Acceleration',
  speeding: 'Speeding',
  cornering: 'Cornering',
  seatbelt: 'Seatbelt'
}

const trendIcons = {
  improving: TrendingUp,
  declining: TrendingDown,
  stable: Minus
}

const priorityColors = {
  1: 'border-red-500 bg-red-500/10',
  2: 'border-orange-500 bg-orange-500/10',
  3: 'border-amber-500 bg-amber-500/10',
  4: 'border-blue-500 bg-blue-500/10',
  5: 'border-gray-500 bg-gray-500/10'
}

function scoreColor(score: number): string {
  if (score >= 90) return 'text-emerald-400'
  if (score >= 70) return 'text-amber-400'
  return 'text-red-400'
}

function DriverCard({ driver, onAcknowledge }: { driver: DriverCoachingProfile, onAcknowledge: (id: string) => void }) {
  const [showDetail, setShowDetail] = useState(false)
  const config = statusConfig[driver.status]
  const StatusIcon = config.icon
  const TrendIcon = trendIcons[driver.trend.direction]

  // Prepare radar chart data
  const radarData = [
    { category: 'Braking', score: driver.scores.harsh_braking, fullMark: 100 },
    { category: 'Acceleration', score: driver.scores.harsh_acceleration, fullMark: 100 },
    { category: 'Speeding', score: driver.scores.speeding, fullMark: 100 },
    { category: 'Cornering', score: driver.scores.cornering, fullMark: 100 },
    { category: 'Seatbelt', score: driver.scores.seatbelt, fullMark: 100 },
  ]

  // Celebration effect for improved drivers
  const isImproved = driver.status === 'improved'

  return (
    <motion.div
      layout
      className="bg-gray-900 rounded-xl shadow-lg overflow-hidden border border-gray-800/50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className={`px-4 py-3 border-b border-gray-800 ${config.bg}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <StatusIcon className={`w-5 h-5 ${config.color}`} />
            <div>
              <h3 className="font-semibold text-white">{driver.driver_name}</h3>
              <p className={`text-sm ${config.color}`}>{config.label}</p>
            </div>
            {isImproved && (
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  rotate: [0, 10, -10, 0],
                }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  repeatDelay: 3,
                }}
              >
                🎉
              </motion.div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <div className={`text-2xl font-bold ${scoreColor(driver.overall_score)}`}>
              <CountUp end={driver.overall_score} duration={1} decimals={0} />
            </div>
            <TrendIcon className={`w-4 h-4 ${
              driver.trend.direction === 'improving' ? 'text-emerald-400' : 
              driver.trend.direction === 'declining' ? 'text-red-400' : 'text-gray-400'
            }`} />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Quick stats */}
        <div className="grid grid-cols-3 gap-4 mb-4 text-center">
          <div>
            <div className="text-lg font-semibold text-white">{driver.events_this_week}</div>
            <div className="text-xs text-gray-400">Events</div>
          </div>
          <div>
            <div className={`text-lg font-semibold flex items-center justify-center gap-1 ${
              driver.fuel_waste_pct > 15 ? 'text-red-400' : 
              driver.fuel_waste_pct > 5 ? 'text-amber-400' : 'text-emerald-400'
            }`}>
              <Fuel className="w-4 h-4" />
              <CountUp end={driver.fuel_waste_pct} duration={1} decimals={1} />%
            </div>
            <div className="text-xs text-gray-400">Fuel Waste</div>
          </div>
          <div>
            <div className={`text-lg font-semibold ${driver.acknowledged ? 'text-emerald-400' : 'text-gray-400'}`}>
              {driver.acknowledged ? '✓' : '○'}
            </div>
            <div className="text-xs text-gray-400">Reviewed</div>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="h-48 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="category" tick={{ fill: '#9CA3AF', fontSize: 10 }} />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]} 
                tick={{ fill: '#6B7280', fontSize: 8 }} 
                tickCount={3}
              />
              <Radar
                name="Score"
                dataKey="score"
                stroke={driver.overall_score >= 90 ? '#10B981' : driver.overall_score >= 70 ? '#F59E0B' : '#EF4444'}
                fill={driver.overall_score >= 90 ? '#10B981' : driver.overall_score >= 70 ? '#F59E0B' : '#EF4444'}
                fillOpacity={0.1}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Recommendations */}
        {driver.recommendations.length > 0 && (
          <div className="space-y-2 mb-4">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Coaching Recommendations</h4>
            {driver.recommendations.slice(0, 2).map((rec, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${priorityColors[rec.priority as keyof typeof priorityColors]} text-sm`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium">Priority {rec.priority}</span>
                  <span className="text-xs text-gray-400">•</span>
                  <span className="text-xs">{categoryLabels[rec.category]}</span>
                  {rec.fuel_impact_pct > 0 && (
                    <>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-amber-400">+{rec.fuel_impact_pct}% fuel cost</span>
                    </>
                  )}
                </div>
                <p className="text-gray-200">{rec.message}</p>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowDetail(!showDetail)}
            className="flex-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            {showDetail ? 'Hide Details' : 'View Details'}
          </button>
          {!driver.acknowledged && (
            <button
              onClick={() => onAcknowledge(driver.driver_id)}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm transition-colors flex items-center gap-1"
            >
              <CheckCircle className="w-4 h-4" />
              Acknowledge
            </button>
          )}
        </div>

        {/* Detailed trend view */}
        <AnimatePresence>
          {showDetail && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mt-4 pt-4 border-t border-gray-800"
            >
              <h5 className="text-sm font-medium text-gray-300 mb-2">Trend Analysis</h5>
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div>
                  <div className="text-white font-medium">{driver.trend.current_week.toFixed(1)}</div>
                  <div className="text-gray-400">This Week</div>
                </div>
                <div>
                  <div className="text-white font-medium">{driver.trend.last_week.toFixed(1)}</div>
                  <div className="text-gray-400">Last Week</div>
                </div>
                <div>
                  <div className="text-white font-medium">{driver.trend.four_weeks_avg.toFixed(1)}</div>
                  <div className="text-gray-400">4-Week Avg</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default function DriverCoaching() {
  const coachingData = useCoachingDrivers()
  const reportsData = useCoachingReports()
  const [filter, setFilter] = useState<CoachingStatus | 'all'>('all')

  const handleAcknowledge = async (driverId: string) => {
    try {
      await acknowledgeCoaching(driverId)
      coachingData.refresh()
    } catch (error) {
      console.error('Failed to acknowledge coaching:', error)
    }
  }

  const filteredDrivers = coachingData.data?.filter(driver => 
    filter === 'all' ? true : driver.status === filter
  ) || []

  // Sort drivers: needs attention first, then by score
  const sortedDrivers = [...filteredDrivers].sort((a, b) => {
    if (a.status === 'needs_attention' && b.status !== 'needs_attention') return -1
    if (b.status === 'needs_attention' && a.status !== 'needs_attention') return 1
    return a.overall_score - b.overall_score
  })

  return (
    <div className="space-y-6">
      {/* Fleet Coaching Summary */}
      {reportsData.data && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-900 rounded-xl shadow-lg overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-gray-800">
            <h2 className="text-xl font-bold flex items-center gap-2">
              🏆 Fleet Coaching Summary
              <span className="text-sm bg-gray-800 px-2 py-1 rounded-full text-gray-400">
                {reportsData.data.total_drivers} Drivers
              </span>
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-400">
                  <CountUp end={reportsData.data.average_score} duration={2} decimals={1} />
                </div>
                <div className="text-sm text-gray-400">Average Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">
                  <CountUp end={reportsData.data.needs_attention} duration={2} />
                </div>
                <div className="text-sm text-gray-400">Need Attention</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-400">
                  <CountUp end={reportsData.data.on_track} duration={2} />
                </div>
                <div className="text-sm text-gray-400">On Track</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  <CountUp end={reportsData.data.improved} duration={2} />
                </div>
                <div className="text-sm text-gray-400">Improved</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-amber-400 flex items-center justify-center gap-1">
                  <Fuel className="w-5 h-5" />
                  <CountUp end={reportsData.data.fleet_fuel_savings_potential} duration={2} decimals={1} />%
                </div>
                <div className="text-sm text-gray-400">Savings Potential</div>
              </div>
            </div>

            {/* Best Improved and Worst Performers */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {reportsData.data.best_improved.length > 0 && (
                <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/30">
                  <h3 className="font-medium text-blue-400 mb-2 flex items-center gap-2">
                    🌟 Most Improved Drivers
                  </h3>
                  <div className="space-y-1">
                    {reportsData.data.best_improved.map((name, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <motion.span
                          animate={{ scale: [1, 1.1, 1] }}
                          transition={{ delay: index * 0.2, duration: 0.5 }}
                        >
                          🎉
                        </motion.span>
                        <span className="text-white">{name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {reportsData.data.worst_performers.length > 0 && (
                <div className="bg-amber-500/10 rounded-lg p-4 border border-amber-500/30">
                  <h3 className="font-medium text-amber-400 mb-2 flex items-center gap-2">
                    ⚠️ Needs Focus
                  </h3>
                  <div className="space-y-1">
                    {reportsData.data.worst_performers.map((name, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <span className="text-amber-400">•</span>
                        <span className="text-white">{name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Filter Controls */}
      <div className="bg-gray-900 rounded-xl p-4 shadow-lg">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              filter === 'all' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            All Drivers ({coachingData.data?.length || 0})
          </button>
          <button
            onClick={() => setFilter('needs_attention')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              filter === 'needs_attention' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Needs Attention ({coachingData.data?.filter(d => d.status === 'needs_attention').length || 0})
          </button>
          <button
            onClick={() => setFilter('on_track')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              filter === 'on_track' 
                ? 'bg-emerald-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            On Track ({coachingData.data?.filter(d => d.status === 'on_track').length || 0})
          </button>
          <button
            onClick={() => setFilter('improved')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              filter === 'improved' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Improved! ({coachingData.data?.filter(d => d.status === 'improved').length || 0})
          </button>
        </div>
      </div>

      {/* Driver Cards */}
      <div>
        {coachingData.loading && (
          <div className="text-center py-12 text-gray-500">
            Loading driver coaching data...
          </div>
        )}
        
        {coachingData.error && (
          <div className="text-center py-12 text-red-400">
            Error loading coaching data: {coachingData.error}
          </div>
        )}

        {sortedDrivers.length === 0 && !coachingData.loading && (
          <div className="text-center py-12 text-gray-500">
            No drivers found for the selected filter.
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {sortedDrivers.map((driver) => (
              <DriverCard
                key={driver.driver_id}
                driver={driver}
                onAcknowledge={handleAcknowledge}
              />
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}