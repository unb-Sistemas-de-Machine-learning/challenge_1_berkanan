import type { Conversation } from "@/types/chat"
import { storageGetJson, storageSetJson } from "@/lib/storage"

const KEY = "conversations"

export function loadConversations(): Conversation[] {
  const list = storageGetJson<Conversation[]>(KEY, [])
  if (!Array.isArray(list)) return []
  const interrupted = "A verificação foi interrompida. Envie novamente."
  let didSanitize = false
  const cleaned = list
    .filter((item) => item && typeof item.id === "string")
    .map((conv) => ({
      ...conv,
      messages: Array.isArray(conv.messages)
        ? conv.messages.map((m) => {
            if (!m.pending) return m
            didSanitize = true
            return {
              ...m,
              pending: false,
              error: interrupted,
              content: interrupted,
            }
          })
        : [],
    }))
    .sort((a, b) => String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")))
  if (didSanitize) storageSetJson(KEY, cleaned)
  return cleaned
}

export function saveConversations(conversations: Conversation[]): void {
  storageSetJson(KEY, conversations)
}

export function upsertConversation(list: Conversation[], next: Conversation): Conversation[] {
  const others = list.filter((item) => item.id !== next.id)
  return [next, ...others].sort((a, b) => String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")))
}
