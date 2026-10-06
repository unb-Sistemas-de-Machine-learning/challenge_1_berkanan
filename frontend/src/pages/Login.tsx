import { FormEvent, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "@/providers/AuthProvider"

export default function Login() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [error, setError] = useState("")

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!name.trim() || !email.trim() || !email.includes("@")) {
      setError("Informe um nome e um e-mail válidos para continuar localmente.")
      return
    }
    signIn({ name, email })
    navigate("/chat", { replace: true })
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[var(--bg)]">
      <div className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-[var(--glow)] blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full bg-[var(--accent-soft)] blur-3xl" />
      <div className="mx-auto grid min-h-screen max-w-6xl items-center gap-10 px-6 py-12 lg:grid-cols-[1.1fr_0.9fr]">
        <section>
          <p className="mt-6 text-xs font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">BERKANAN</p>
          <h1 className="mt-3 max-w-xl text-4xl font-semibold tracking-tight sm:text-5xl">
            Verifique afirmações sobre diabetes com evidências, não com achismos.
          </h1>
          <p className="mt-4 max-w-lg text-sm leading-7 text-[var(--muted)]">
            Uma sessão local abre o espaço de verificação. Não há cadastro no servidor, senha real nem conta médica. O Berkanan não substitui nutricionista, endocrinologista ou prescrição.
          </p>
        </section>

        <section className="rounded-[32px] border border-[var(--line)] bg-[var(--surface)] p-6 shadow-[var(--shadow)] sm:p-8">
          <h2 className="text-xl font-semibold">Entrar no espaço de verificação</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
            Autenticação mock apenas neste navegador. Nenhum dado é enviado a um endpoint de login.
          </p>
          <form className="mt-6 grid gap-4" onSubmit={onSubmit}>
            <div>
              <label htmlFor="name" className="mb-1.5 block text-sm font-medium">
                Nome
              </label>
              <input
                id="name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="w-full rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] px-4 py-3 text-sm outline-none"
                autoComplete="name"
              />
            </div>
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] px-4 py-3 text-sm outline-none"
                autoComplete="email"
              />
            </div>
            {error ? (
              <p className="text-sm text-[color:var(--fake)]" role="alert">
                {error}
              </p>
            ) : null}
            <button type="submit" className="mt-2 rounded-full bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white">
              Continuar
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}
