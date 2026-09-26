import { useMemo, useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { CopyButton } from '@/components/CopyButton'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

function serialize(value: unknown): string {
  if (typeof value === 'string') return value
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

export function JsonViewer({
  value,
  label,
  className,
  defaultCollapsed = false,
  maxHeightClass = 'max-h-80',
}: {
  value: unknown
  label?: string
  className?: string
  defaultCollapsed?: boolean
  maxHeightClass?: string
}) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed)
  const text = useMemo(() => serialize(value), [value])
  const isNull = value === null || value === undefined

  return (
    <div className={cn('rounded-md border border-border bg-muted/20', className)}>
      <div className="flex items-center justify-between gap-2 border-b border-border px-2 py-1.5">
        <button
          type="button"
          className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground"
          onClick={() => setCollapsed((v) => !v)}
        >
          {collapsed ? (
            <ChevronRight className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
          {label ?? 'Data'}
        </button>
        <div className="flex items-center gap-1">
          {!isNull && <CopyButton value={text} />}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-6 px-1.5 text-[11px]"
            onClick={() => setCollapsed((v) => !v)}
          >
            {collapsed ? 'Expand' : 'Collapse'}
          </Button>
        </div>
      </div>
      {!collapsed && (
        <pre
          className={cn(
            'overflow-auto p-3 font-mono text-[12px] leading-relaxed text-foreground/90',
            maxHeightClass,
          )}
        >
          {isNull ? <span className="text-muted-foreground">null</span> : text}
        </pre>
      )}
    </div>
  )
}
