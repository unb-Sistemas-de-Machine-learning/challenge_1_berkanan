import type { MatchedSource } from "@/types/analysis"
import { EvidenceCard } from "@/components/analysis/EvidenceCard"

export function EvidenceList({ sources }: { sources?: MatchedSource[] }) {
  const items = Array.isArray(sources) ? sources : []

  if (items.length === 0) {
    return (
      <p className="text-sm leading-6 text-[var(--muted)]">
        Nenhuma evidência correspondente foi devolvida para esta afirmação.
      </p>
    )
  }

  return (
    <div className="grid gap-3">
      {items.map((source, index) => (
        <EvidenceCard key={`${source.source || "source"}-${index}`} source={source} />
      ))}
    </div>
  )
}
