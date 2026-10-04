type ErrorStateProps = {
  title?: string
  message: string
}

export function ErrorState({ title = "Algo não saiu como esperado", message }: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="rounded-2xl border border-[color:var(--fake)]/30 bg-[color:var(--fake-bg)] px-4 py-3 text-sm text-[color:var(--fake)]"
    >
      <p className="font-semibold">{title}</p>
      <p className="mt-1 leading-6">{message}</p>
    </div>
  )
}
