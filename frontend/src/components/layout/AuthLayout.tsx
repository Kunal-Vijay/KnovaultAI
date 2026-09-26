import { BookOpen } from 'lucide-react'
import { Outlet } from 'react-router-dom'
import { APP_NAME, APP_TAGLINE } from '@/lib/branding'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-accent/30 to-background p-4">
      <div className="mb-8 flex flex-col items-center gap-1 text-primary">
        <div className="flex items-center gap-2">
          <BookOpen className="h-8 w-8" />
          <h1 className="text-2xl font-bold tracking-tight">{APP_NAME}</h1>
        </div>
        <p className="text-sm text-muted-foreground">{APP_TAGLINE}</p>
      </div>
      <Outlet />
    </div>
  )
}
