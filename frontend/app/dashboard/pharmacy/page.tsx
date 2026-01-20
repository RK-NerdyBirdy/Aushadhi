import StatsCard from "@/components/stats-card"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import DashboardAreaChart from "@/components/charts/area-chart"

export default function PharmacyDashboard() {
  return (
    <div className="space-y-6">

      {/* KPI CARDS */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Stock"
          value="2,45,000"
          change="+12.5%"
          subtitle="Compared to last month"
        />

        <StatsCard
          title="Low Stock Items"
          value="18"
          change="-20%"
          positive={false}
          subtitle="Needs replenishment"
        />

        <StatsCard
          title="Active Medicines"
          value="312"
          change="+8.2%"
          subtitle="Across all categories"
        />

        <StatsCard
          title="Expiry Risk"
          value="4.5%"
          change="+1.1%"
          subtitle="Within next 30 days"
        />
      </div>

      {/* CHART */}
      <Card>
        <CardHeader>
          <CardTitle>Total Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <DashboardAreaChart />
        </CardContent>
      </Card>

    </div>
  )
}