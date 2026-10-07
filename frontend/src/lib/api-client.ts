import type { AnalysisResponse, MatchedSource } from "@/types/analysis"

// Empty in development so fetch uses relative paths (/api/*, /health) via Vite proxy.
// Production: set VITE_API_URL to the public API origin, OR put frontend and backend
// behind the same domain.
const DEFAULT_API_URL = ""
const ANALYZE_TIMEOUT_MS = 180000
const DEFAULT_TIMEOUT_MS = 80000

export class ApiError extends Error {
  status?: number
  code: "network" | "timeout" | "http" | "invalid" | "offline"

  constructor(message: string, options?: { status?: number; code?: ApiError["code"] }) {
    super(message)
    this.name = "ApiError"
    this.status = options?.status
    this.code = options?.code || "http"
  }
}

function getApiBaseUrl(): string {
  const fromVite = import.meta.env.VITE_API_URL
  const fromPublic = import.meta.env.NEXT_PUBLIC_API_URL
  const raw = String(fromVite || fromPublic || DEFAULT_API_URL).trim()
  return raw.replace(/\/+$/, "")
}

async function parseJson(response: Response): Promise<unknown> {
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    throw new ApiError("A resposta do Berkanan veio em um formato inesperado.", {
      status: response.status,
      code: "invalid",
    })
  }
}

function messageForStatus(status: number): string {
  if (status === 422) return "A afirmação enviada não pôde ser processada. Revise o texto e tente novamente."
  if (status === 500) return "O Berkanan encontrou um erro interno ao analisar esta afirmação."
  if (status >= 500) return "O serviço de análise está indisponível no momento."
  if (status === 404) return "O endpoint solicitado não foi encontrado no Berkanan."
  return "Não foi possível concluir a verificação agora."
}

async function request<T>(
  path: string,
  options: RequestInit & { timeoutMs?: number } = {},
): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, ...init } = options
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...(init.headers || {}),
      },
    })

    if (!response.ok) {
      throw new ApiError(messageForStatus(response.status), {
        status: response.status,
        code: "http",
      })
    }

    return (await parseJson(response)) as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("A verificação demorou demais para responder.", { code: "timeout" })
    }
    throw new ApiError("Não foi possível conectar ao Berkanan.", { code: "network" })
  } finally {
    window.clearTimeout(timer)
  }
}

function asNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return value
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value)
    if (Number.isFinite(parsed)) return parsed
  }
  return 0
}

function asString(value: unknown, fallback = ""): string {
  if (typeof value === "string") return value
  if (value == null) return fallback
  return String(value)
}

function normalizeSource(raw: unknown): MatchedSource {
  if (!raw || typeof raw !== "object") {
    return { text: asString(raw), source: "Fonte não identificada", similarity: 0 }
  }
  const item = raw as Record<string, unknown>
  return {
    ...item,
    text: asString(item.text ?? item.excerpt ?? item.snippet),
    source: asString(item.source ?? item.source_title ?? item.title, "Fonte não identificada"),
    similarity: asNumber(item.similarity ?? item.score),
    source_url: asString(item.source_url ?? item.url),
    source_title: asString(item.source_title ?? item.title),
    source_date: asString(item.source_date),
  }
}

export function normalizeAnalysis(raw: unknown): AnalysisResponse {
  const data = raw && typeof raw === "object" ? (raw as Record<string, unknown>) : {}
  const sourcesRaw = data.matched_sources
  const matched_sources = Array.isArray(sourcesRaw) ? sourcesRaw.map(normalizeSource) : []

  // /api/analyze → timestamp ; /api/history → analysis_date
  const timestampValue =
    data.timestamp != null ? data.timestamp
    : data.analysis_date != null ? data.analysis_date
    : null

  // O backend ora manda model_version, ora llm_model.
  const modelValue =
    data.model_version != null ? data.model_version
    : data.llm_model != null ? data.llm_model
    : "não informado"

  // O backend pode mandar explanation OU llm_explanation OU nenhum dos dois (null).
  const explanationValue =
    typeof data.explanation === "string" && data.explanation.trim()
      ? data.explanation
      : typeof data.llm_explanation === "string" && data.llm_explanation.trim()
        ? data.llm_explanation
        : undefined

  return {
    ...data,
    id: data.id == null ? null : asString(data.id),
    input_text: asString(data.input_text ?? data.text),
    classification: asString(data.classification, "UNKNOWN"),
    confidence_score: asNumber(data.confidence_score),
    matched_sources,
    model_version: asString(modelValue, "não informado"),
    timestamp: timestampValue == null ? null : asString(timestampValue),
    explanation: explanationValue,
    answer: typeof data.answer === "string" && data.answer.trim() ? data.answer : undefined,
  }
}

function extractHistoryList(raw: unknown): unknown[] {
  if (Array.isArray(raw)) return raw
  if (raw && typeof raw === "object") {
    const data = raw as Record<string, unknown>
    if (Array.isArray(data.items)) return data.items
    if (Array.isArray(data.results)) return data.results
    if (Array.isArray(data.history)) return data.history
    if (Array.isArray(data.analyses)) return data.analyses
  }
  return []
}

export const api = {
  getBaseUrl: getApiBaseUrl,

  async health(): Promise<boolean> {
    try {
      await request("/api/health", { method: "GET", timeoutMs: 4000 })
      return true
    } catch (err) {
      console.warn("[health] /api/health falhou:", err)
      try {
        await request("/health", { method: "GET", timeoutMs: 4000 })
        return true
      } catch (err2) {
        console.warn("[health] /health falhou:", err2)
        return false
      }
    }
  },

  async analyzeClaim(text: string): Promise<AnalysisResponse> {
    const payload = await request<unknown>("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
      timeoutMs: ANALYZE_TIMEOUT_MS,
    })
    return normalizeAnalysis(payload)
  },

  async getHistory(): Promise<AnalysisResponse[]> {
    const payload = await request<unknown>("/api/history", {
      method: "GET",
      timeoutMs: 8000,
    })
    return extractHistoryList(payload).map(normalizeAnalysis)
  },
}