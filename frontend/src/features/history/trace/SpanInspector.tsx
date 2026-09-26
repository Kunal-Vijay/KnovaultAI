import { useMemo, useState } from 'react'
import { CopyButton } from '@/components/CopyButton'
import { JsonViewer } from '@/components/JsonViewer'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import {
  estimateCostUsd,
  extractTokenCount,
  formatCost,
  inferSpanKind,
  normalizeSpanStatusLabel,
  spanIsErrored,
  spanKindAccent,
} from '@/features/history/trace/span-style'
import { spanKey } from '@/features/history/trace/trace-tree'
import { cn, formatDateTime, formatLatency } from '@/lib/utils'
import type { SpanView } from '@/types/history'

export function SpanInspector({
  span,
  parentName,
  open,
  onOpenChange,
}: {
  span: SpanView | null
  parentName?: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [showRaw, setShowRaw] = useState(false)
  const kind = span ? inferSpanKind(span) : 'default'
  const accent = spanKindAccent(kind)
  const tokenCount = extractTokenCount(span?.tokens ?? null)
  const cost = estimateCostUsd(span?.tokens ?? null, span?.model)

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="font-mono text-sm">{span?.name ?? 'Span'}</SheetTitle>
        </SheetHeader>
        {span ? (
          <div className="flex-1 space-y-5 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={spanIsErrored(span.status) ? 'destructive' : 'secondary'}>
                {normalizeSpanStatusLabel(span.status)}
              </Badge>
              <span
                className={cn(
                  'rounded border border-border px-1.5 py-0.5 text-[10px] uppercase tracking-wide',
                  accent.icon,
                )}
              >
                {accent.label}
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                {formatLatency(span.latency_ms)}
              </span>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Span Name" value={span.name} mono />
              <Field label="Status" value={normalizeSpanStatusLabel(span.status)} />
              <Field label="Duration" value={formatLatency(span.latency_ms)} mono />
              <Field label="Parent Span" value={parentName ?? span.parent_span_id ?? '—'} mono />
              <Field label="Model" value={span.model ?? '—'} mono />
              <Field
                label="Tokens"
                value={tokenCount != null ? String(tokenCount) : '—'}
                mono
              />
              <Field label="Est. Cost" value={formatCost(cost)} mono />
              <Field label="Started" value={formatDateTime(span.started_at)} />
            </div>

            {span.error_message ? (
              <div className="rounded-md border border-destructive/30 bg-destructive/10 p-3">
                <p className="text-[11px] uppercase tracking-wide text-destructive">Error</p>
                <p className="mt-1 whitespace-pre-wrap font-mono text-xs text-foreground">
                  {span.error_message}
                </p>
              </div>
            ) : null}

            <PayloadBlock label="Input" value={span.input_preview} />
            <PayloadBlock label="Output" value={span.output_preview} />

            {span.tokens && Object.keys(span.tokens).length > 0 ? (
              <div>
                <p className="mb-1.5 text-[11px] uppercase tracking-wide text-muted-foreground">
                  Token breakdown
                </p>
                <dl className="grid grid-cols-2 gap-2 rounded-md border border-border p-2.5 text-xs">
                  {Object.entries(span.tokens).map(([k, v]) => (
                    <div key={k}>
                      <dt className="text-muted-foreground">{k}</dt>
                      <dd className="font-mono text-foreground">
                        {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                      </dd>
                    </div>
                  ))}
                </dl>
              </div>
            ) : null}

            {span.attributes && Object.keys(span.attributes).length > 0 ? (
              <div>
                <p className="mb-1.5 text-[11px] uppercase tracking-wide text-muted-foreground">
                  Metadata
                </p>
                <dl className="space-y-1.5 rounded-md border border-border p-2.5 text-xs">
                  {Object.entries(span.attributes).map(([k, v]) => (
                    <div key={k} className="flex items-start justify-between gap-3">
                      <dt className="shrink-0 text-muted-foreground">{k}</dt>
                      <dd className="truncate text-right font-mono text-foreground">
                        {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                      </dd>
                    </div>
                  ))}
                </dl>
              </div>
            ) : null}

            <div>
              <button
                type="button"
                className="text-xs font-medium text-primary transition-colors duration-150 hover:text-foreground"
                onClick={() => setShowRaw((v) => !v)}
              >
                {showRaw ? 'Hide JSON' : 'View JSON'}
              </button>
              {showRaw ? (
                <div className="mt-2">
                  <JsonViewer value={span} label="Raw span" />
                </div>
              ) : null}
            </div>

            <Field label="Span ID" value={spanKey(span)} mono copy />
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  )
}

function Field({
  label,
  value,
  mono,
  copy,
}: {
  label: string
  value: string
  mono?: boolean
  copy?: boolean
}) {
  return (
    <div className="min-w-0">
      <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <div className="mt-0.5 flex items-center gap-1">
        <p className={cn('break-all text-sm text-foreground', mono && 'font-mono text-xs')}>
          {value}
        </p>
        {copy && value !== '—' ? <CopyButton value={value} /> : null}
      </div>
    </div>
  )
}

function PayloadBlock({ label, value }: { label: string; value: string | null | undefined }) {
  const preview = useMemo(() => summarizePayload(value), [value])
  const [expanded, setExpanded] = useState(false)

  if (value === null || value === undefined) {
    return (
      <div>
        <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
        <p className="mt-0.5 text-sm text-muted-foreground">—</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between gap-2">
        <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
        <button
          type="button"
          className="text-[11px] text-muted-foreground transition-colors duration-150 hover:text-foreground"
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      </div>
      {!expanded ? (
        <p className="rounded-md border border-border bg-muted/30 px-2.5 py-2 font-mono text-[11px] leading-relaxed text-foreground/90">
          {preview}
        </p>
      ) : (
        <JsonViewer value={value} label={label} />
      )}
    </div>
  )
}

function summarizePayload(value: unknown): string {
  if (typeof value === 'string') {
    return value.length > 180 ? `${value.slice(0, 180)}…` : value
  }
  try {
    const text = JSON.stringify(value)
    return text.length > 180 ? `${text.slice(0, 180)}…` : text
  } catch {
    return String(value)
  }
}
