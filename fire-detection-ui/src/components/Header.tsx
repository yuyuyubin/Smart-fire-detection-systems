interface HeaderProps {
  onToggleSidebar: () => void
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  return (
    <header className="h-16 bg-zinc-900 md:ml-6  overflow-x-hidden">
      <div className="flex items-center justify-between px-4 max-w-[1200px] w-full h-full border-b border-zinc-700">
        <div className="flex items-center gap-4">
          <button
            className="md:hidden text-white"
            onClick={onToggleSidebar}
          >
            ☰
          </button>
          <h2 className="text-lg font-semibold text-white"></h2>
        </div>
        <div className="text-sm text-zinc-400">관리자  2025-05-27</div>
      </div>
    </header>
  )
}
