export type MatchedSource = {
  text?: string
  source?: string
  similarity?: number
  source_url?: string
  source_title?: string
  source_date?: string
  [key: string]: unknown
}

export type AnalysisResponse = {
  id: string | null
  input_text: string
  classification: string
  confidence_score: number
  matched_sources: MatchedSource[]
  model_version: string
  timestamp: string | null
  explanation?: string
  answer?: string
  alert?: string
  context?: string
  follow_up_question?: string
  [key: string]: unknown
}

export type ClassificationTone = "real" | "fake" | "partial" | "inconclusive" | "unknown"

export type ClassificationPresentation = {
  key: string
  label: string
  tone: ClassificationTone
  hint: string
}
