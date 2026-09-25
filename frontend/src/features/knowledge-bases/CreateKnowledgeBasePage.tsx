import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateKnowledgeBase } from './hooks'

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export function CreateKnowledgeBasePage() {
  const navigate = useNavigate()
  const createKb = useCreateKnowledgeBase()
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { name: '', description: '' } })

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      const kb = await createKb.mutateAsync({
        name: values.name,
        description: values.description || undefined,
      })
      toast.success('Knowledge base created')
      navigate(`/knowledge-bases/${kb.id}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create')
    }
  })

  return (
    <Card className="mx-auto max-w-lg">
      <CardHeader>
        <CardTitle>New knowledge base</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input id="name" {...form.register('name')} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Input id="description" {...form.register('description')} />
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => navigate('/')}>Cancel</Button>
            <Button type="submit" disabled={createKb.isPending}>Create</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
