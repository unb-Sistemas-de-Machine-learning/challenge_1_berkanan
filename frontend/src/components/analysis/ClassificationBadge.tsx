import { AlertTriangle, CheckCircle2, HelpCircle, MinusCircle } from "lucide-react"
import { getClassificationPresentation } from "@/lib/classification"
import type { ClassificationTone } from "@/types/analysis"

type IconComponent = typeof AlertTriangle

const ICONS: Record<ClassificationTone, IconComponent> = {
  real: CheckCircle2,
  fake: AlertTriangle,
  partial: MinusCircle,
  inconclusive: HelpCircle,
  unknown: HelpCircle,
}

export function ClassificationBadge({ classification }: { classification: string }) {
  const { label, tone } = getClassificationPresentation(classification)
  const Icon = ICONS[tone] ?? HelpCircle

  return (
    <span
      className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold leading-none"
      style={{
        color: `var(--${tone})`,
        backgroundColor: `var(--${tone}-bg)`,
      }}
    >
      <Icon size={18} strokeWidth={2.4} aria-hidden="true" />
      <span>{label}</span>
    </span>
  )
}