import { useMemo } from 'react'
import {
  inferSpanKind,
  spanIsErrored,
  spanKindAccent,
} from '@/features/history/trace/span-style'
import {
  buildSpanForest,
  flattenSpanForest,
  spanKey,
  spanOffsetPercent,
} from '@/features/history/trace/trace-tree'
import { cn, formatLatency } from '@/lib/utils'
import type { ExecutionTraceView, SpanView } from '@/types/history'

export function TraceWaterfall({
  trace,
  selectedId,
  onSelect,
}: {
  trace: ExecutionTraceView
  selectedId?: string | null
  onSelect: (span: SpanView) => void
}) {
  const rows = useMemo(
    () => flattenSpanForest(buildSpanForest(trace.spans)),
    [trace.spans],
  )
  const traceStart = new Date(trace.started_at).getTime()
  const totalMs =
    trace.total_latency_ms && trace.total_latency_ms > 0
      ? trace.total_latency_ms
      : Math.max(
          ...rows.map((s) => {
            const end = s.ended_at
              ? new Date(s.ended_at).getTime()
              : new Date(s.started_at).getTime() + (s.latency_ms ?? 0)
            return end - traceStart
          }),
          1,
        )

  const ticks = [0, 0.25, 0.5, 0.75, 1]

  return (
    <div className="rounded-md border border-border bg-card/40">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="text-[11px] uppercase tracking-wide text-muted-foreground">Timing</span>
        <span className="font-mono text-[11px] text-muted-foreground">
          Total {formatLatency(totalMs)}
        </span>
      </div>

      <div className="overflow-x-auto p-3">
        <div className="mb-2 grid grid-cols-[minmax(140px,200px)_1fr_72px] gap-2 pl-1 text-[10px] text-muted-foreground">
          <span>Span</span>
          <div className="relative h-4">
            {ticks.map((t) => (
              <span
                key={t}
                className="absolute top-0 font-mono"
                style={{ left: `${t * 100}%`, transform: 'translateX(-50%)' }}
              >
                {formatLatency(totalMs * t)}
              </span>
            ))}
          </div>
          <span className="text-right">Duration</span>
        </div>

        <div className="space-y-1">
          {rows.map((span) => {
            const { left, width } = spanOffsetPercent(span, traceStart, totalMs)
            const errored = spanIsErrored(span.status)
            const accent = spanKindAccent(inferSpanKind(span))
            const selected = selectedId === spanKey(span)

            return (
              <button
                type="button"
                key={spanKey(span)}
                className={cn(
                  'grid w-full min-w-[480px] grid-cols-[minmax(140px,200px)_1fr_72px] items-center gap-2 rounded-md px-1 py-1 text-left transition-colors duration-150 hover:bg-muted/50',
                  selected && 'bg-accent/60',
                )}
                onClick={() => onSelect(span)}
              >
                <span
                  className="truncate font-mono text-[11px] text-foreground"
                  style={{ paddingLeft: span.depth * 12 }}
                  title={span.name}
                >
                  {span.depth > 0 ? (
                    <span className="mr-1 text-muted-foreground">└</span>
                  ) : null}
                  {span.name}
                </span>
                <div className="relative h-5 overflow-hidden rounded-sm bg-muted/50">
                  <div
                    className={cn(
                      'absolute inset-y-0.5 rounded-sm transition-[opacity,box-shadow] duration-150',
                      errored ? 'bg-destructive/80' : accent.bar,
                      selected && 'ring-1 ring-primary',
                    )}
                    style={{ left: `${left}%`, width: `${Math.max(width, 0.8)}%` }}
                  />
                </div>
                <span className="text-right font-mono text-[11px] text-muted-foreground">
                  {formatLatency(span.latency_ms)}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
