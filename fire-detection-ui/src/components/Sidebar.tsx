interface SidebarProps {
    isOpen: boolean
    onClose: () => void
  }
  
  export default function Sidebar({ isOpen, onClose }: SidebarProps) {
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 768
  
    return (
      <>
        {/* 모바일 배경 오버레이 */}
        {isMobile && isOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />
        )}
  
        <aside
          className={`z-50 h-full w-64 bg-zinc-800 p-4 
          ${isMobile ? "fixed top-0 left-0 transform transition-transform duration-300" : "fixed top-0 left-0"}
          ${isMobile ? (isOpen ? "translate-x-0" : "-translate-x-full") : ""}
          `}
        >
          <h1 className="text-xl font-bold mb-6 text-white">🔥 Fire UI</h1>
          <nav className="flex flex-col space-y-4 text-white">
            <a href="/dashboard" className="hover:text-orange-400">Dashboard</a>
            <a href="/camera" className="hover:text-orange-400">Camera</a>
            <a href="/logs" className="hover:text-orange-400">Logs</a>
            <a href="/settings" className="hover:text-orange-400">Settings</a>
          </nav>
        </aside>
      </>
    )
  }
  