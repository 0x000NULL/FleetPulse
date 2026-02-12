import { motion } from 'framer-motion'
import CountUp from 'react-countup'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import type { FleetOverview } from '../types/fleet'

interface Props {
  overview: FleetOverview | null
  loading: boolean
}

const cards = [
  { 
    key: 'total_vehicles', 
    label: 'Total Vehicles', 
    icon: '🚗', 
    color: 'from-blue-500 to-blue-700',
    sparkline: [48, 49, 50, 49, 50, 50],
    trend: 'stable'
  },
  { 
    key: 'active', 
    label: 'Active', 
    icon: '🟢', 
    color: 'from-emerald-500 to-emerald-700',
    sparkline: [32, 35, 28, 42, 38, 40],
    trend: 'up'
  },
  { 
    key: 'idle', 
    label: 'Idle', 
    icon: '🟡', 
    color: 'from-amber-500 to-amber-700',
    sparkline: [8, 6, 12, 4, 7, 5],
    trend: 'down'
  },
  { 
    key: 'parked', 
    label: 'Parked', 
    icon: '🔵', 
    color: 'from-slate-500 to-slate-700',
    sparkline: [10, 9, 10, 4, 5, 5],
    trend: 'stable'
  },
  { 
    key: 'total_trips_today', 
    label: 'Trips Today', 
    icon: '📊', 
    color: 'from-purple-500 to-purple-700',
    sparkline: [125, 138, 142, 155, 167, 172],
    trend: 'up'
  },
  { 
    key: 'total_distance_km', 
    label: 'Distance (km)', 
    icon: '🛣️', 
    color: 'from-cyan-500 to-cyan-700',
    sparkline: [1200, 1350, 1450, 1380, 1520, 1680],
    trend: 'up'
  },
  { 
    key: 'avg_trip_duration_min', 
    label: 'Avg Duration (min)', 
    icon: '⏱️', 
    color: 'from-rose-500 to-rose-700',
    sparkline: [45, 42, 48, 44, 41, 43],
    trend: 'stable'
  },
  { 
    key: 'avg_trip_distance_km', 
    label: 'Avg Distance (km)', 
    icon: '📏', 
    color: 'from-indigo-500 to-indigo-700',
    sparkline: [12, 11, 13, 12, 14, 13],
    trend: 'stable'
  },
] as const

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05
    }
  }
}

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: {
      type: "spring" as const,
      stiffness: 400,
      damping: 25
    }
  }
}

export default function Dashboard({ overview, loading }: Props) {
  const sparklineData = (data: readonly number[] | number[]) => [...data].map((value, index) => ({ x: index, y: value }))

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '📈'
      case 'down': return '📉'
      default: return '➡️'
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-emerald-400'
      case 'down': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <motion.div 
      className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {cards.map((c, index) => (
        <motion.div
          key={c.key}
          variants={cardVariants}
          whileHover={{ 
            scale: 1.02,
            transition: { type: "spring" as const, stiffness: 400, damping: 25 }
          }}
          className={`relative bg-gradient-to-br ${c.color} rounded-xl p-4 shadow-lg hover:shadow-xl transition-shadow duration-300 border border-white/10 backdrop-blur-sm group overflow-hidden`}
        >
          {/* Background gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          
          {/* Content */}
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-lg">{c.icon}</span>
              <span className={`text-xs ${getTrendColor(c.trend)}`}>
                {getTrendIcon(c.trend)}
              </span>
            </div>
            
            <div className="text-2xl font-bold mb-1">
              {loading ? (
                <div className="animate-pulse bg-white/20 rounded h-6 w-12" />
              ) : (
                <CountUp
                  end={(overview as any)?.[c.key] ?? 0}
                  duration={1.2}
                  delay={index * 0.1}
                  preserveValue
                />
              )}
            </div>
            
            <div className="text-xs text-white/70 mb-2">{c.label}</div>
            
            {/* Sparkline */}
            <div className="h-6 w-full mt-2">
              {!loading && (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sparklineData(c.sparkline)}>
                    <Line 
                      type="monotone" 
                      dataKey="y" 
                      stroke="rgba(255,255,255,0.6)" 
                      strokeWidth={1.5}
                      dot={false}
                      activeDot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </motion.div>
      ))}
    </motion.div>
  )
}
