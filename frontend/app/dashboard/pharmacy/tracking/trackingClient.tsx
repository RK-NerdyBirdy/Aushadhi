"use client"

import { useEffect } from "react"
import dynamic from "next/dynamic"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Package, Truck, MapPin } from "lucide-react"

// CRITICAL: Import map with ssr: false to avoid hydration issues
const TrackingMap = dynamic(() => import("@/components/tracking-map"), {
  ssr: false,
  loading: () => (
    <div className="h-96 w-full rounded-md border bg-muted/50 flex items-center justify-center">
      <div className="flex flex-col items-center gap-2">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
        <p className="text-sm text-muted-foreground">Loading map...</p>
      </div>
    </div>
  ),
})

interface Props {
  batchInfo: any
  trail: any[]
}

export default function TrackingClient({ batchInfo, trail }: Props) {
  // Debug logging
  useEffect(() => {
    console.log("Batch Info:", batchInfo)
    console.log("Trail Data:", trail)
    console.log("Trail Length:", trail.length)
    
    if (trail.length > 0) {
      console.log("First Point:", trail[0])
      console.log("Last Point:", trail[trail.length - 1])
      
      // Check for invalid coordinates
      const invalidPoints = trail.filter(
        p => !p.latitude || !p.longitude || 
             p.latitude === 0 || p.longitude === 0 ||
             Math.abs(p.latitude) > 90 || Math.abs(p.longitude) > 180
      )
      if (invalidPoints.length > 0) {
        console.error("Invalid coordinate points found:", invalidPoints)
      }
    }
  }, [batchInfo, trail])

  return (
    <>
      {/* SUMMARY */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5" />
            Batch Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-6 text-sm">
          <div>
            <p className="text-muted-foreground mb-1">Medicine ID</p>
            <p className="font-medium">{batchInfo.medicine_id}</p>
          </div>
          <div>
            <p className="text-muted-foreground mb-1">Batch Number</p>
            <p className="font-medium">{batchInfo.batch_number}</p>
          </div>
          <div>
            <p className="text-muted-foreground mb-1">Expiry Date</p>
            <p className="font-medium">
              {batchInfo.expiry_date 
                ? new Date(batchInfo.expiry_date).toLocaleDateString()
                : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground mb-1">Quantity</p>
            <p className="font-medium">{batchInfo.quantity_available || 0}</p>
          </div>
          <div>
            <p className="text-muted-foreground mb-1">Shipment Number</p>
            <p className="font-medium text-white">{batchInfo.shipment_number || "Not shipped"}</p>
          </div>
          <div>
            <p className="text-muted-foreground mb-1">Shipment Status</p>
            <Badge variant={batchInfo.shipment_status ? "default" : "secondary"}>
              {batchInfo.shipment_status ?? "IN_WAREHOUSE"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* DEBUG INFO - Remove this after fixing */}
      <Card className="border-yellow-500 bg-yellow-50">
        <CardHeader>
          <CardTitle className="text-sm text-yellow-900">Debug Info</CardTitle>
        </CardHeader>
        <CardContent className="text-xs space-y-2">
          <p><strong>Trail points:</strong> {trail.length}</p>
          <p><strong>Shipment number:</strong> {batchInfo.shipment_number || "None"}</p>
          {trail.length > 0 && (
            <>
              <p><strong>First point:</strong> {trail[0].latitude}, {trail[0].longitude}</p>
              <p><strong>Last point:</strong> {trail[trail.length - 1].latitude}, {trail[trail.length - 1].longitude}</p>
            </>
          )}
        </CardContent>
      </Card>

      {/* MAP */}
      {trail.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Truck className="w-5 h-5" />
              Shipment Route ({trail.length} points)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TrackingMap trail={trail} />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              No Tracking Data
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {batchInfo.shipment_number 
                ? "No tracking points recorded for this shipment yet."
                : "This batch has not been shipped yet."}
            </p>
          </CardContent>
        </Card>
      )}

      {/* HISTORY */}
      {trail.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Location History</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Latitude</TableHead>
                  <TableHead>Longitude</TableHead>
                  <TableHead>Temp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {trail.map((p, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-sm">
                      {new Date(p.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        {p.status ?? "Unknown"}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {p.latitude ? Number(p.latitude).toFixed(6) : "N/A"}
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {p.longitude ? Number(p.longitude).toFixed(6) : "N/A"}
                    </TableCell>
                    <TableCell>
                      {p.temperature ? (
                        <span className={p.temperature > 25 ? "text-red-600 font-medium" : ""}>
                          {p.temperature}°C
                        </span>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </>
  )
}