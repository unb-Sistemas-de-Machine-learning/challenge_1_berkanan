export function createId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  return `bk_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

export function nowIso(): string {
  return new Date().toISOString()
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

export function truncate(value: string, max = 72): string {
  const text = value.trim()
  if (text.length <= max) return text
  return `${text.slice(0, max - 1).trim()}…`
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "—"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return "—"
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date)
}

export function startOfDay(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime()
}

export function conversationGroupLabel(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return "Anteriores"
  const today = startOfDay(new Date())
  const target = startOfDay(date)
  const dayMs = 24 * 60 * 60 * 1000
  if (target === today) return "Hoje"
  if (target === today - dayMs) return "Ontem"
  if (target > today - 7 * dayMs) return "Esta semana"
  return "Anteriores"
}

export function titleFromClaim(text: string): string {
  const clean = text.replace(/\s+/g, " ").trim()
  if (!clean) return "Nova verificação"
  return truncate(clean, 48)
}
