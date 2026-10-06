
const EXAMPLES = [
  "Canela cura diabetes?",
  "Diabético pode comer frutas?",
  "Açúcar mascavo é mais saudável para quem tem diabetes?",
  "Chá natural controla a glicemia?",
]

export function ChatEmptyState({ onExample }: { onExample: (text: string) => void }) {
  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col justify-center px-4 py-10">
      <h1 className="mt-5 text-3xl font-semibold tracking-tight">Verifique uma afirmação alimentar</h1>
      <p className="mt-3 max-w-xl text-sm leading-7 text-[var(--muted)]">
        O Berkanan analisa alegações sobre diabetes, nutrição e mitos alimentares com base em evidências. Não é diagnóstico, prescrição nem substituto de orientação médica.
      </p>
      <div className="mt-7 grid gap-3 sm:grid-cols-2">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => onExample(example)}
            className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] px-4 py-4 text-left text-sm leading-6 shadow-[var(--shadow)] transition hover:-translate-y-0.5"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  )
}
