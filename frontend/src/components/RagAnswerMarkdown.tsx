import { useMemo } from 'react'
import Markdown from 'react-markdown'
import type { Components } from 'react-markdown'
import { Badge } from '@/components/ui/badge'
import { chunkIndexFromHref, linkifyChunkReferences } from '@/lib/chunk-citations'
import type { Citation } from '@/types/api'

function citationTooltip(citations: Citation[] | undefined, index: number): string | undefined {
  const c = citations?.[index - 1]
  if (!c) return undefined
  const parts = [c.source ?? `doc ${c.document_id}`]
  if (c.page_number != null) parts.push(`p.${c.page_number}`)
  if (c.section) parts.push(c.section)
  return parts.join(' · ')
}

export function RagAnswerMarkdown({
  content,
  citations,
}: {
  content: string
  citations?: Citation[]
}) {
  const processed = useMemo(() => linkifyChunkReferences(content), [content])

  const components: Components = useMemo(
    () => ({
      a: ({ href, children, ...props }) => {
        const chunkIndex = chunkIndexFromHref(href)
        if (chunkIndex != null) {
          const title = citationTooltip(citations, chunkIndex)
          return (
            <Badge
              variant="outline"
              className="mx-0.5 inline-flex align-middle text-[11px] font-normal not-prose"
              title={title}
            >
              {children}
            </Badge>
          )
        }
        return (
          <a href={href} {...props} className="text-primary underline-offset-2 hover:underline">
            {children}
          </a>
        )
      },
    }),
    [citations],
  )

  return (
    <Markdown components={components}>{processed}</Markdown>
  )
}
