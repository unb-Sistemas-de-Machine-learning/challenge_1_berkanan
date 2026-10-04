import { confidencePercent, formatConfidence } from "@/lib/classification"

export function ConfidenceIndicator({ score }: { score?: number | null }) {
  const percent = confidencePercent(score)

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-sm">
        <span className="font-medium">Confiança da classificação</span>
        <span className="tabular-nums text-[var(--muted)]">{formatConfidence(score)}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[var(--accent-soft)]" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent} aria-label="Confiança da classificação">
        <div className="h-full rounded-full bg-[var(--accent)] transition-all duration-500" style={{ width: `${percent}%` }} />
      </div>
      <p className="mt-2 text-xs leading-5 text-[var(--faint)]">
        Esta métrica indica a confiança do classificador nesta consulta, não uma certeza científica.
      </p>
    </div>
  )
}
