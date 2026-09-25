import { useCallback, useRef, useState } from 'react'
import { Upload } from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useDocuments, useUploadDocument } from './hooks'

const ALLOWED_EXT = ['.pdf', '.txt', '.md', '.markdown', '.docx']

function isAllowed(file: File) {
  const lower = file.name.toLowerCase()
  return ALLOWED_EXT.some((ext) => lower.endsWith(ext))
}

export function DocumentsPanel({ kbId }: { kbId: number }) {
  const { data: docs, isLoading, error } = useDocuments(kbId)
  const upload = useUploadDocument(kbId)
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      for (const file of Array.from(files)) {
        if (!isAllowed(file)) {
          toast.error(`${file.name}: allowed types are PDF, TXT, Markdown, DOCX`)
          continue
        }
        try {
          await upload.mutateAsync(file)
          toast.success(`Uploaded ${file.name}`)
        } catch (err) {
          toast.error(err instanceof Error ? err.message : 'Upload failed')
        }
      }
    },
    [upload],
  )

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files)
  }

  return (
    <div className="space-y-4">
      <Card
        className={`border-dashed ${dragOver ? 'border-primary bg-accent/50' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <CardHeader>
          <CardTitle className="text-base">Upload documents</CardTitle>
          <CardDescription>Drag and drop or choose PDF, TXT, Markdown, or DOCX files.</CardDescription>
        </CardHeader>
        <CardContent>
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            multiple
            accept=".pdf,.txt,.md,.markdown,.docx"
            onChange={(e) => e.target.files && handleFiles(e.target.files)}
          />
          <Button type="button" variant="outline" onClick={() => inputRef.current?.click()} disabled={upload.isPending}>
            <Upload className="h-4 w-4" />
            Choose files
          </Button>
        </CardContent>
      </Card>

      {isLoading && <Skeleton className="h-40 w-full" />}
      {error && <p className="text-destructive">{error.message}</p>}

      {docs && docs.length > 0 && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-left">
              <tr>
                <th className="p-3 font-medium">Filename</th>
                <th className="p-3 font-medium">Status</th>
                <th className="p-3 font-medium">Type</th>
                <th className="p-3 font-medium">Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.id} className="border-t">
                  <td className="p-3">{doc.filename}</td>
                  <td className="p-3">
                    <Badge variant={doc.status === 'failed' ? 'outline' : 'secondary'} className={doc.status === 'failed' ? 'border-destructive text-destructive' : ''}>{doc.status}</Badge>
                  </td>
                  <td className="p-3 text-muted-foreground">{doc.mime_type ?? '—'}</td>
                  <td className="p-3 text-muted-foreground">{new Date(doc.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
