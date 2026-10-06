import App, { routes } from '@/App.tsx'
import { flattenRoutes } from '@/lib/router.ts'
import { createHead, UnheadProvider } from '@unhead/react/server'
import { renderToString } from 'react-dom/server'
import { StaticRouter } from 'react-router-dom/server'

interface PrerenderData {
  url: string
}

type PrerenderResult = string | {
  html?: string
  head?: {
    lang?: string
    title?: string
    elements?: Set<{
      type: string
      props: Record<string, string>
      children?: string
    }>
  }
  links?: Set<string> | string[]
} | null | undefined

const paths = flattenRoutes(routes)
  .map(route => route.path)

export async function prerender(data: PrerenderData): Promise<PrerenderResult> {
  try {
    const head = createHead({
      disableDefaults: true,
    })

    const html = renderToString(
      <UnheadProvider value={head}>
        <StaticRouter location={data.url}>
          <App />
        </StaticRouter>
      </UnheadProvider>,
    )

    const { parseLinks } = await import('vite-prerender-plugin/parse')

    const links = [
      ...parseLinks(html),
      ...paths,
    ]

    const headTags = await head.resolveTags()
    const lang = headTags.find(tag => tag.tag === 'htmlAttrs')?.props.lang
    const title = headTags.find(tag => tag.tag === 'title')?.textContent
    const elements = headTags
      .filter(tag => tag.tag !== 'htmlAttrs' && tag.tag !== 'title')
      .map(tag => ({
        type: tag.tag,
        props: tag.props,
        children: tag.textContent,
      }))

    return {
      html,
      links,
      head: {
        lang,
        title,
        elements: new Set(elements),
      },
    }
  } catch (e: any) {
    console.warn(`Failed to prerender "${data.url}":`, e.message)
    return null
  }
}
