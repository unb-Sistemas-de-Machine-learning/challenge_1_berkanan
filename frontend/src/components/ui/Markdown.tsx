import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Components } from "react-markdown"

type MarkdownProps = {
  children: string
  className?: string
}

const components: Components = {
  h1: ({ children }) => (
    <h3 className="mt-4 text-sm font-semibold text-[var(--ink)] first:mt-0">{children}</h3>
  ),
  h2: ({ children }) => (
    <h3 className="mt-4 text-sm font-semibold text-[var(--ink)] first:mt-0">{children}</h3>
  ),
  h3: ({ children }) => (
    <h4 className="mt-4 text-sm font-semibold text-[var(--ink)] first:mt-0">{children}</h4>
  ),
  h4: ({ children }) => (
    <h4 className="mt-3 text-sm font-semibold text-[var(--ink)] first:mt-0">{children}</h4>
  ),
  p: ({ children }) => (
    <p className="mt-2 text-sm leading-6 text-[var(--muted)] first:mt-0">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-[var(--ink)]">{children}</strong>
  ),
  em: ({ children }) => <em className="italic">{children}</em>,
  ul: ({ children }) => (
    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-[var(--muted)] first:mt-0">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="mt-2 list-decimal space-y-1 pl-5 text-sm leading-6 text-[var(--muted)] first:mt-0">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="pl-0.5">{children}</li>,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-[var(--accent)] underline underline-offset-2 hover:opacity-80"
    >
      {children}
    </a>
  ),
  blockquote: ({ children }) => (
    <blockquote className="mt-2 border-l-2 border-[var(--accent)]/40 pl-3 text-sm italic leading-6 text-[var(--muted)]">
      {children}
    </blockquote>
  ),
  code: ({ children }) => (
    <code className="rounded bg-[var(--bg-accent)] px-1.5 py-0.5 font-mono text-[0.85em] text-[var(--ink)]">
      {children}
    </code>
  ),
  pre: ({ children }) => (
    <pre className="mt-2 overflow-x-auto rounded-xl bg-[var(--bg-accent)] p-3 text-xs leading-5">
      {children}
    </pre>
  ),
  hr: () => <hr className="my-4 border-[var(--line)]" />,
  table: ({ children }) => (
    <div className="mt-3 overflow-x-auto">
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-[var(--line)] bg-[var(--bg-accent)] px-3 py-2 text-left text-xs font-semibold text-[var(--ink)]">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-[var(--line)] px-3 py-2 text-xs text-[var(--muted)]">{children}</td>
  ),
}

export function Markdown({ children, className }: MarkdownProps) {
  return (
    <div className={className}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  )
}