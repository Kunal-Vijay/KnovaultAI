import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useQueryHistory } from './hooks'

function formatCost(v: number | null | undefined) {
  if (v == null) return '—'
  if (v === 0) return '$0'
  return `$${v.toFixed(4)}`
}

export function HistoryPanel({ kbId }: { kbId: number }) {
  const { data, isLoading, error } = useQueryHistory(kbId)

  if (isLoading) return <Skeleton className="h-48 w-full" />
  if (error) return <p className="text-destructive">{error.message}</p>

  const items = data?.items ?? []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Query history</CardTitle>
        <CardDescription>Past RAG requests with model, tokens, and pipeline traces.</CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No queries yet. Ask a question in the Ask tab.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left">
                <tr>
                  <th className="p-3 font-medium">Question</th>
                  <th className="p-3 font-medium">Status</th>
                  <th className="p-3 font-medium">Model</th>
                  <th className="p-3 font-medium">Tokens</th>
                  <th className="p-3 font-medium">Cost</th>
                  <th className="p-3 font-medium">When</th>
                  <th className="p-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {items.map((row) => (
                  <tr key={row.execution_id} className="border-t">
                    <td className="max-w-xs truncate p-3">{row.question}</td>
                    <td className="p-3">
                      <Badge variant={row.status === 'failed' ? 'outline' : 'secondary'}>{row.status}</Badge>
                    </td>
                    <td className="p-3 text-muted-foreground">{row.routed_model ?? '—'}</td>
                    <td className="p-3 text-muted-foreground">{row.total_tokens ?? '—'}</td>
                    <td className="p-3 text-muted-foreground">{formatCost(row.estimated_cost_usd)}</td>
                    <td className="p-3 text-muted-foreground">{new Date(row.created_at).toLocaleString()}</td>
                    <td className="p-3">
                      <Button variant="link" size="sm" asChild>
                        <Link to={`/knowledge-bases/${kbId}/history/${row.execution_id}`}>View Details</Link>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
