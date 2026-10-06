import type { RouteObject } from "react-router-dom"
import { useRoutes } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { GuestRoute } from "@/components/layout/GuestRoute"
import { ProtectedRoute } from "@/components/layout/ProtectedRoute"
import Chat from "@/pages/Chat"
import History from "@/pages/History"
import Login from "@/pages/Login"
import RootRedirect from "@/pages/RootRedirect"
import { AuthProvider } from "@/providers/AuthProvider"
import { ChatProvider } from "@/providers/ChatProvider"
import { ThemeProvider } from "@/providers/ThemeProvider"

export const routes: RouteObject[] = [
  { path: "/", element: <RootRedirect /> },
  {
    element: <GuestRoute />,
    children: [{ path: "/login", element: <Login /> }],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/chat", element: <Chat /> },
          { path: "/chat/:id", element: <Chat /> },
          { path: "/history", element: <History /> },
        ],
      },
    ],
  },
]

function AppRoutes() {
  return useRoutes(routes)
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ChatProvider>
          <AppRoutes />
        </ChatProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
