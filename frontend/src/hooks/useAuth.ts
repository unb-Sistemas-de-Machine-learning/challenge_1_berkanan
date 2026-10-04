import type { User } from '@lumi.new/sdk'
import { lumi } from '@/lib/lumi'
import { useEffect, useState } from 'react'

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(lumi.auth.isAuthenticated)
  const [user, setUser] = useState<User | null>(lumi.auth.user)

  useEffect(() => {
    const unsubscribe = lumi.auth.onAuthChange(({ isAuthenticated, user }) => {
      setIsAuthenticated(isAuthenticated)
      setUser(user)
    })
    return () => unsubscribe()
  }, [])

  return {
    user,
    isAuthenticated,
    isAdmin: user?.userRole === 'ADMIN',
  }
}
