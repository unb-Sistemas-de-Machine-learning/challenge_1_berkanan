import type { ClassificationPresentation } from "@/types/analysis"
import { clamp } from "@/lib/utils"

export function getClassificationPresentation(classification?: string | null): ClassificationPresentation {
  const key = String(classification || "").trim().toUpperCase()

  if (key === "REAL") {
    return {
      key,
      label: "Verdadeiro",
      tone: "real",
      hint: "A afirmação se alinha às evidências recuperadas.",
    }
  }

  if (key === "FAKE") {
    return {
      key,
      label: "Falso",
      tone: "fake",
      hint: "A afirmação entra em conflito com as evidências recuperadas.",
    }
  }

  if (key === "INCONCLUSIVE") {
    return {
      key,
      label: "Sem evidência suficiente",
      tone: "inconclusive",
      hint: "As fontes recuperadas não sustentam uma classificação mais precisa.",
    }
  }

  if (key === "PARTIALLY_TRUE") {
    return {
      key,
      label: "Parcialmente verdadeiro",
      tone: "partial",
      hint: "Parte da afirmação pode ser compatível com evidências, mas não o conjunto.",
    }
  }

  return {
    key: key || "UNKNOWN",
    label: "Resultado da análise",
    tone: "unknown",
    hint: "A classificação recebida ainda não possui um rótulo específico.",
  }
}

export function formatConfidence(score?: number | null): string {
  if (typeof score !== "number" || !Number.isFinite(score)) return "—"
  const percent = Math.round(clamp(score, 0, 1) * 100)
  return `${percent}%`
}

export function confidencePercent(score?: number | null): number {
  if (typeof score !== "number" || !Number.isFinite(score)) return 0
  return Math.round(clamp(score, 0, 1) * 100)
}
