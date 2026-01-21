"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { getMe } from "@/app/apis/auth"

const AuthContext = createContext<any>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")

    if (!token) {
      setLoading(false)
      return
    }

    getMe()
      .then((user) => setUser(user))
      .catch(() => {
        localStorage.removeItem("access_token")
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)