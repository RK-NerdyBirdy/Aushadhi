"use client"

import { useEffect, useMemo } from "react"
import "leaflet/dist/leaflet.css"
import L from "leaflet"
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Popup,
} from "react-leaflet"

interface Point {
  latitude: number
  longitude: number
  timestamp: string
  status?: string
}

export default function TrackingMap({ trail }: { trail: Point[] }) {
  // Fix Leaflet icon issue in Next.js
  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    })
  }, [])

  // Memoize positions to avoid recalculating on every render
  const positions = useMemo(
    () => trail.map((p) => [
      Number(p.latitude), 
      Number(p.longitude)
    ] as [number, number]),
    [trail]
  )

  if (!trail.length) {
    return (
      <div className="flex h-96 w-full items-center justify-center rounded-md border bg-muted/50">
        <p className="text-sm text-muted-foreground">No tracking data available</p>
      </div>
    )
  }

  // Validate that we have valid coordinates
  const hasValidCoordinates = trail.every(
    p => p.latitude && p.longitude && 
         !isNaN(Number(p.latitude)) && !isNaN(Number(p.longitude))
  )

  if (!hasValidCoordinates) {
    return (
      <div className="flex h-96 w-full items-center justify-center rounded-md border bg-red-50">
        <p className="text-sm text-red-600">Invalid coordinate data in tracking points</p>
      </div>
    )
  }

  const centerLat = Number(trail[0].latitude)
  const centerLng = Number(trail[0].longitude)

  return (
    <div className="h-96 w-full rounded-md overflow-hidden border">
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={6}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution="© OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Route line */}
        <Polyline
          positions={positions}
          pathOptions={{
            color: "#16a34a",
            weight: 5,
            opacity: 0.8,
          }}
        />

        {/* Markers */}
        {trail.map((point, index) => (
          <Marker
            key={`${point.latitude}-${point.longitude}-${index}`}
            position={[Number(point.latitude), Number(point.longitude)]}
          >
            <Popup>
              <div className="text-sm space-y-1">
                <div>
                  <span className="font-medium">Status:</span>{" "}
                  {point.status ?? "N/A"}
                </div>
                <div>
                  <span className="font-medium">Time:</span>{" "}
                  {new Date(point.timestamp).toLocaleString()}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Point {index + 1} of {trail.length}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}