import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
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

function vehicleIcon(status: string) {
  const color = statusColor[status] || '#6b7280'
  return L.divIcon({
    className: '',
    html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,.4)"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  })
}

export default function FleetMap({ vehicles, locations }: Props) {
  // Las Vegas center
  const center: [number, number] = [36.12, -115.16]

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg">
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
        <h2 className="font-semibold">🗺️ Fleet Map</h2>
        <div className="flex gap-3 text-xs">
          {Object.entries(statusColor).map(([s, c]) => (
            <span key={s} className="flex items-center gap-1">
              <span style={{ background: c }} className="inline-block w-2 h-2 rounded-full" />
              {s}
            </span>
          ))}
        </div>
      </div>
      <MapContainer center={center} zoom={11} style={{ height: 420 }} scrollWheelZoom>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        />
        {/* Location zones */}
        {locations?.map(loc => (
          <Circle
            key={loc.name}
            center={[loc.latitude, loc.longitude]}
            radius={200}
            pathOptions={{ color: '#3b82f6', fillOpacity: 0.15, weight: 1 }}
          >
            <Popup>
              <strong>{loc.name}</strong><br />
              {loc.vehicle_count} vehicles · Safety {loc.safety_score}
            </Popup>
          </Circle>
        ))}
        {/* Vehicle markers */}
        {vehicles?.filter(v => v.position).map(v => (
          <Marker
            key={v.id}
            position={[v.position!.latitude, v.position!.longitude]}
            icon={vehicleIcon(v.status)}
          >
            <Popup>
              <strong>{v.name}</strong><br />
              Status: {v.status}<br />
              Speed: {v.position!.speed} km/h
              {v.location_name && <><br />📍 {v.location_name}</>}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
