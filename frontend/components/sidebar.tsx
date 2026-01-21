"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

import {
  LayoutDashboard,
  Boxes,
  LineChart,
  Activity,
  Truck,
  ClipboardList,
  Upload,
} from "lucide-react"

/* ----------------------------------
   ICON REGISTRY
----------------------------------- */

const iconMap: Record<string, React.ElementType> = {
  dashboard: LayoutDashboard,
  boxes: Boxes,
  chart: LineChart,
  activity: Activity,
  truck: Truck,
  clipboard: ClipboardList,
  upload: Upload,
}

/* ----------------------------------
   TYPES
----------------------------------- */

type NavLink = {
  title: string
  href: string
  icon: string
}

export default function Sidebar({
  links,
}: {
  links: NavLink[]
}) {
  const pathname = usePathname()

  return (
    <aside className="hidden md:flex min-h-screen w-64 flex-col border-r bg-muted/40">
      {/* LOGO */}
      <div className="px-6 py-3 h-12 border-b">
        Aushadi Inc.
      </div>

      {/* NAV LINKS */}
      <nav className="flex-1 space-y-1 p-3">
        {links.map((link) => {
          const Icon = iconMap[link.icon]
          const active = pathname === link.href

          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-light transition-colors",
                active
                  ? "bg-primary text-white"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              {Icon && <Icon className="h-4 w-4" />}
              {link.title}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}