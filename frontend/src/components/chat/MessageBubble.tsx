import { motion } from "framer-motion"
import type { Message } from "@/types/chat"
import { AnalysisResult } from "@/components/analysis/AnalysisResult"
import { ErrorState } from "@/components/ui/ErrorState"
import { LoadingState } from "@/components/ui/LoadingState"

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-end"
      >
        <div className="max-w-[85%] rounded-[24px] rounded-br-md bg-[var(--accent)] px-4 py-3 text-sm leading-6 text-white">
          {message.content}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex w-full flex-col gap-3"
    >
      {message.pending ? <LoadingState /> : null}
      {message.error ? <ErrorState message={message.error} /> : null}

      {!message.pending && !message.error && message.content ? (
        <div className="rounded-[24px] rounded-bl-md border border-[var(--line)] bg-[var(--surface)] px-4 py-3 text-sm leading-6 text-[var(--ink)]">
          {message.content}
        </div>
      ) : null}

      {message.analysis ? <AnalysisResult analysis={message.analysis} /> : null}
    </motion.div>
  )
}