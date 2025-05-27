// src/components/Header.tsx
interface HeaderProps {
    onToggleSidebar: () => void
  }
  
  export default function Header({ onToggleSidebar }: HeaderProps) {
    return (
      <header className="h-16 flex items-center justify-between px-4 bg-zinc-900 border-b border-zinc-700 md:ml-64">
        <div className="flex items-center gap-4">
          {/* ✅ 햄버거 버튼 (모바일 전용) */}
          <button
            className="md:hidden text-white"
            onClick={onToggleSidebar}
          >
            ☰
          </button>
          <h2 className="text-lg font-semibold text-white">Dashboard</h2>
        </div>
        <div className="text-sm text-zinc-400">관리자 | 2025-05-27</div>
      </header>
    )
  }
  