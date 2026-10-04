export type LocalSession = {
  name: string
  email: string
  signedInAt: string
}

export type AuthContextValue = {
  session: LocalSession | null
  isAuthenticated: boolean
  signIn: (input: { name: string; email: string }) => void
  signOut: () => void
}
