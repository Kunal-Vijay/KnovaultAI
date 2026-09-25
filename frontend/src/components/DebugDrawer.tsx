import { useState } from 'react'
import { Bug } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

export interface DebugEntry {
  url: string
  status: number
  durationMs: number
  bodyPreview?: string
}

export function DebugDrawer({ lastRequest }: { lastRequest: DebugEntry | null }) {
  const [open, setOpen] = useState(false)
  if (!import.meta.env.DEV) return null

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button type="button" variant="outline" size="sm" className="fixed bottom-4 right-4 z-50 gap-2 shadow-lg">
          <Bug className="h-4 w-4" />
          Debug
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>Last API request</DialogTitle>
        </DialogHeader>
        {lastRequest ? (
          <pre className="whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">{JSON.stringify(lastRequest, null, 2)}</pre>
        ) : (
          <p className="text-sm text-muted-foreground">No requests captured yet.</p>
        )}
      </DialogContent>
    </Dialog>
  )
}
