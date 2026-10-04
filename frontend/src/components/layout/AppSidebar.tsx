import { useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { History, LogOut, Moon, Plus, Sun, Trash2, X } from "lucide-react"
import { useChat } from "@/providers/ChatProvider"
import { useAuth } from "@/providers/AuthProvider"
import { useTheme } from "@/providers/ThemeProvider"
import { useHealth } from "@/hooks/useHealth"
import { conversationGroupLabel } from "@/lib/utils"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"

type AppSidebarProps = {
  open: boolean
  onClose: () => void
}

export function AppSidebar({ open, onClose }: AppSidebarProps) {
  const { conversations, createConversation, deleteConversation } = useChat()
  const { session, signOut } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const online = useHealth()
  const navigate = useNavigate()
  const location = useLocation()

  const [pendingDelete, setPendingDelete] = useState<{ id: string; title: string } | null>(null)

  const grouped = conversations.reduce<Record<string, typeof conversations>>((acc, conversation) => {
    const label = conversationGroupLabel(conversation.updatedAt)
    acc[label] = [...(acc[label] || []), conversation]
    return acc
  }, {})

  const startNew = () => {
    const conversation = createConversation()
    navigate(`/chat/${conversation.id}`)
    onClose()
  }

  const requestDelete = (id: string, title: string) => {
    setPendingDelete({ id, title })
  }

  const confirmDelete = () => {
    if (!pendingDelete) return
    const { id } = pendingDelete
    deleteConversation(id)
    setPendingDelete(null)
    if (location.pathname === `/chat/${id}`) {
      navigate("/chat", { replace: true })
    }
  }

  return (
    <>
      {/* Backdrop mobile */}
      <div
        className={`fixed inset-0 z-30 bg-black/40 lg:hidden ${open ? "block" : "hidden"}`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-[18.5rem] flex-col overflow-hidden border-r border-[var(--line)] bg-[var(--surface)] transition-transform lg:static lg:h-full lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* ===== Cabeçalho (fixo no topo) ===== */}
        <div className="flex shrink-0 items-center justify-between px-4 py-4">
          <Link to="/chat" className="flex items-center gap-3" onClick={onClose}>
            <div>
              <p className="text-sm font-semibold tracking-[0.18em]">CHATBOT BERKANAN</p>
              <p className="text-xs text-[var(--faint)]">Verificação nutricional</p>
            </div>
          </Link>
          <button
            type="button"
            className="rounded-full p-2 lg:hidden"
            onClick={onClose}
            aria-label="Fechar menu"
          >
            <X size={18} />
          </button>
        </div>

        {/* ===== Botão novo chat (fixo) ===== */}
        <div className="shrink-0 px-3">
          <button
            type="button"
            onClick={startNew}
            className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-white"
          >
            <Plus size={16} />
            Novo chat
          </button>
        </div>

        {/* ===== Lista de conversas (rola) ===== */}
        <nav className="berkanan-scroll mt-4 min-h-0 flex-1 overflow-y-auto px-3 pb-4">
          {Object.entries(grouped).map(([label, items]) => (
            <div key={label} className="mb-4">
              <p className="px-2 pb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--faint)]">
                {label}
              </p>
              <div className="grid gap-1">
                {items.map((conversation) => {
                  const active = location.pathname === `/chat/${conversation.id}`
                  return (
                    <div key={conversation.id} className="group relative">
                      <Link
                        to={`/chat/${conversation.id}`}
                        onClick={onClose}
                        className={`block rounded-xl py-2 pl-3 pr-10 text-sm transition ${
                          active
                            ? "bg-[var(--accent-soft)] text-[var(--accent)]"
                            : "text-[var(--ink)] hover:bg-[var(--bg-accent)]"
                        }`}
                      >
                        <span className="line-clamp-2">{conversation.title}</span>
                      </Link>

                      <button
                        type="button"
                        onClick={() => requestDelete(conversation.id, conversation.title)}
                        className={`absolute right-1.5 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-[var(--faint)] transition hover:bg-rose-500/10 hover:text-rose-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-500/40 ${
                          active
                            ? "opacity-100"
                            : "opacity-100 lg:opacity-0 lg:group-hover:opacity-100 lg:focus-visible:opacity-100"
                        }`}
                        aria-label={`Apagar conversa: ${conversation.title}`}
                        title="Apagar conversa"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
          {conversations.length === 0 ? (
            <p className="px-2 text-sm text-[var(--muted)]">
              Suas verificações locais aparecerão aqui.
            </p>
          ) : null}
        </nav>

        {/* ===== Rodapé (fixo embaixo) ===== */}
        <div className="grid shrink-0 gap-3 border-t border-[var(--line)] p-4">
          <Link
            to="/history"
            onClick={onClose}
            className="inline-flex items-center gap-2 rounded-xl px-2 py-2 text-sm hover:bg-[var(--bg-accent)]"
          >
            <History size={16} />
            Histórico
          </Link>

          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex items-center gap-2 rounded-xl px-2 py-2 text-sm hover:bg-[var(--bg-accent)]"
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            {theme === "dark" ? "Tema claro" : "Tema escuro"}
          </button>

          <div className="flex items-center justify-between rounded-xl bg-[var(--bg-accent)] px-3 py-2 text-sm">
            <span>
              {online == null ? "Verificando sistema" : online ? "Sistema online" : "Sistema offline"}
            </span>
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                online ? "bg-teal-500" : online == null ? "bg-amber-400" : "bg-rose-500"
              }`}
            />
          </div>

          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{session?.name || "Visitante"}</p>
              <p className="truncate text-xs text-[var(--faint)]">{session?.email}</p>
            </div>
            <button
              type="button"
              onClick={() => {
                signOut()
                navigate("/login")
              }}
              className="rounded-full p-2 hover:bg-[var(--bg-accent)]"
              aria-label="Sair"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Modal de confirmação de exclusão */}
      <ConfirmDialog
        open={pendingDelete !== null}
        title="Apagar esta conversa?"
        description={
          pendingDelete
            ? `"${
                pendingDelete.title.length > 80
                  ? pendingDelete.title.slice(0, 77) + "..."
                  : pendingDelete.title
              }" será removida permanentemente deste navegador. Esta ação não pode ser desfeita.`
            : undefined
        }
        confirmLabel="Apagar"
        cancelLabel="Cancelar"
        tone="danger"
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </>
  )
}