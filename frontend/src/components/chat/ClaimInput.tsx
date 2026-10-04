import { useState, type KeyboardEvent } from "react"
import {ArrowUp} from 'lucide-react'
import { validateClaim } from "@/lib/validation"

type ClaimInputProps = {
  disabled?: boolean
  onSubmit: (text: string) => Promise<void> | void
}

export function ClaimInput({ disabled, onSubmit }: ClaimInputProps) {
  const [value, setValue] = useState("")
  const [error, setError] = useState("")

  const submit = async () => {
    const validation = validateClaim(value)
    if (!validation.ok) {
      setError(validation.message)
      return
    }
    setError("")
    await onSubmit(validation.value)
    setValue("")
  }

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      if (!disabled) void submit()
    }
  }

  return (
    <div className="border-t border-[var(--line)] bg-[var(--surface)]/90 p-3 backdrop-blur sm:p-4">
      <label htmlFor="claim-input" className="sr-only">
        Afirmação sobre diabetes, alimentação ou nutrição
      </label>
      <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-[28px] border border-[var(--line)] bg-[var(--surface-2)] p-2 shadow-[var(--shadow)]">
        <textarea
          id="claim-input"
          rows={2}
          value={value}
          disabled={disabled}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Digite uma afirmação sobre diabetes, alimentação ou nutrição..."
          className="min-h-[52px] w-full resize-none bg-transparent px-3 py-3 text-sm leading-6 outline-none placeholder:text-[var(--faint)]"
        />
        <button
          type="button"
          onClick={() => void submit()}
          disabled={disabled}
          className="mb-1 inline-flex h-11 min-w-[44px] items-center justify-center gap-2 rounded-full bg-[var(--accent)] px-4 text-sm font-semibold text-white disabled:opacity-50"
          aria-label="Verificar"
        >
          <ArrowUp size={16} />
          <span className="hidden sm:inline">Verificar</span>
        </button>
      </div>
      {error ? (
        <p className="mx-auto mt-2 max-w-3xl px-2 text-sm text-[color:var(--fake)]" role="alert">
          {error}
        </p>
      ) : (
        <p className="mx-auto mt-2 max-w-3xl px-2 text-xs text-[var(--faint)]">
          Enter envia. Shift+Enter quebra linha. O Berkanan não substitui orientação médica.
        </p>
      )}
    </div>
  )
}
