import { Link } from 'react-router-dom'
import { FolderOpen, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useKnowledgeBases } from './hooks'

export function DashboardPage() {
  const { data: kbs, isLoading, error } = useKnowledgeBases()

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    )
  }

  if (error) {
    return <p className="text-destructive">{error.message}</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Knowledge bases</h2>
          <p className="text-muted-foreground">Select a base to upload documents and ask questions.</p>
        </div>
        <Button asChild>
          <Link to="/knowledge-bases/new">
            <Plus className="h-4 w-4" />
            New knowledge base
          </Link>
        </Button>
      </div>

      {!kbs?.length ? (
        <Card>
          <CardHeader>
            <CardTitle>No knowledge bases yet</CardTitle>
            <CardDescription>Create your first knowledge base to start ingesting documents.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link to="/knowledge-bases/new">Create knowledge base</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {kbs.map((kb) => (
            <Link key={kb.id} to={`/knowledge-bases/${kb.id}`} className="block transition-opacity hover:opacity-90">
              <Card className="h-full">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-lg">{kb.name}</CardTitle>
                    <FolderOpen className="h-5 w-5 text-primary" />
                  </div>
                  <CardDescription>
                    {kb.description || 'No description'}
                    <br />
                    <span className="text-xs">Created {new Date(kb.created_at).toLocaleDateString()}</span>
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
