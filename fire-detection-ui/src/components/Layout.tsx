'use client'

import { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDesktop, setIsDesktop] = useState(false)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const handleResize = () => {
        setIsDesktop(window.innerWidth >= 768)
      }
      handleResize()
      window.addEventListener('resize', handleResize)
      return () => window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <div className="flex min-h-screen transition-colors duration-500 ease-in-out bg-white text-zinc-900 dark:bg-zinc-950 dark:text-white">
      {/* 사이드바 */}
      <Sidebar isOpen={sidebarOpen || isDesktop} onClose={() => setSidebarOpen(false)} />

      {/* 본문 영역 */}
      <div
        className={`flex flex-col flex-1 transition-all duration-300 ease-in-out ${
          isDesktop ? 'ml-64' : ''
        }`}
        style={isDesktop ? { width: 'calc(100% - 16rem)' } : {}}
      >
        <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <main className="px-4 py-6 max-w-screen-xl mx-auto overflow-x-hidden transition-colors duration-500 ease-in-out">
          {children}
        </main>
      </div>
    </div>
  )
}
