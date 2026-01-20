import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown } from "lucide-react"

type Props = {
  title: string
  value: string
  change: string
  positive?: boolean
  subtitle: string
}

export default function StatsCard({
  title,
  value,
  change,
  positive = true,
  subtitle,
}: Props) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <p className="text-sm font-medium text-muted-foreground">
          {title}
        </p>

        <Badge variant="outline" className="gap-1">
          {positive ? (
            <TrendingUp className="h-3 w-3" />
          ) : (
            <TrendingDown className="h-3 w-3" />
          )}
          {change}
        </Badge>
      </CardHeader>

      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground mt-1">
          {subtitle}
        </p>
      </CardContent>
    </Card>
  )
}