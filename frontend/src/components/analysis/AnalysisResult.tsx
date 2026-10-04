import type { AnalysisResponse } from "@/types/analysis"
import { getClassificationPresentation } from "@/lib/classification"
import { AnalysisMetadata } from "@/components/analysis/AnalysisMetadata"
import { ClassificationBadge } from "@/components/analysis/ClassificationBadge"
import { ConfidenceIndicator } from "@/components/analysis/ConfidenceIndicator"
import { EvidenceList } from "@/components/analysis/EvidenceList"
import { Markdown } from "@/components/ui/Markdown"

export function AnalysisResult({ analysis }: { analysis: AnalysisResponse }) {
  const presentation = getClassificationPresentation(analysis.classification)
  const explanation = typeof analysis.explanation === "string" ? analysis.explanation.trim() : ""

  return (
    <section className="overflow-hidden rounded-[28px] border border-[var(--line)] bg-[var(--surface)] shadow-[var(--shadow)]">
      <div className="border-b border-[var(--line)] px-5 py-4 sm:px-6">
        <div className="flex flex-wrap items-center gap-3">
          <ClassificationBadge classification={analysis.classification} />
          <p className="text-sm text-[var(--muted)]">{presentation.hint}</p>
        </div>
      </div>
      <div className="grid gap-6 px-5 py-5 sm:px-6">
        <ConfidenceIndicator score={analysis.confidence_score} />
        <div>
          <h3 className="text-sm font-semibold">Por que essa classificação?</h3>
          {explanation ? (
            <Markdown className="mt-2">{explanation}</Markdown>
          ) : (
            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
              O Berkanan classifica a afirmação a partir das evidências recuperadas abaixo. Nenhuma explicação textual adicional foi devolvida por esta análise.
            </p>
          )}
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold">Evidências recuperadas</h3>
          <EvidenceList sources={analysis.matched_sources} />
        </div>
        <AnalysisMetadata analysis={analysis} />
      </div>
    </section>
  )
}
