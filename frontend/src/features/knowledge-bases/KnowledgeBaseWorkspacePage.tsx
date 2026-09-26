import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DocumentsPanel } from '@/features/documents/DocumentsPanel'
import { AskPanel } from '@/features/chat/AskPanel'
import { SearchPanel } from '@/features/search/SearchPanel'
import { HistoryPanel } from '@/features/history/HistoryPanel'
import { useKnowledgeBase } from './hooks'

export function KnowledgeBaseWorkspacePage() {
  const { kbId: kbIdParam } = useParams()
  const kbId = Number(kbIdParam)
  const { data: kb, isLoading, error } = useKnowledgeBase(kbId)

  if (!kbIdParam || Number.isNaN(kbId)) {
    return <p className="text-destructive">Invalid knowledge base.</p>
  }

  if (isLoading) return <Skeleton className="h-48 w-full" />
  if (error || !kb) return <p className="text-destructive">{error?.message ?? 'Knowledge base not found'}</p>

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Link>
        </Button>
        <div>
          <h2 className="text-2xl font-semibold">{kb.name}</h2>
          <p className="text-sm text-muted-foreground">{kb.description || 'Knowledge base workspace'}</p>
        </div>
      </div>

      <Tabs defaultValue="ask">
        <TabsList>
          <TabsTrigger value="ask">Ask</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="search">Search</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>
        <TabsContent value="ask">
          <AskPanel kbId={kbId} />
        </TabsContent>
        <TabsContent value="documents">
          <DocumentsPanel kbId={kbId} />
        </TabsContent>
        <TabsContent value="search">
          <SearchPanel kbId={kbId} />
        </TabsContent>
        <TabsContent value="history">
          <HistoryPanel kbId={kbId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
