import { Navigate, Outlet } from "react-router-dom"
import { useAuth } from "@/providers/AuthProvider"

export function GuestRoute() {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to="/chat" replace />
  return <Outlet />
}
