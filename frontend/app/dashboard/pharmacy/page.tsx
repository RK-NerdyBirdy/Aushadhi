"use client"

import { useEffect, useState } from "react"
import { getDashboardMetrixs } from "@/app/apis/dashboard"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

import {
  Boxes,
  TrendingUp,
  AlertTriangle,
  Activity,
} from "lucide-react"

import StatsCard from "@/components/stats-card"

export default function PharmacyDashboard() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    getDashboardMetrixs()
      .then(setData)
      .catch(console.error)
  }, [])

  if (!data) return null

  const {
    summary,
    top_medicines,
    top_usage,
    usage_metrics,
    recent_alerts,
  } = data

  return (
    <div className="space-y-6">

      {/* PAGE HEADER */}
      <div className="space-y-0.5">
        <h1 className="text-2xl font-bold tracking-tight">
          Dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          Inventory overview, usage insights and system alerts
        </p>
      </div>

      {/* KPI CARDS */}
      <div className="grid grid-cols-4 gap-2 lg:grid-cols-4">
        <StatsCard 
          title="Medicines" 
          value={summary.total_medicines} 
          change="" 
          subtitle=""
        />
        <StatsCard
          title="Stock Value"
          value={`₹${(summary.total_stock_value / 10000).toFixed(2)}`}
          change="" 
          subtitle=""
        />
        <StatsCard 
          title="Low Stock" 
          value={summary.low_stock_count} 
          change="" 
          subtitle="" 
        />
        <StatsCard 
          title="Expiring Soon" 
          value={summary.expiring_soon_count} 
          change="" 
          subtitle=""
        />
        <StatsCard 
          title="Active Alerts" 
          value={summary.active_alerts_count} 
          change="" 
          subtitle=""
        />
        <StatsCard 
          title="Pending Orders" 
          value={summary.pending_orders_count} 
          change="" 
          subtitle=""
        />
      </div>

      <Separator className="my-8" />

      {/* ANALYTICS */}
      <div className="grid gap-4 lg:grid-cols-2">

        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-base font-semibold">Usage Overview</CardTitle>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                Total usage (7 days)
              </span>
              <span className="text-xl font-bold">
                {usage_metrics.total_usage_7_days.toLocaleString()}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                Average daily usage
              </span>
              <span className="text-xl font-bold">
                {usage_metrics.avg_daily_usage.toFixed(0)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-base font-semibold">System Status</CardTitle>
            </div>
          </CardHeader>

          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="text-xs px-2.5 py-0.5">
                Expired: {summary.expired_count}
              </Badge>
              <Badge variant="outline" className="text-xs px-2.5 py-0.5">
                Low stock: {summary.low_stock_count}
              </Badge>
              <Badge variant="outline" className="text-xs px-2.5 py-0.5">
                Alerts: {summary.active_alerts_count}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* TOP MEDICINES */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Boxes className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-base font-semibold">Top Medicines by Stock</CardTitle>
          </div>
        </CardHeader>

        <CardContent className="px-0">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="pl-6">Medicine</TableHead>
                <TableHead>ID</TableHead>
                <TableHead className="text-right pr-6">
                  Quantity
                </TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {top_medicines.map((m: any) => (
                <TableRow key={m.medicine_id}>
                  <TableCell className="font-medium pl-6">{m.medicine_name}</TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {m.medicine_id}
                  </TableCell>
                  <TableCell className="text-right font-semibold pr-6">
                    {m.quantity.toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* TOP USAGE */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-base font-semibold">Most Used Medicines</CardTitle>
          </div>
        </CardHeader>

        <CardContent className="px-0">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="pl-6">Medicine</TableHead>
                <TableHead>ID</TableHead>
                <TableHead className="text-right pr-6">
                  Usage
                </TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {top_usage.map((m: any) => (
                <TableRow key={m.medicine_id}>
                  <TableCell className="font-medium pl-6">{m.medicine_name}</TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {m.medicine_id}
                  </TableCell>
                  <TableCell className="text-right font-semibold pr-6">
                    {m.total_usage.toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* ALERTS */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold">Recent Alerts</CardTitle>
        </CardHeader>

        <CardContent>
          {recent_alerts.length === 0 ? (
            <p className="text-sm text-muted-foreground py-2">
              No active alerts
            </p>
          ) : (
            <div className="space-y-2">
              {recent_alerts.map((a: any) => (
                <div
                  key={a.alert_id}
                  className="rounded-md border bg-card p-3 text-sm"
                >
                  <p className="font-medium mb-0.5">{a.alert_type}</p>
                  <p className="text-muted-foreground text-xs">
                    {a.alert_message}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

    </div>
  )
}