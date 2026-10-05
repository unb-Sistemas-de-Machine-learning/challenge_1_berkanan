// Cliente de autenticação do app.
// Este é o único módulo que depende do SDK de auth. O resto do código usa
// apenas `authClient` e `AuthUser`, para que detalhes do provedor fiquem
// isolados num só lugar.
import { createClient } from "@lumi.new/sdk"
import type { User } from "@lumi.new/sdk"

export type AuthUser = User

export const authClient = createClient({
  projectId: "p496705692817887232",
  apiBaseUrl: "https://api.lumi.new",
  authOrigin: "https://auth.lumi.new",
})