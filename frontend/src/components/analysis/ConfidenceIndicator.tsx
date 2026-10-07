import { confidencePercent, formatConfidence } from "@/lib/classification"

export function ConfidenceIndicator({ score }: { score?: number | null }) {
  const percent = confidencePercent(score)
  const classification = typeof score === "number" && Number.isFinite(score)
    ? score >= 0.5 ? "Falso" : "Verdadeiro"
    : "—"

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-sm">
        <span className="font-medium">Probabilidade de a afirmação ser falsa</span>
        <span className="tabular-nums text-[var(--muted)]">
          {formatConfidence(score)} · Resultado: {classification}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[var(--accent-soft)]" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent} aria-label="Probabilidade de a afirmação ser falsa">
        <div className="h-full rounded-full bg-[var(--accent)] transition-all duration-500" style={{ width: `${percent}%` }} />
      </div>
      <p className="mt-2 text-xs leading-5 text-[var(--faint)]">
        Na checagem, 50% ou mais indica Falso; abaixo de 50% indica Verdadeiro. O resultado é estimado a partir das evidências recuperadas.
      </p>
    </div>
  )
}
