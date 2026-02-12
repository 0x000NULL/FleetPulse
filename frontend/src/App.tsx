import { useCallback, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, Zap } from 'lucide-react'
import Dashboard from './components/Dashboard'
import FleetAnalytics from './components/FleetAnalytics'
import FleetChat from './components/FleetChat'
import FleetMap from './components/FleetMap'
import VehicleList from './components/VehicleList'
import SafetyScorecard from './components/SafetyScorecard'
import Leaderboard from './components/Leaderboard'
import AlertFeed from './components/AlertFeed'
import LocationCard from './components/LocationCard'
import AgenticMonitor from './components/AgenticMonitor'
import { useFleetOverview, useVehicles, useSafetyScores, useLeaderboard, useAlerts, useLocations, useMonitorAlerts, useMonitorStatus } from './hooks/useGeotab'

export default function App() {
  const [chatOpen, setChatOpen] = useState(false)
  
  const overview = useFleetOverview()
  const vehicles = useVehicles()
  const safety = useSafetyScores()
  const leaderboard = useLeaderboard()
  const alerts = useAlerts()
  const locations = useLocations()
  const monitorAlerts = useMonitorAlerts()
  const monitorStatus = useMonitorStatus()

  const triggerCheck = useCallback(() => {
    fetch('/api/monitor/check', { method: 'POST' }).then(() => {
      monitorAlerts.refresh()
      monitorStatus.refresh()
    })
  }, [monitorAlerts, monitorStatus])

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 }
  }

  const pageTransition = {
    type: 'tween' as const,
    ease: 'anticipate' as const,
    duration: 0.5
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Header */}
      <motion.header 
        className="border-b border-gray-800/50 px-4 sm:px-6 py-4 flex items-center justify-between backdrop-blur-xl bg-gray-950/80"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center gap-3">
          <motion.span 
            className="text-3xl"
            animate={{ rotate: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          >
            🚗
          </motion.span>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
              FleetPulse
            </h1>
            <p className="text-xs text-gray-500 hidden sm:block">Budget Rent a Car · Las Vegas · 8 Locations</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <motion.span 
            className="inline-block w-2 h-2 rounded-full bg-emerald-400"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span className="hidden sm:inline">Live</span>
        </div>
      </motion.header>

      <motion.main 
        className="p-4 sm:p-6 space-y-6 max-w-[1800px] mx-auto"
        variants={pageVariants}
        initial="initial"
        animate="in"
        exit="out"
        transition={pageTransition}
      >
        {/* KPI Cards */}
        <section>
          <Dashboard overview={overview.data} loading={overview.loading} />
        </section>

        {/* Fleet Analytics */}
        <section>
          <FleetAnalytics loading={overview.loading} />
        </section>

        {/* Map + Alerts row */}
        <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              <FleetMap vehicles={vehicles.data} locations={locations.data} />
            </motion.div>
          </div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <AlertFeed alerts={alerts.data} loading={alerts.loading} />
          </motion.div>
        </section>

        {/* Agentic Monitor */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            <AgenticMonitor
              alerts={monitorAlerts.data}
              status={monitorStatus.data}
              loading={monitorAlerts.loading}
              onTriggerCheck={triggerCheck}
            />
          </motion.div>
        </section>

        {/* Safety + Leaderboard row */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            <SafetyScorecard scores={safety.data} loading={safety.loading} />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.5 }}
          >
            <Leaderboard drivers={leaderboard.data} loading={leaderboard.loading} />
          </motion.div>
        </section>

        {/* Vehicles */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.5 }}
          >
            <VehicleList vehicles={vehicles.data} loading={vehicles.loading} />
          </motion.div>
        </section>

        {/* Location Cards */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.5 }}
          >
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              📍 Locations
              <span className="text-xs bg-gray-800 px-2 py-1 rounded-full text-gray-400">
                8 Active
              </span>
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {locations.data?.map((loc, index) => (
                <motion.div
                  key={loc.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.0 + index * 0.1, duration: 0.3 }}
                >
                  <LocationCard location={loc} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        </section>
      </motion.main>

      {/* AI Chat Floating Action Button */}
      <motion.button
        onClick={() => setChatOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full shadow-lg hover:shadow-xl flex items-center justify-center group z-40"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, y: 100 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2, type: "spring" as const, stiffness: 400, damping: 25 }}
      >
        <MessageCircle className="w-6 h-6 text-white" />
        <motion.div
          className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center"
          animate={{ scale: [1, 1.2, 1], opacity: [1, 0.8, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Zap className="w-2 h-2 text-white" />
        </motion.div>
        
        {/* Tooltip */}
        <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          Ask AI about your fleet
          <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
        </div>
      </motion.button>

      {/* AI Chat Interface */}
      <AnimatePresence>
        {chatOpen && <FleetChat isOpen={chatOpen} onClose={() => setChatOpen(false)} />}
      </AnimatePresence>
    </div>
  )
}
