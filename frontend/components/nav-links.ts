// components/nav-links.ts

export type NavLink = {
  title: string
  href: string
  icon: string
}

/* ================================
   WAREHOUSE NAVIGATION
================================ */

export const warehouseLinks: NavLink[] = [
  {
    title: "Overview",
    href: "/dashboard/warehouse",
    icon: "dashboard",
  },
  {
    title: "Inventory",
    href: "/dashboard/warehouse/inventory",
    icon: "boxes",
  },
  {
    title: "Analytics",
    href: "/dashboard/warehouse/analytics",
    icon: "chart",
  },
  {
    title: "Optimization",
    href: "/dashboard/warehouse/optimization",
    icon: "activity",
  },
  {
    title: "Distribution",
    href: "/dashboard/warehouse/distribution",
    icon: "truck",
  },
]

/* ================================
   PHARMACY NAVIGATION
   (for later use)
================================ */

export const pharmacyLinks: NavLink[] = [
  {
    title: "Overview",
    href: "/dashboard/pharmacy",
    icon: "dashboard",
  },
  {
    title: "Inventory",
    href: "/dashboard/pharmacy/inventory",
    icon: "boxes",
  },
  {
    title: "Consumption",
    href: "/dashboard/pharmacy/consumption",
    icon: "chart",
  },
  {
    title: "Requests",
    href: "/dashboard/pharmacy/requests",
    icon: "clipboard",
  },
  {
    title: "Tracking",
    href: "/dashboard/pharmacy/tracking",
    icon: "truck",
  },
  {
    title: "Upload",
    href: "/dashboard/pharmacy/upload",
    icon: "upload",
  }
]