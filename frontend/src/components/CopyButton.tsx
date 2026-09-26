import { useState } from 'react'
import { Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { copyText } from '@/lib/utils'

export function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)

  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      className="h-6 w-6 p-0"
      aria-label="Copy"
      onClick={async () => {
        const ok = await copyText(value)
        if (ok) {
          setCopied(true)
          window.setTimeout(() => setCopied(false), 1500)
        }
      }}
    >
      <Copy className="h-3 w-3" />
      {copied ? <span className="sr-only">Copied</span> : null}
    </Button>
  )
}
