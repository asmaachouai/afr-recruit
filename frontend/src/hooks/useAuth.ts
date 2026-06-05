"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import api, { setAccessToken } from "@/lib/api"

export function useAuth() {
  const { user, isLoading, logout } = useAuthStore()
  return { user, isLoading, logout }
}

export function useRequireAuth(role?: "candidate" | "recruiter" | "admin") {
  const router = useRouter()
  const { user, isLoading, setUser, setLoading } = useAuthStore()

  useEffect(() => {
    const init = async () => {
      const refresh = localStorage.getItem("refresh_token")
      if (!refresh) { setLoading(false); router.push("/login"); return }
      try {
        const { data: tokens } = await api.post("/auth/refresh", { refresh_token: refresh })
        setAccessToken(tokens.access_token)
        const { data: me } = await api.get("/auth/me")
        setUser(me)
        if (role && me.role !== role && me.role !== "admin") router.push("/login")
      } catch {
        setLoading(false)
        router.push("/login")
      } finally {
        setLoading(false)
      }
    }
    if (!user) init()
    else setLoading(false)
  }, [])

  return { user, isLoading }
}