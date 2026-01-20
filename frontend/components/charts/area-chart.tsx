"use client"

import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

const data = [
  { date: "Jun 24", value: 120 },
  { date: "Jun 25", value: 80 },
  { date: "Jun 26", value: 160 },
  { date: "Jun 27", value: 220 },
  { date: "Jun 28", value: 140 },
  { date: "Jun 29", value: 90 },
  { date: "Jun 30", value: 180 },
]

export default function DashboardAreaChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Area
          type="monotone"
          dataKey="value"
          stroke="hsl(var(--primary))"
          fill="hsl(var(--primary))"
          fillOpacity={0.2}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}