import { sql } from "@/app/apis/db"
import TrackingClient from "./trackingClient"
import { Card, CardContent } from "@/components/ui/card"
import { AlertCircle } from "lucide-react"

export default async function TrackPage({
  searchParams,
}: {
  searchParams: Promise<{ batch?: string }>
}) {
  const { batch } = await searchParams

  let batchInfo = null
  let trail: any[] = []
  let error = null

  if (batch) {
    try {
      // Get batch info
      const batchData = await sql`
        SELECT
          wi.inventory_id,
          wi.medicine_id,
          wi.batch_number,
          wi.expiry_date,
          wi.quantity_available,
          wi.unit_price,
          os.shipment_id,
          os.shipment_number,
          os.shipment_status,
          os.hospital_id
        FROM warehouse_inventory wi
        LEFT JOIN shipment_batches sb ON wi.inventory_id = sb.inventory_id
        LEFT JOIN outbound_shipments os ON sb.shipment_id = os.shipment_id
        WHERE wi.batch_number = ${batch}
        LIMIT 1;
      `

      if (batchData.length === 0) {
        error = `Batch number "${batch}" not found in the system.`
      } else {
        batchInfo = batchData[0]

        // Get tracking trail if shipment exists
        if (batchInfo?.shipment_number) {
          trail = await sql`
            SELECT
              st.latitude,
              st.longitude,
              st.timestamp,
              st.status,
              st.temperature
            FROM shipment_tracking st
            JOIN outbound_shipments os ON st.shipment_id = os.shipment_id
            WHERE os.shipment_number = ${batchInfo.shipment_number}
            ORDER BY st.timestamp ASC;
          `
          
          console.log(`Found ${trail.length} tracking points for shipment ${batchInfo.shipment_number}`)
        }
      }
    } catch (err) {
      console.error("Database error:", err)
      error = "An error occurred while fetching tracking data."
    }
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Medicine Tracking</h1>
        <p className="text-muted-foreground mt-1">
          Track batch movement and shipment route
        </p>
      </div>

      {/* Search Form */}
      <Card>
        <CardContent className="pt-6">
          <form className="flex gap-3">
            <input
              name="batch"
              placeholder="Enter batch number (e.g., BATCH001)"
              defaultValue={batch ?? ""}
              className="flex-1 max-w-md border px-4 py-2 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
              required
            />
            <button 
              type="submit"
              className="px-6 py-2 bg-black text-white rounded-md text-sm font-medium hover:bg-black/90 transition-colors"
            >
              Track Batch
            </button>
          </form>
        </CardContent>
      </Card>

      {/* Error Message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tracking Results */}
      {batchInfo && !error && (
        <TrackingClient batchInfo={batchInfo} trail={trail} />
      )}

      {/* Initial State */}
      {!batch && !error && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground text-center py-8">
              Enter a batch number above to track its location and shipment history
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}