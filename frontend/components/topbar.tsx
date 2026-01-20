"use client"

import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { LogOut } from "lucide-react"
import { useRouter } from "next/navigation"

export default function Topbar() {
  const router = useRouter()

  return (
    <header className="flex h-12 items-center justify-between border-b bg-background px-6 py-5">
      <div className="font-medium">
        Dashboard
      </div>

      <div className="flex items-center gap-4">
        <Avatar>
          <AvatarFallback>WH</AvatarFallback>
        </Avatar>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/login")}
        >
          <LogOut size={18} />
        </Button>
      </div>
    </header>
  )
}