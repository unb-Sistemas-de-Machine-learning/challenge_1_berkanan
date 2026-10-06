import { useMemo, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { ChatEmptyState } from "@/components/chat/ChatEmptyState"
import { ClaimInput } from "@/components/chat/ClaimInput"
import { MessageBubble } from "@/components/chat/MessageBubble"
import { useChat } from "@/providers/ChatProvider"

export default function Chat() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { getConversation, createConversation, sendClaim } = useChat()
  const conversation = getConversation(id)
  const [sending, setSending] = useState(false)

  const title = conversation?.title || "Nova verificação"
  const messages = conversation?.messages || []
  const busy = sending || messages.some((message) => message.pending)

  const ensureConversationId = () => {
    if (conversation?.id) return conversation.id
    const created = createConversation()
    navigate(`/chat/${created.id}`, { replace: true })
    return created.id
  }

  const handleSubmit = async (text: string) => {
    const conversationId = ensureConversationId()
    setSending(true)
    try {
      await sendClaim(conversationId, text)
    } catch (error) {
      console.error("[chat] falha ao enviar afirmação:", error)
    } finally {
      setSending(false)
    }
  }

  const headerMeta = useMemo(() => {
    if (!conversation) return "Comece com uma afirmação sobre alimentação e diabetes."
    return "Conversa local neste navegador. A análise é enviada apenas como texto."
  }, [conversation])

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {/* Cabeçalho — alinhado com o conteúdo central */}
      <div className="border-b border-[var(--line)] bg-[var(--surface)] px-4 py-3 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <h1 className="truncate text-base font-semibold">{title}</h1>
          <p className="text-xs text-[var(--faint)]">{headerMeta}</p>
        </div>
      </div>

      {/* Mensagens — mesmo max-w e padding do input */}
      <div className="berkanan-scroll min-h-0 flex-1 overflow-y-auto px-4 sm:px-6">
        {messages.length === 0 ? (
          <ChatEmptyState onExample={(text) => void handleSubmit(text)} />
        ) : (
          <div className="mx-auto max-w-3xl py-6">
            <div className="grid gap-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <ClaimInput disabled={busy} onSubmit={handleSubmit} />
    </div>
  )
}