import { BookOpen } from 'lucide-react'
import { Outlet } from 'react-router-dom'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-accent/30 to-background p-4">
      <div className="mb-8 flex items-center gap-2 text-primary">
        <BookOpen className="h-8 w-8" />
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Assistant</h1>
      </div>
      <Outlet />
    </div>
  )
}
