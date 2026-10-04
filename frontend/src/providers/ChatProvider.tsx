import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react"
import type { Conversation, Message } from "@/types/chat"
import { api, ApiError } from "@/lib/api-client"
import { loadConversations, saveConversations, upsertConversation } from "@/lib/conversations"
import { createId, nowIso, titleFromClaim } from "@/lib/utils"
import { validateClaim } from "@/lib/validation"

type ChatContextValue = {
  conversations: Conversation[]
  getConversation: (id?: string) => Conversation | undefined
  createConversation: (id?: string) => Conversation
  deleteConversation: (id: string) => void
  sendClaim: (conversationId: string, text: string) => Promise<void>
}

const ChatContext = createContext<ChatContextValue | null>(null)

function emptyConversation(id?: string): Conversation {
  const stamp = nowIso()
  return {
    id: id || createId(),
    title: "Nova verificação",
    createdAt: stamp,
    updatedAt: stamp,
    messages: [],
  }
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>(() => loadConversations())

  const persistUpdate = useCallback((updater: (prev: Conversation[]) => Conversation[]) => {
    setConversations((prev) => {
      const next = updater(prev)
      saveConversations(next)
      return next
    })
  }, [])

  const getConversation = useCallback(
    (id?: string) => conversations.find((item) => item.id === id),
    [conversations],
  )

  const createConversation = useCallback(
    (id?: string) => {
      const conversation = emptyConversation(id)
      persistUpdate((prev) => {
        if (id && prev.some((item) => item.id === id)) {
          return prev
        }
        return upsertConversation(prev, conversation)
      })
      return conversation
    },
    [persistUpdate],
  )

  const deleteConversation = useCallback(
    (id: string) => {
      persistUpdate((prev) => prev.filter((item) => item.id !== id))
    },
    [persistUpdate],
  )

  const sendClaim = useCallback(
    async (conversationId: string, text: string) => {
      const validation = validateClaim(text)
      if (!validation.ok) {
        throw new ApiError(validation.message, { code: "invalid" })
      }

      const userMessage: Message = {
        id: createId(),
        role: "user",
        content: validation.value,
        createdAt: nowIso(),
      }
      const pendingMessage: Message = {
        id: createId(),
        role: "assistant",
        content: "Analisando sua afirmação...",
        createdAt: nowIso(),
        pending: true,
      }

      persistUpdate((prev) => {
        const current =
          prev.find((item) => item.id === conversationId) || emptyConversation(conversationId)
        const withPending: Conversation = {
          ...current,
          title: current.messages.length === 0 ? titleFromClaim(validation.value) : current.title,
          updatedAt: nowIso(),
          messages: [...current.messages, userMessage, pendingMessage],
        }
        return upsertConversation(
          prev.filter((item) => item.id !== conversationId),
          withPending,
        )
      })

      try {
        const analysis = await api.analyzeClaim(validation.value)

        // A bolha do assistente NÃO duplica o texto do AnalysisResult.
        // Só usamos `answer` (curto). Se não houver, content fica vazio
        // e o card do AnalysisResult é a única coisa exibida.
        const assistantMessage: Message = {
          id: pendingMessage.id,
          role: "assistant",
          content: analysis.answer ?? "",
          createdAt: nowIso(),
          analysis,
        }

        persistUpdate((prev) => {
          const latest = prev.find((item) => item.id === conversationId)
          if (!latest) return prev
          return upsertConversation(prev, {
            ...latest,
            updatedAt: nowIso(),
            messages: latest.messages.map((message) =>
              message.id === pendingMessage.id ? assistantMessage : message,
            ),
          })
        })
      } catch (error) {
        const message =
          error instanceof ApiError ? error.message : "Não foi possível conectar ao Berkanan."
        persistUpdate((prev) => {
          const latest = prev.find((item) => item.id === conversationId)
          if (!latest) return prev
          return upsertConversation(prev, {
            ...latest,
            updatedAt: nowIso(),
            messages: latest.messages.map((item) =>
              item.id === pendingMessage.id
                ? {
                    ...item,
                    pending: false,
                    error: message,
                    content: message,
                  }
                : item,
            ),
          })
        })
      }
    },
    [persistUpdate],
  )

  const value = useMemo(
    () => ({
      conversations,
      getConversation,
      createConversation,
      deleteConversation,
      sendClaim,
    }),
    [conversations, createConversation, deleteConversation, getConversation, sendClaim],
  )

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error("useChat deve ser usado dentro de ChatProvider")
  }
  return context
}