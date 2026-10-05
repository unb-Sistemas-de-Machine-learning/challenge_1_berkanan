import { useEffect, useState } from "react"
import { authClient, type AuthUser } from "@/lib/auth-client"

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(authClient.auth.isAuthenticated)
  const [user, setUser] = useState<AuthUser | null>(authClient.auth.user)

  useEffect(() => {
    const unsubscribe = authClient.auth.onAuthChange(({ isAuthenticated, user }) => {
      setIsAuthenticated(isAuthenticated)
      setUser(user)
    })
    return () => unsubscribe()
  }, [])

  return {
    user,
    isAuthenticated,
    isAdmin: user?.userRole === "ADMIN",
  }
}