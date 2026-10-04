import { useState } from "react"
import { ExternalLink } from "lucide-react"
import type { MatchedSource } from "@/types/analysis"

function similarityLabel(value?: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—"
  return `${Math.round(value * 100)}%`
}

type ParsedSource = { url: string; title: string; body: string }

/**
 * O backend injeta um cabeçalho no texto de algumas fontes:
 *   Fonte: https://...
 *   Título: nome_da_fonte
 *   ================================================================================
 * Este parser extrai cada parte e remove a linha de separadores (===, ---, ___, ***).
 * Fontes sem cabeçalho (ex.: SBD_dias_doenca_DM1.txt) caem no fallback.
 */
function parseSourceText(raw?: string): ParsedSource {
  const text = (raw ?? "").trim()
  if (!text) return { url: "", title: "", body: "" }

  let url = ""
  let title = ""
  let body = text

  const urlMatch = body.match(/^Fonte:\s*(\S+)\s*$/im)
  if (urlMatch) {
    url = urlMatch[1]
    body = body.replace(urlMatch[0], "")
  }

  const titleMatch = body.match(/^T[íi]tulo:\s*(.+?)\s*$/im)
  if (titleMatch) {
    title = titleMatch[1]
    body = body.replace(titleMatch[0], "")
  }

  body = body
    .split("\n")
    .filter((line) => !/^[=\-*_]{3,}\s*$/.test(line.trim()))
    .join("\n")
    .trim()

  return { url, title, body }
}

function isValidHttpUrl(value: string): boolean {
  return /^https?:\/\//i.test(value)
}

export function EvidenceCard({ source }: { source: MatchedSource }) {
  const [expanded, setExpanded] = useState(false)

  const parsed = parseSourceText(source.text)
  const url = (source.source_url || parsed.url || "").trim()
  const title = (source.source_title || parsed.title || "").trim()
  const filename = (source.source || "").trim()
  const body = parsed.body

  // Valor principal: URL → título → filename → fallback
  const primarySource = url || title || filename

  // Só mostra linhas extras se forem distintas do valor principal
  const showTitle = title.length > 0 && title !== primarySource
  const showFilename = filename.length > 0 && filename !== primarySource

  const hasBody = body.length > 0
  const longBody = body.length > 320
  const visibleBody = !hasBody
    ? ""
    : expanded || !longBody
      ? body
      : `${body.slice(0, 320).trimEnd()}...`

  return (
    <article className="rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] p-4 sm:p-5">
      <div className="flex items-start justify-between gap-4">
        {/*
          Grid [auto_1fr]: a coluna dos labels se dimensiona pelo mais largo
          ("Arquivo:"), então TODOS os valores ficam alinhados verticalmente.
          Isso dá ritmo e consistência visual entre os cards.
        */}
        <dl className="grid min-w-0 flex-1 grid-cols-[auto_1fr] gap-x-2 gap-y-1 text-xs leading-5">
          <dt className="text-[var(--faint)]">Fonte:</dt>
          <dd className="min-w-0">
            {isValidHttpUrl(primarySource) ? (
              <a
                href={primarySource}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex min-w-0 items-baseline gap-1 text-[var(--accent)] underline-offset-2 hover:underline"
              >
                <span className="min-w-0 break-all">{primarySource}</span>
                <ExternalLink size={11} className="shrink-0 translate-y-[2px]" aria-hidden="true" />
              </a>
            ) : (
              <span className="break-all text-[var(--muted)]">
                {primarySource || "Fonte não identificada"}
              </span>
            )}
          </dd>

          {showTitle ? (
            <>
              <dt className="text-[var(--faint)]">Título:</dt>
              <dd className="min-w-0 break-all text-[var(--muted)]">{title}</dd>
            </>
          ) : null}

          {showFilename ? (
            <>
              <dt className="text-[var(--faint)]">Arquivo:</dt>
              <dd className="min-w-0 break-all text-[var(--muted)]">{filename}</dd>
            </>
          ) : null}
        </dl>

        <span className="shrink-0 rounded-full bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--accent)]">
          {similarityLabel(source.similarity)}
        </span>
      </div>

      {hasBody ? (
        <div className="mt-4 border-t border-[var(--line)] pt-3">
          <p className="text-sm leading-6 text-[var(--muted)]">{visibleBody}</p>
          {longBody ? (
            <button
              type="button"
              className="mt-3 text-xs font-semibold text-[var(--accent)] hover:underline"
              onClick={() => setExpanded((v) => !v)}
              aria-expanded={expanded}
            >
              {expanded ? "Recolher trecho" : "Ver trecho completo"}
            </button>
          ) : null}
        </div>
      ) : null}
    </article>
  )
}