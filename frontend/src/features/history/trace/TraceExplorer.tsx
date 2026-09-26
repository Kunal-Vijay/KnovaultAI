import { useMemo, useState } from 'react'
import { JsonViewer } from '@/components/JsonViewer'
import { Skeleton } from '@/components/ui/skeleton'
import { SpanInspector } from '@/features/history/trace/SpanInspector'
import { TraceGraph } from '@/features/history/trace/TraceGraph'
import { TraceWaterfall } from '@/features/history/trace/TraceWaterfall'
import { spanKey } from '@/features/history/trace/trace-tree'
import { cn, formatDateTime, formatLatency } from '@/lib/utils'
import type { ExecutionTraceView, SpanView } from '@/types/history'

type Tab = 'graph' | 'waterfall' | 'events' | 'raw'

export function TraceExplorer({
  trace,
  isLoading,
  error,
}: {
  trace: ExecutionTraceView | undefined
  isLoading?: boolean
  error?: unknown
}) {
  const [tab, setTab] = useState<Tab>('graph')
  const [selected, setSelected] = useState<SpanView | null>(null)

  const parentName = useMemo(() => {
    if (!selected?.parent_span_id || !trace) return null
    return (
      trace.spans.find((s) => spanKey(s) === String(selected.parent_span_id))?.name ?? null
    )
  }, [selected, trace])

  const events = useMemo(() => {
    if (!trace) return []
    return [...trace.spans]
      .sort((a, b) => new Date(a.started_at).getTime() - new Date(b.started_at).getTime())
      .flatMap((span) => {
        const items = [
          {
            id: `${spanKey(span)}-start`,
            at: span.started_at,
            label: 'started',
            span,
          },
        ]
        if (span.ended_at) {
          items.push({
            id: `${spanKey(span)}-end`,
            at: span.ended_at,
            label: span.status === 'failed' || span.status === 'error' ? 'failed' : 'completed',
            span,
          })
        }
        return items
      })
      .sort((a, b) => new Date(a.at).getTime() - new Date(b.at).getTime())
  }, [trace])

  if (isLoading) return <Skeleton className="h-[480px] w-full" />

  if (error) {
    return (
      <p className="text-sm text-destructive">
        {error instanceof Error ? error.message : 'Failed to load trace'}
      </p>
    )
  }

  if (!trace || trace.spans.length === 0) {
    return <p className="text-sm text-muted-foreground">No pipeline spans recorded.</p>
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-1 border-b border-border">
        {(
          [
            ['graph', 'Graph'],
            ['waterfall', 'Waterfall'],
            ['events', 'Events'],
            ['raw', 'Raw'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={cn(
              'px-3 py-1.5 text-xs font-medium transition-colors duration-150',
              tab === id
                ? 'border-b-2 border-primary text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            )}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'graph' ? (
        <TraceGraph
          spans={trace.spans}
          selectedId={selected ? spanKey(selected) : null}
          onSelect={setSelected}
        />
      ) : null}
      {tab === 'waterfall' ? (
        <TraceWaterfall
          trace={trace}
          selectedId={selected ? spanKey(selected) : null}
          onSelect={setSelected}
        />
      ) : null}
      {tab === 'events' ? (
        <div className="rounded-md border border-border">
          <ul className="divide-y divide-border">
            {events.map((ev) => (
              <li key={ev.id}>
                <button
                  type="button"
                  className={cn(
                    'flex w-full items-center gap-3 px-3 py-2 text-left transition-colors duration-150 hover:bg-muted/40',
                    selected && spanKey(selected) === spanKey(ev.span) && 'bg-accent/50',
                  )}
                  onClick={() => setSelected(ev.span)}
                >
                  <span className="w-40 shrink-0 font-mono text-[11px] text-muted-foreground">
                    {formatDateTime(ev.at)}
                  </span>
                  <span className="w-20 shrink-0 text-[11px] uppercase tracking-wide text-muted-foreground">
                    {ev.label}
                  </span>
                  <span className="min-w-0 truncate font-mono text-xs text-foreground">
                    {ev.span.name}
                  </span>
                  <span className="ml-auto shrink-0 font-mono text-[11px] text-muted-foreground">
                    {formatLatency(ev.span.latency_ms)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {tab === 'raw' ? <JsonViewer value={trace} label="ExecutionTraceView" /> : null}

      <SpanInspector
        span={selected}
        parentName={parentName}
        open={Boolean(selected)}
        onOpenChange={(open) => {
          if (!open) setSelected(null)
        }}
      />
    </div>
  )
}
