import { useState } from 'react'
import { Search } from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { CorrelationStrip } from '@/components/CorrelationStrip'
import { useAuth } from '@/hooks/useAuth'
import type { ApiMeta, SearchResultItem } from '@/types/api'
import { searchKnowledge } from './api'

export function SearchPanel({ kbId }: { kbId: number }) {
  const { user } = useAuth()
  const [query, setQuery] = useState('')
  const [keywordQuery, setKeywordQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<SearchResultItem[]>([])
  const [meta, setMeta] = useState<ApiMeta | null>(null)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const runSearch = async () => {
    if (!user || !query.trim()) return
    setLoading(true)
    try {
      const { data, meta: m } = await searchKnowledge(user.id, {
        knowledge_base_id: kbId,
        query: query.trim(),
        keyword_query: keywordQuery.trim() || undefined,
        top_k: topK,
      })
      setResults(data.results)
      setMeta(m)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Hybrid search</CardTitle>
          <CardDescription>Test retrieval with semantic + keyword fusion and scores.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row">
            <Input
              placeholder="Search your knowledge base…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && runSearch()}
            />
            <Button type="button" onClick={runSearch} disabled={loading || !query.trim()}>
              <Search className="h-4 w-4" />
              Search
            </Button>
          </div>
          <Button type="button" variant="ghost" size="sm" onClick={() => setShowAdvanced((v) => !v)}>
            {showAdvanced ? 'Hide' : 'Show'} advanced
          </Button>
          {showAdvanced && (
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <Label>Keyword query</Label>
                <Input value={keywordQuery} onChange={(e) => setKeywordQuery(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label>Top K</Label>
                <Input type="number" min={1} max={20} value={topK} onChange={(e) => setTopK(Number(e.target.value))} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {meta && <CorrelationStrip meta={meta} />}

      {loading && (
        <div className="space-y-2">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      )}

      {!loading && results.length === 0 && meta && (
        <p className="text-sm text-muted-foreground">No results for this query.</p>
      )}

      <div className="space-y-3">
        {results.map((item, idx) => (
          <Card key={`${item.chunk.id}-${idx}`}>
            <CardHeader className="pb-2">
              <div className="flex flex-wrap items-center gap-2">
                <Badge>Score {item.score.toFixed(4)}</Badge>
                <span className="text-xs text-muted-foreground">
                  Doc {item.chunk.document_id} · Chunk {item.chunk.id}
                  {item.chunk.page_number != null && ` · p.${item.chunk.page_number}`}
                </span>
              </div>
              {item.chunk.source && <CardDescription>{item.chunk.source}</CardDescription>}
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-wrap line-clamp-6">{item.chunk.content}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
