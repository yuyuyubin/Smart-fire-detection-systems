'use client'

import { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDesktop, setIsDesktop] = useState(false)

  // 창 크기 감지
  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth >= 768)
    }
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className="flex min-h-screen">
      {/* 사이드바 */}
      <Sidebar isOpen={sidebarOpen || isDesktop} onClose={() => setSidebarOpen(false)} />

      {/* 본문 영역 */}
      <div
        className={isDesktop ? 'ml-64 w-full' : 'w-full'}
        style={isDesktop ? { width: 'calc(100% - 16rem)' } : {}}
      >
        <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <main className="px-4 py-6 max-w-screen-xl mx-auto overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}
