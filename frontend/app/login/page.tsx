"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowRight } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import LiquidEther from "@/components/background/liquid"
import RotatingText from "@/components/rotatingText"

export default function LoginPage() {
  const router = useRouter()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showLogin, setShowLogin] = useState(false)

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 relative overflow-hidden">

      {/* BACKGROUND */}
        <div className="absolute inset-0">
            <LiquidEther />
        </div>

      {/* LEFT PANEL */}
        <div className="relative z-10 flex flex-col justify-center px-16 text-white">
            <h1 className="absolute top-4 left-4 text-2xl font-bold">
                Aushadhi Inc.
            </h1>
            <p className="text-5xl font-semibold pb-1">Your Dashboard For</p>
            <div className="inline-flex">
                <RotatingText
                    texts={[
                    "Real-time inventory visibility",
                    "Predictive shortage & expiry alerts",
                    "Secure traceability & audit logs",
                    "Everything"
                    ]}
                    staggerDuration={0.05}
                    mainClassName="
                    py-1
                    text-5xl
                    font-semibold
                    text-white
                    "
                    splitBy="words"
                    staggerFrom="last"
                    initial={{ y: '100%', opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: '-120%', opacity: 0 }}
                    rotationInterval={3000}
                    transition={{ type: 'spring', damping: 30, stiffness: 200 }}
                    splitLevelClassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
                />
            </div>

            <p className="text-lg text-white max-w-xl py-5">
                Intelligent Drug Inventory & Supply Chain Management Platform
                ensuring transparency, availability and efficiency across
                healthcare institutions.
            </p>

            <p className="text-sm text-white">
                Designed for hospitals, warehouses and public health systems.
            </p>

            <div className="absolute bottom-5">
                <p>
                    BigBoyCoders • InnoHack VIT • PS32
                </p>
            </div>
        </div>

      {/* RIGHT PANEL */}
      <div className="relative z-10 flex items-center justify-center overflow-hidden">

        {/* MORPH BACKGROUND */}
        <motion.div
          layout
          initial={{
            width: 80,
            height: 80,
            borderRadius: 999,
            top: "50%",
            left: "50%",
            translateX: "-50%",
            translateY: "-50%",
            position: "absolute",
          }}
          animate={
            showLogin
              ? {
                  width: "100%",
                  height: "100%",
                  top: 0,
                  right: 0,
                  translateY: "0%",
                  borderRadius: 0,
                }
              : {}
          }
          transition={{
            duration: 0.5,
            ease: [0.4, 0, 0.2, 1],
          }}
          className="bg-emerald-800/80 shadow-xl"
        >
          {!showLogin && (
            <button
              onClick={() => setShowLogin(true)}
              className="absolute inset-0 flex items-center justify-center text-white hover:text-gray-800 transition-colors duration-200"
            >
              <ArrowRight size={35} />
            </button>
          )}
        </motion.div>

        {/* LOGIN FORM */}
        <AnimatePresence>
          {showLogin && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              className="relative z-20"
            >
              <Card className="w-95 shadow-2xl">
                <CardContent className="space-y-5 py-10">

                  <h2 className="text-2xl font-bold text-center text-emerald-700">
                    Welcome back
                  </h2>

                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input value={email} onChange={e => setEmail(e.target.value)} />
                  </div>

                  <div className="space-y-2">
                    <Label>Password</Label>
                    <Input
                      type="password"
                      value={password}
                      onChange={e => setPassword(e.target.value)}
                    />
                  </div>

                  <Button
                    className="w-full h-11 bg-emerald-800 hover:bg-emerald-950 transition-colors duration-200 ease-in-out"
                    onClick={() => router.push("/dashboard/warehouse")}
                  >
                    Login
                  </Button>

                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}