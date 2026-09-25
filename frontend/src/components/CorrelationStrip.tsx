import { Copy } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import type { ApiMeta } from '@/types/api'

export function CorrelationStrip({ meta }: { meta: ApiMeta }) {
  const id = meta.requestId ?? meta.traceparent
  if (!id && meta.durationMs === 0) return null

  const copy = () => {
    if (id) {
      navigator.clipboard.writeText(id)
      toast.success('Copied correlation ID')
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-md border bg-muted/50 px-3 py-2 text-xs text-muted-foreground">
      {id && (
        <>
          <span className="font-medium text-foreground">Correlation:</span>
          <code className="max-w-[240px] truncate">{id}</code>
          <Button type="button" variant="ghost" size="icon" className="h-7 w-7" onClick={copy} aria-label="Copy ID">
            <Copy className="h-3.5 w-3.5" />
          </Button>
        </>
      )}
      <span className="ml-auto">{meta.durationMs}ms</span>
    </div>
  )
}
