import { useState } from "react"
import { Outlet } from "react-router-dom"
import { Menu } from "lucide-react"
import { AppSidebar } from "@/components/layout/AppSidebar"

export function AppShell() {
  const [open, setOpen] = useState(false)

  return (
    <div className="h-dvh bg-[var(--bg)] lg:grid lg:grid-cols-[18.5rem_minmax(0,1fr)] lg:grid-rows-1">
      <AppSidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex h-full min-h-0 min-w-0 flex-col">
        <header className="flex items-center justify-between border-b border-[var(--line)] bg-[var(--surface)] px-4 py-3 lg:hidden">
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="rounded-full p-2"
            aria-label="Abrir menu"
          >
            <Menu size={18} />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold tracking-[0.14em]">BERKANAN</span>
          </div>
          <span className="w-8" />
        </header>
        <Outlet />
      </div>
    </div>
  )
}