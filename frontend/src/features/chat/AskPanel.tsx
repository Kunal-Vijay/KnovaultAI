import { Link } from 'react-router-dom'
import { useState } from 'react'
import { RagAnswerMarkdown } from '@/components/RagAnswerMarkdown'
import { Send } from 'lucide-react'
import { toast } from 'sonner'
import { CitationBadges } from '@/components/CitationBadges'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { CorrelationStrip } from '@/components/CorrelationStrip'
import { useAuth } from '@/hooks/useAuth'
import type { ApiMeta, RAGResponse, SearchResultItem } from '@/types/api'
import { askRag } from './api'
import { ApiError } from '@/lib/api-client'
import { searchKnowledge } from '@/features/search/api'
import { useDocuments } from '@/features/documents/hooks'

const EXAMPLE_PROMPTS = [
  'Why does evaluation retry fail?',
  'How is document ingestion structured?',
  'What are the hybrid search parameters?',
]

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  rag?: RAGResponse
  meta?: ApiMeta
}

export function AskPanel({ kbId }: { kbId: number }) {
  const { user } = useAuth()
  const { data: docs } = useDocuments(kbId)
  const hasIndexedDocs = (docs ?? []).some((d) => d.status === 'completed' && (d.chunk_count ?? 0) > 0)
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [contextOpen, setContextOpen] = useState(false)
  const [contextChunks, setContextChunks] = useState<SearchResultItem[]>([])
  const [contextLoading, setContextLoading] = useState(false)

  const submit = async (q: string) => {
    if (!user || !q.trim()) return
    const trimmed = q.trim()
    setQuestion('')
    setMessages((m) => [...m, { role: 'user', content: trimmed }])
    setLoading(true)
    try {
      const { data, meta } = await askRag(user.id, {
        knowledge_base_id: kbId,
        question: trimmed,
        top_k: 5,
      })
      setMessages((m) => [...m, { role: 'assistant', content: data.answer, rag: data, meta }])
    } catch (err) {
      const detail =
        err instanceof ApiError
          ? err.detail
          : err instanceof Error
            ? err.message
            : 'Failed to get answer'
      toast.error(detail)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: `Sorry, I could not generate an answer. ${detail}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const viewContext = async (q: string) => {
    if (!user) return
    setContextLoading(true)
    setContextOpen(true)
    try {
      const { data } = await searchKnowledge(user.id, {
        knowledge_base_id: kbId,
        query: q,
        keyword_query: q,
        top_k: 5,
      })
      setContextChunks(data.results)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to load context')
      setContextChunks([])
    } finally {
      setContextLoading(false)
    }
  }

  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant' && m.rag)

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Ask a question</CardTitle>
          <CardDescription>
            Answers are grounded in documents in this knowledge base.
            {!hasIndexedDocs && ' Upload and wait for indexing to finish before asking.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_PROMPTS.map((p) => (
              <Button key={p} type="button" variant="secondary" size="sm" onClick={() => setQuestion(p)}>
                {p}
              </Button>
            ))}
          </div>
          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              submit(question)
            }}
          >
            <Input
              placeholder="Ask a question…"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
              aria-label="Question"
            />
            <Button
              type="submit"
              disabled={loading || !question.trim() || !hasIndexedDocs}
              aria-label="Send question"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4" aria-live="polite">
        {messages.map((msg, i) => (
          <Card key={i} className={msg.role === 'user' ? 'border-primary/30' : ''}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">{msg.role === 'user' ? 'You' : 'Answer'}</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm dark:prose-invert max-w-none">
              {msg.role === 'assistant' ? (
                <RagAnswerMarkdown content={msg.content} citations={msg.rag?.citations} />
              ) : (
                <p>{msg.content}</p>
              )}
              {msg.rag && (
                <div className="mt-4 space-y-2 not-prose">
                  <p className="text-sm font-medium">Sources</p>
                  <CitationBadges citations={msg.rag.citations} />
                  {msg.meta && <CorrelationStrip meta={msg.meta} />}
                  {msg.rag.routed_model && (
                    <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                      <Badge variant="secondary">{msg.rag.routed_model}</Badge>
                      {msg.rag.usage?.total_tokens != null && (
                        <Badge variant="outline">{msg.rag.usage.total_tokens} tokens</Badge>
                      )}
                      {msg.rag.estimated_cost_usd != null && (
                        <Badge variant="outline">${msg.rag.estimated_cost_usd.toFixed(4)}</Badge>
                      )}
                      {msg.rag.routing_reason && <span>{msg.rag.routing_reason}</span>}
                    </div>
                  )}
                  {msg.rag.execution_id && (
                    <Button type="button" variant="link" size="sm" className="h-auto p-0" asChild>
                      <Link to={`/knowledge-bases/${kbId}/history/${msg.rag.execution_id}`}>View pipeline</Link>
                    </Button>
                  )}
                  <Button type="button" variant="outline" size="sm" onClick={() => viewContext(messages[i - 1]?.content ?? '')}>
                    View retrieved context
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {lastAssistant?.meta && messages.length === 0 && <CorrelationStrip meta={lastAssistant.meta} />}

      <Dialog open={contextOpen} onOpenChange={setContextOpen}>
        <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Retrieved context</DialogTitle>
          </DialogHeader>
          {contextLoading ? (
            <p className="text-sm text-muted-foreground">Loading chunks…</p>
          ) : contextChunks.length === 0 ? (
            <p className="text-sm text-muted-foreground">No chunks retrieved.</p>
          ) : (
            <div className="space-y-3">
              {contextChunks.map((item) => (
                <div key={item.chunk.id} className="rounded-md border p-3 text-sm">
                  <div className="mb-1 flex gap-2 text-xs text-muted-foreground">
                    <Badge variant="secondary">Score {item.score.toFixed(4)}</Badge>
                    <span>Chunk {item.chunk.id}</span>
                  </div>
                  <p className="whitespace-pre-wrap">{item.chunk.content}</p>
                </div>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
