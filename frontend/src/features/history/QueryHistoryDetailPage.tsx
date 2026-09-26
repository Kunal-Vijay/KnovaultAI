import { Link, useParams } from 'react-router-dom'
import { RagAnswerMarkdown } from '@/components/RagAnswerMarkdown'
import { ArrowLeft } from 'lucide-react'
import { CitationBadges } from '@/components/CitationBadges'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { TraceExplorer } from '@/features/history/trace/TraceExplorer'
import { useQueryDetail, useQueryTrace } from '@/features/history/hooks'

export function QueryHistoryDetailPage() {
  const { kbId: kbIdParam, executionId } = useParams()
  const kbId = Number(kbIdParam)
  const { data: detail, isLoading: detailLoading, error: detailError } = useQueryDetail(kbId, executionId)
  const { data: trace, isLoading: traceLoading, error: traceError } = useQueryTrace(kbId, executionId)

  if (!kbIdParam || Number.isNaN(kbId) || !executionId) {
    return <p className="text-destructive">Invalid URL.</p>
  }

  if (detailLoading) return <Skeleton className="h-64 w-full" />
  if (detailError || !detail) {
    return <p className="text-destructive">{detailError?.message ?? 'Not found'}</p>
  }

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <Button variant="ghost" size="sm" asChild>
        <Link to={`/knowledge-bases/${kbId}`}>
          <ArrowLeft className="h-4 w-4" />
          Back to workspace
        </Link>
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Query</CardTitle>
          <p className="text-sm text-muted-foreground">{detail.question}</p>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2 text-xs">
            <Badge variant="secondary">{detail.status}</Badge>
            {detail.routed_model && <Badge variant="outline">{detail.routed_model}</Badge>}
            {detail.routing_policy && <Badge variant="outline">{detail.routing_policy}</Badge>}
            {detail.usage?.total_tokens != null && (
              <Badge variant="outline">{detail.usage.total_tokens} tokens</Badge>
            )}
            {detail.estimated_cost_usd != null && (
              <Badge variant="outline">${detail.estimated_cost_usd.toFixed(4)}</Badge>
            )}
          </div>
          {detail.routing_reason && (
            <p className="text-sm text-muted-foreground">{detail.routing_reason}</p>
          )}
          {detail.answer && (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <RagAnswerMarkdown content={detail.answer} citations={detail.citations} />
            </div>
          )}
          {detail.citations.length > 0 && <CitationBadges citations={detail.citations} />}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Pipeline</CardTitle>
        </CardHeader>
        <CardContent>
          <TraceExplorer trace={trace} isLoading={traceLoading} error={traceError} />
        </CardContent>
      </Card>
    </div>
  )
}
