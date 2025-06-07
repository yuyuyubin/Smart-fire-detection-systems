'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [isMobile, setIsMobile] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const handleResize = () => setIsMobile(window.innerWidth < 768)
      handleResize()
      window.addEventListener('resize', handleResize)
      return () => window.removeEventListener('resize', handleResize)
    }
  }, [])

  const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/camera', label: 'Real-Time Camera' },
    { href: '/logs', label: 'Sensor Data Log' },
    { href: '/settings', label: 'System Settings' },
    { href: '/help', label: 'Help' }
  ]

  return (
    <>
      {isMobile && isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          z-50 h-full w-64 bg-white dark:bg-zinc-900 p-6
          transition-colors duration-500
          ${isMobile ? "fixed top-0 left-0 transform transition-transform duration-300" : "fixed top-0 left-0"}
          ${isMobile ? (isOpen ? "translate-x-0" : "-translate-x-full") : ""}
          shadow-lg border-r border-zinc-200 dark:border-zinc-700
        `}
      >
        {/* 상단 제목 */}
        <div className="mb-10">
          <h1 className="text-2xl font-extrabold text-zinc-900 dark:text-white leading-tight transition-colors duration-500">
            Fire<br />Detection System
          </h1>
        </div>

        {/* 네비게이션 */}
        <nav className="flex flex-col space-y-4 text-sm font-medium">
          {navItems.map(({ href, label }) => {
            const isActive = pathname === href
            return (
              <a
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg
                  transition-colors duration-300
                  ${
                    isActive
                      ? "bg-orange-100 text-orange-600 dark:bg-zinc-700 dark:text-orange-400"
                      : "text-zinc-800 dark:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800"
                  }
                `}
              >
                <span>{label}</span>
              </a>
            )
          })}

          {/* 로그아웃 버튼 */}
          <button
            onClick={() => {
              localStorage.removeItem('auth')
              window.location.href = '/login'
            }}
            className="mt-10 px-3 py-2 rounded-lg text-left text-red-500 hover:bg-red-100 dark:hover:bg-zinc-800 transition-colors duration-300"
          >
            로그아웃
          </button>
        </nav>
      </aside>
    </>
  )
}
