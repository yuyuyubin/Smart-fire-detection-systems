'use client'

import { useTheme } from '@/hooks/useTheme'
import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

interface HeaderProps {
  onToggleSidebar: () => void
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'
  const pathname = usePathname()

  // 경로에 따라 헤더 제목을 변경
  const getTitle = () => {
    if (pathname.startsWith('/dashboard')) return 'Dashboard'
    if (pathname.startsWith('/logs')) return '로그 기록'
    if (pathname.startsWith('/settings')) return '설정'
    if (pathname.startsWith('/help')) return '도움말'
    if (pathname.startsWith('/camera')) return '실시간 카메라'
    return 'Fire Detection System'
  }

  return (
    <header className="h-16 bg-white dark:bg-zinc-900 md:ml-6 overflow-x-hidden shadow-sm border-b border-zinc-200 dark:border-zinc-700 transition-colors duration-500 ease-in-out">
      <div className="flex items-center justify-between px-3 sm:px-4 max-w-screen-xl w-full h-full">
        {/* 왼쪽: 메뉴 & 제목 */}
        <div className="flex items-center gap-3 sm:gap-4">
          <button
            className="sm:hidden text-black dark:text-white text-xl transition-colors duration-500"
            onClick={onToggleSidebar}
          >
            ☰
          </button>
          <h2 className="text-base sm:text-lg font-semibold text-black dark:text-white transition-colors duration-500 truncate max-w-[150px] sm:max-w-none">
            {getTitle()}
          </h2>
        </div>

        {/* 오른쪽: 시간 + 테마 */}
        <div className="flex items-center gap-2 sm:gap-4 text-xs sm:text-sm">
          <TimeDisplay />
          <button
            onClick={toggleTheme}
            className="px-2 sm:px-3 py-1 border border-zinc-300 dark:border-zinc-600 rounded text-black dark:text-white transition-colors duration-500"
          >
            {isDark ? '🌞' : '🌙'}
          </button>
        </div>
      </div>
    </header>
  )
}

function TimeDisplay() {
  const [time, setTime] = useState<Date | null>(null)

  useEffect(() => {
    const update = () => setTime(new Date())
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [])

  if (!time) return null

  const formattedDate = time.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
  const formattedTime = time.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })

  return (
    <span className="text-zinc-600 dark:text-zinc-400 transition-colors duration-500 whitespace-nowrap">
      관리자 | {formattedDate} {formattedTime}
    </span>
  )
}
