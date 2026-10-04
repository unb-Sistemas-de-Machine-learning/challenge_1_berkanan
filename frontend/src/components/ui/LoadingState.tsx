import { motion } from "framer-motion"

type LoadingStateProps = {
  message?: string
}

export function LoadingState({ message = "Analisando sua afirmação..." }: LoadingStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="inline-flex items-center gap-3 self-start rounded-[24px] rounded-bl-md border border-[var(--line)] bg-[var(--surface)] px-4 py-3"
      role="status"
      aria-live="polite"
    >
      {/* Bolinha com "ping" — a mesma linguagem visual do status online da sidebar */}
      <span className="relative flex h-2.5 w-2.5 shrink-0" aria-hidden="true">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--accent)] opacity-50" />
        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[var(--accent)]" />
      </span>

      <span className="text-sm text-[var(--muted)]">{message}</span>
    </motion.div>
  )
}