import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"

export function useHealth() {
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false

    const check = async () => {
      const ok = await api.health()
      if (!cancelled) setOnline(ok)
    }

    void check()
    const timer = window.setInterval(() => {
      void check()
    }, 60000)

    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [])

  return online
}
