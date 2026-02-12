import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from 'react-leaflet'
import { Eye, EyeOff, Activity, MapPin, Navigation, Layers } from 'lucide-react'
import L from 'leaflet'
import type { Vehicle, LocationStats } from '../types/fleet'

interface Props {
  vehicles: Vehicle[] | null
  locations: LocationStats[] | null
}

const statusColor: Record<string, string> = {
  active: '#10b981',
  idle: '#f59e0b', 
  parked: '#6366f1',
  offline: '#6b7280',
}

const statusEmoji: Record<string, string> = {
  active: '🟢',
  idle: '🟡',
  parked: '🔵', 
  offline: '⚫'
}

function vehicleIcon(status: string, isMoving: boolean = false) {
  const color = statusColor[status] || '#6b7280'
  const size = isMoving ? 16 : 14
  const animation = isMoving ? 'animation: pulse 1.5s infinite;' : ''
  
  return L.divIcon({
    className: '',
    html: `
      <div style="
        width:${size}px;
        height:${size}px;
        border-radius:50%;
        background:${color};
        border:2px solid white;
        box-shadow:0 0 8px rgba(0,0,0,.6);
        ${animation}
        transform: translate(-50%, -50%);
      "></div>
      <style>
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 8px rgba(0,0,0,.6), 0 0 0 0 ${color}; }
          50% { box-shadow: 0 0 8px rgba(0,0,0,.6), 0 0 0 6px rgba(16, 185, 129, 0.2); }
        }
      </style>
    `,
    iconSize: [size, size],
    iconAnchor: [size/2, size/2],
  })
}

