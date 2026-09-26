import type { SpanView } from '@/types/history'

export type SpanKind =
  | 'llm'
  | 'retrieval'
  | 'tool'
  | 'verification'
  | 'analysis'
  | 'planner'
  | 'default'

export function spanIsErrored(status: string): boolean {
  const s = status.toLowerCase()
  return s === 'failed' || s === 'error'
}

export function normalizeSpanStatusLabel(status: string): string {
  const s = status.toLowerCase()
  if (s === 'completed' || s === 'ok') return 'OK'
  if (spanIsErrored(status)) return 'FAIL'
  return status.toUpperCase()
}

export function inferSpanKind(span: Pick<SpanView, 'name' | 'attributes' | 'model'>): SpanKind {
  const name = span.name.toLowerCase()
  const attrs = span.attributes ?? {}
  const kindAttr = String(attrs.span_kind ?? attrs.kind ?? attrs.type ?? '').toLowerCase()

  if (
    kindAttr.includes('llm') ||
    name.includes('llm') ||
    name.includes('generate') ||
    name.includes('completion') ||
    name.includes('chat') ||
    Boolean(span.model)
  ) {
    return 'llm'
  }
  if (
    kindAttr.includes('retriev') ||
    kindAttr.includes('rag') ||
    name.includes('retriev') ||
    name.includes('embed') ||
    name.includes('search')
  ) {
    return 'retrieval'
  }
  if (kindAttr.includes('tool') || name.includes('tool') || name.includes('function')) {
    return 'tool'
  }
  if (kindAttr.includes('verif') || name.includes('verif') || name.includes('guard')) {
    return 'verification'
  }
  if (
    kindAttr.includes('analys') ||
    name.includes('root cause') ||
    name.includes('analysis') ||
    name.includes('rca')
  ) {
    return 'analysis'
  }
  if (kindAttr.includes('plan') || name.includes('plan')) {
    return 'planner'
  }
  return 'default'
}

export function spanKindAccent(kind: SpanKind): {
  border: string
  icon: string
  bar: string
  label: string
} {
  switch (kind) {
    case 'llm':
      return {
        border: 'border-l-violet-500',
        icon: 'text-violet-600',
        bar: 'bg-violet-500/70',
        label: 'LLM',
      }
    case 'retrieval':
      return {
        border: 'border-l-emerald-500',
        icon: 'text-emerald-600',
        bar: 'bg-emerald-500/70',
        label: 'Retrieval',
      }
    case 'tool':
      return {
        border: 'border-l-amber-500',
        icon: 'text-amber-600',
        bar: 'bg-amber-500/70',
        label: 'Tool',
      }
    case 'verification':
      return {
        border: 'border-l-primary',
        icon: 'text-primary',
        bar: 'bg-primary/70',
        label: 'Verify',
      }
    case 'analysis':
      return {
        border: 'border-l-sky-500',
        icon: 'text-sky-600',
        bar: 'bg-sky-500/70',
        label: 'Analysis',
      }
    case 'planner':
      return {
        border: 'border-l-primary',
        icon: 'text-primary',
        bar: 'bg-primary/60',
        label: 'Planner',
      }
    default:
      return {
        border: 'border-l-border',
        icon: 'text-muted-foreground',
        bar: 'bg-foreground/40',
        label: 'Span',
      }
  }
}

export function extractTokenCount(
  tokens: Record<string, unknown> | null | undefined,
): number | null {
  if (!tokens) return null
  const total =
    tokens.total ??
    tokens.total_tokens ??
    (typeof tokens.prompt === 'number' || typeof tokens.completion === 'number'
      ? Number(tokens.prompt ?? 0) + Number(tokens.completion ?? 0)
      : null) ??
    tokens.prompt_tokens ??
    null
  if (typeof total === 'number' && !Number.isNaN(total)) return total
  if (typeof total === 'string' && total.trim() !== '') {
    const n = Number(total)
    return Number.isNaN(n) ? null : n
  }
  return null
}

export function estimateCostUsd(
  tokens: Record<string, unknown> | null | undefined,
  model?: string | null,
): number | null {
  const cost = tokens?.cost
  if (typeof cost === 'number' && !Number.isNaN(cost)) return cost
  const count = extractTokenCount(tokens)
  if (count == null) return null
  const per1k = model?.toLowerCase().includes('gpt-4') ? 0.03 : 0.002
  return (count / 1000) * per1k
}

export function formatCost(usd: number | null | undefined): string {
  if (usd == null || Number.isNaN(usd)) return '—'
  if (usd < 0.01) return `$${usd.toFixed(4)}`
  return `$${usd.toFixed(3)}`
}
