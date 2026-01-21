"use client"

import { useEffect, useState } from "react"
import { getDashboardMetrixs } from "@/app/apis/dashboard"
import StatsCard from "@/components/stats-card"

export default function PharmacyDashboard() {
  const [metrics, setMetrics] = useState<any | null>(null)

  useEffect(() => {
    getDashboardMetrixs()
      .then((data) => {
        console.log("API DATA:", data)
        setMetrics(data)
      })
      .catch(console.error)
  }, [])

  if (metrics === null) {
    return <p>Loading dashboard...</p>
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

        <StatsCard
          title="Total Medicines"
          change=""
          subtitle=""
          value={metrics.total_medicines}
        />

        <StatsCard
          title="Total Stock Value"
          change=""
          subtitle=""
          value={`₹${metrics.total_stock_value.toLocaleString()}`}
        />

        <StatsCard
          title="Low Stock"
          subtitle=""
          change=""
          value={metrics.low_stock_count}
        />

        <StatsCard
          title="Expiring Soon"
          change=""
          subtitle=""
          value={metrics.expiring_soon_count}
        />

        <StatsCard
          title="Active Alerts"
          subtitle=""
          change=""
          value={metrics.active_alerts_count}
        />

        <StatsCard
          title="Pending Orders"
          subtitle=""
          change=""
          value={metrics.pending_orders_count}
        />

      </div>
    </div>
  )
}