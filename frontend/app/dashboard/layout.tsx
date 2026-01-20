import Sidebar from "@/components/sidebar"
import Topbar from "@/components/topbar"
import {
  warehouseLinks,
  pharmacyLinks,
} from "@/components/nav-links"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // TEMP ROLE (replace later with auth)
  const role = "pharmacy"

  const links = (role === "warehouse") ? warehouseLinks : pharmacyLinks


  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar links={links} />

      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}