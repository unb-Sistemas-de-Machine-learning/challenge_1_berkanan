import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import type { AnalysisResponse } from "@/types/analysis"
import { api } from "@/lib/api-client"
import { formatDateTime } from "@/lib/utils"
import { ClassificationBadge } from "@/components/analysis/ClassificationBadge"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { useChat } from "@/providers/ChatProvider"

export default function History() {
  const { conversations } = useChat()
  const [remote, setRemote] = useState<AnalysisResponse[]>([])
  const [remoteError, setRemoteError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const items = await api.getHistory()
        if (!cancelled) {
          setRemote(items)
          setRemoteError("")
        }
      } catch {
        if (!cancelled) {
          setRemoteError("As análises recentes sincronizadas estão indisponíveis no momento. O histórico local foi preservado.")
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="berkanan-scroll flex-1 overflow-y-auto px-4 py-6 sm:px-8">
      <div className="mx-auto grid max-w-5xl gap-8">
        <header>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">Memória</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Histórico</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">
            Conversas ficam neste navegador. As análises recentes sincronizadas vêm do backend e não pertencem a uma conta.
          </p>
        </header>

        <section className="grid gap-3">
          <h2 className="text-lg font-semibold">Conversas locais</h2>
          {conversations.length === 0 ? (
            <EmptyState
              title="Nenhuma conversa ainda"
              description="As verificações feitas neste navegador aparecerão aqui, separadas das análises sincronizadas."
            />
          ) : (
            <div className="grid gap-3">
              {conversations.map((conversation) => (
                <Link
                  key={conversation.id}
                  to={`/chat/${conversation.id}`}
                  className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] px-4 py-4 shadow-[var(--shadow)]"
                >
                  <p className="font-medium">{conversation.title}</p>
                  <p className="mt-1 text-xs text-[var(--faint)]">{formatDateTime(conversation.updatedAt)}</p>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="grid gap-3">
          <h2 className="text-lg font-semibold">Análises recentes sincronizadas</h2>
          {loading ? <p className="text-sm text-[var(--muted)]">Carregando análises recentes...</p> : null}
          {remoteError ? <ErrorState title="Histórico remoto indisponível" message={remoteError} /> : null}
          {!loading && !remoteError && remote.length === 0 ? (
            <EmptyState
              title="Nenhuma análise sincronizada"
              description="O backend ainda não devolveu análises recentes."
            />
          ) : null}
          <div className="grid gap-3">
            {remote.map((item, index) => (
              <article key={item.id || `${item.input_text}-${index}`} className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] px-4 py-4">
                <div className="flex flex-wrap items-center gap-3">
                  <ClassificationBadge classification={item.classification} />
                  <span className="text-xs text-[var(--faint)]">{formatDateTime(item.timestamp)}</span>
                </div>
                <p className="mt-3 text-sm leading-6">{item.input_text || "Afirmação não informada"}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
