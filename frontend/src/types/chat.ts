import type { AnalysisResponse } from "@/types/analysis"

export type MessageRole = "user" | "assistant"

export type Message = {
  id: string
  role: MessageRole
  content: string
  createdAt: string
  analysis?: AnalysisResponse
  error?: string
  pending?: boolean
}

export type Conversation = {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages: Message[]
}