function locationIcon(locationStats: LocationStats) {
  const color = locationStats.safety_score >= 90 ? '#10b981' : locationStats.safety_score >= 85 ? '#f59e0b' : '#ef4444'
  return L.divIcon({
    className: '',
    html: `
      <div style="
        width: 24px;
        height: 24px;
        background: ${color};
        border: 3px solid white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
      ">${locationStats.vehicle_count}</div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  })
}

export default function FleetMap({ vehicles, locations }: Props) {
  const [showVehicles, setShowVehicles] = useState(true)
  const [showLocations, setShowLocations] = useState(true)
  const [showRoutes, setShowRoutes] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)

  // Las Vegas center
  const center: [number, number] = [36.12, -115.16]

  // Filter vehicles by selected location
  const filteredVehicles = useMemo(() => {
    if (!vehicles) return []
    if (!selectedLocation) return vehicles
    return vehicles.filter(v => v.location_name === selectedLocation)
  }, [vehicles, selectedLocation])

  // Generate mock route for demonstration
  const mockRoute = useMemo(() => {
    if (!showRoutes || !vehicles) return []
    const activeVehicles = vehicles.filter(v => v.status === 'active' && v.position).slice(0, 5)
    return activeVehicles.map(v => {
      const basePos = [v.position!.latitude, v.position!.longitude]
      // Generate a simple route path
      const route = [
        [basePos[0] - 0.01, basePos[1] - 0.01],
        [basePos[0] - 0.005, basePos[1]],
        basePos,
        [basePos[0] + 0.005, basePos[1] + 0.005]
      ] as [number, number][]
      return { vehicleId: v.id, route, color: statusColor[v.status] }
    })
  }, [vehicles, showRoutes])

  // Status summary
  const statusSummary = useMemo(() => {
    if (!vehicles) return {}
    return vehicles.reduce((acc, v) => {
      acc[v.status] = (acc[v.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [vehicles])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-br from-gray-900 to-gray-800 dark:from-gray-900 dark:to-gray-800 light:from-white light:to-gray-50 rounded-xl overflow-hidden shadow-lg border border-gray-800 dark:border-gray-800 light:border-gray-200"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800/50 bg-gradient-to-r from-gray-800 to-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-400" />
            Live Fleet Map
            <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded-full">
              Real-time
            </span>
          </h2>
          
          {/* Map Controls */}
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowVehicles(!showVehicles)}
              className={`p-2 rounded-lg transition-colors flex items-center gap-1 ${
                showVehicles ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'
              }`}
            >
              {showVehicles ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              <span className="hidden sm:inline text-xs">Vehicles</span>
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowLocations(!showLocations)}
              className={`p-2 rounded-lg transition-colors flex items-center gap-1 ${
                showLocations ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-400'
              }`}
            >
              <MapPin className="w-4 h-4" />
              <span className="hidden sm:inline text-xs">Locations</span>
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowRoutes(!showRoutes)}
              className={`p-2 rounded-lg transition-colors flex items-center gap-1 ${
                showRoutes ? 'bg-emerald-600 text-white' : 'bg-gray-700 text-gray-400'
              }`}
            >
              <Navigation className="w-4 h-4" />
              <span className="hidden sm:inline text-xs">Routes</span>
            </motion.button>
          </div>
        </div>

        {/* Status Legend & Location Filter */}
        <div className="flex items-center justify-between">
          <div className="flex gap-3 text-xs">
            {Object.entries(statusColor).map(([status, color]) => (
              <motion.span
                key={status}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-1.5 text-gray-300"
              >
                <span 
                  className="inline-block w-2.5 h-2.5 rounded-full"
                  style={{ background: color }}
                />
                <span className="capitalize">{status}</span>
                <span className="text-gray-500">({statusSummary[status] || 0})</span>
              </motion.span>
            ))}
          </div>

          {/* Location Filter */}
          <select
            value={selectedLocation || ''}
            onChange={(e) => setSelectedLocation(e.target.value || null)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-2 py-1 text-xs focus:outline-none focus:border-blue-500"
          >
            <option value="">All Locations</option>
            {locations?.map(loc => (
              <option key={loc.name} value={loc.name}>{loc.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative">
        {(!vehicles && !locations) ? (
          <div className="h-[420px] flex items-center justify-center bg-gray-800/50">
            <div className="flex items-center gap-3 text-gray-400">
              <div className="animate-spin w-6 h-6 border-2 border-gray-600 border-t-gray-400 rounded-full"></div>
              Loading map data...
            </div>
          </div>
        ) : (
          <MapContainer 
            center={center} 
            zoom={11} 
            style={{ height: 420 }} 
            scrollWheelZoom
            className="z-10"
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            
            {/* Location zones and markers */}
            {showLocations && locations?.map(loc => (
              <div key={loc.name}>
                <Circle
                  center={[loc.latitude, loc.longitude]}
                  radius={300}
                  pathOptions={{ 
                    color: loc.safety_score >= 90 ? '#10b981' : loc.safety_score >= 85 ? '#f59e0b' : '#ef4444',
                    fillOpacity: 0.1, 
                    weight: 2,
                    dashArray: selectedLocation === loc.name ? '0' : '5, 5'
                  }}
                />
                <Marker
                  position={[loc.latitude, loc.longitude]}
                  icon={locationIcon(loc)}
                >
                  <Popup className="dark-popup">
                    <div className="text-sm">
                      <div className="font-semibold text-white mb-1">{loc.name}</div>
                      <div className="text-gray-300 space-y-1">
                        <div>🚗 {loc.vehicle_count} vehicles</div>
                        <div>🛡️ Safety: {loc.safety_score}%</div>
                        <div>📊 Utilization: {Math.round(loc.vehicle_count / 8 * 100)}%</div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              </div>
            ))}
            
            {/* Vehicle markers */}
            {showVehicles && filteredVehicles?.filter(v => v.position).map(v => (
              <Marker
                key={v.id}
                position={[v.position!.latitude, v.position!.longitude]}
                icon={vehicleIcon(v.status, v.status === 'active' && (v.position?.speed || 0) > 5)}
              >
                <Popup className="dark-popup">
                  <div className="text-sm">
                    <div className="font-semibold text-white mb-1 flex items-center gap-2">
                      {statusEmoji[v.status]} {v.name}
                    </div>
                    <div className="text-gray-300 space-y-1">
                      <div>Status: <span className="capitalize">{v.status}</span></div>
                      <div>Speed: {v.position!.speed || 0} km/h</div>
                      {v.location_name && <div>📍 {v.location_name}</div>}
                      {v.last_contact && (
                        <div className="text-xs text-gray-400">
                          Last contact: {new Date(v.last_contact).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Route trails */}
            {showRoutes && mockRoute.map(({ vehicleId, route, color }) => (
              <Polyline
                key={vehicleId}
                positions={route}
                pathOptions={{
                  color,
                  weight: 3,
                  opacity: 0.6,
                  dashArray: '10, 5'
                }}
              />
            ))}
          </MapContainer>
        )}

        {/* Map overlay info */}
        <div className="absolute bottom-4 left-4 bg-black/70 dark:bg-black/70 light:bg-white/90 backdrop-blur-sm rounded-lg p-3 text-xs text-white dark:text-white light:text-gray-900 z-20 border border-gray-700 dark:border-gray-700 light:border-gray-200">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Activity className="w-3 h-3 text-emerald-400" />
              <span>{filteredVehicles?.filter(v => v.status === 'active').length || 0} active</span>
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-3 h-3 text-blue-400" />
              <span>{locations?.length || 0} locations</span>
            </div>
            {selectedLocation && (
              <div className="text-yellow-400">
                Filtered: {selectedLocation}
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
