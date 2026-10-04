import type { AnalysisResponse } from "@/types/analysis"
import { formatDateTime } from "@/lib/utils"

export function AnalysisMetadata({ analysis }: { analysis: AnalysisResponse }) {
  return (
    <dl className="grid gap-2 text-xs text-[var(--faint)] sm:grid-cols-3">
      <div>
        <dt className="uppercase tracking-[0.16em]">Modelo</dt>
        <dd className="mt-1 text-[var(--muted)]">{analysis.model_version || "não informado"}</dd>
      </div>
      <div>
        <dt className="uppercase tracking-[0.16em]">Data</dt>
        <dd className="mt-1 text-[var(--muted)]">{formatDateTime(analysis.timestamp)}</dd>
      </div>
      <div>
        <dt className="uppercase tracking-[0.16em]">ID</dt>
        <dd className="mt-1 truncate text-[var(--muted)]" title={analysis.id || undefined}>
          {analysis.id || "não persistido"}
        </dd>
      </div>
    </dl>
  )
}
