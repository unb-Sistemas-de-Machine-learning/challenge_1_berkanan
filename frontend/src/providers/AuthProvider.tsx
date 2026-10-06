import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import type { AuthContextValue, LocalSession } from "@/types/auth"
import { nowIso } from "@/lib/utils"
import { storageGetJson, storageRemove, storageSetJson } from "@/lib/storage"

const AuthContext = createContext<AuthContextValue | null>(null)
const SESSION_KEY = "session"

function loadSession(): LocalSession | null {
  const session = storageGetJson<LocalSession | null>(SESSION_KEY, null)
  if (!session?.email || !session?.name) return null
  return session
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<LocalSession | null>(loadSession)

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      isAuthenticated: Boolean(session),
      signIn: ({ name, email }) => {
        const next: LocalSession = {
          name: name.trim() || "Visitante",
          email: email.trim().toLowerCase(),
          signedInAt: nowIso(),
        }
        storageSetJson(SESSION_KEY, next)
        setSession(next)
      },
      signOut: () => {
        storageRemove(SESSION_KEY)
        setSession(null)
      },
    }),
    [session],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider")
  }
  return context
}
