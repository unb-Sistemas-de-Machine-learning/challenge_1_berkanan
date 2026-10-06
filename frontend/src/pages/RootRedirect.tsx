import { Navigate } from "react-router-dom"
import { useAuth } from "@/providers/AuthProvider"

export default function RootRedirect() {
  const { isAuthenticated } = useAuth()
  return <Navigate to={isAuthenticated ? "/chat" : "/login"} replace />
}
