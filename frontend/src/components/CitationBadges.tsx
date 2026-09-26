import { Badge } from '@/components/ui/badge'
import { deduplicateCitations, formatCitationLabel } from '@/lib/citations'
import type { Citation } from '@/types/api'

interface CitationBadgesProps {
  citations: Citation[]
  className?: string
}

export function CitationBadges({ citations, className }: CitationBadgesProps) {
  const deduped = deduplicateCitations(citations)
  if (deduped.length === 0) {
    return null
  }

  return (
    <div className={className ?? 'flex flex-wrap gap-2'}>
      {deduped.map((d) => (
        <Badge key={d.documentId} variant="outline">
          {formatCitationLabel(d)}
        </Badge>
      ))}
    </div>
  )
}
