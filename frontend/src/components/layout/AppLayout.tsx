import { Link, Outlet, useNavigate } from 'react-router-dom'
import { BookOpen, LogOut, Menu, User } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Separator } from '@/components/ui/separator'
import { useAuth } from '@/hooks/useAuth'
import { APP_NAME, APP_TAGLINE } from '@/lib/branding'
import { cn } from '@/lib/utils'

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 w-64 border-r bg-card p-4 transition-transform md:static md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
        )}
      >
        <div className="mb-6">
          <div className="flex items-center gap-2 font-semibold text-primary">
            <BookOpen className="h-5 w-5 shrink-0" />
            <span>{APP_NAME}</span>
          </div>
          <p className="mt-1 pl-7 text-xs text-muted-foreground">{APP_TAGLINE}</p>
        </div>
        <nav className="flex flex-col gap-1 text-sm">
          <Link
            to="/"
            className="rounded-md px-3 py-2 hover:bg-accent"
            onClick={() => setSidebarOpen(false)}
          >
            Dashboard
          </Link>
        </nav>
      </aside>

      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          aria-label="Close menu"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex min-h-screen flex-1 flex-col md:ml-0">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b bg-background/95 px-4 backdrop-blur">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <span className="hidden text-sm text-muted-foreground sm:inline">{APP_TAGLINE}</span>
            <span className="text-sm text-muted-foreground sm:hidden">{APP_NAME}</span>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2">
                <User className="h-4 w-4" />
                {user?.username ?? 'Account'}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem disabled>{user?.email}</DropdownMenuItem>
              <Separator className="my-1" />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
