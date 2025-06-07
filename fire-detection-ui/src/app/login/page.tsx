'use client'

import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function LoginPage() {
  const router = useRouter()
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isDarkMode, setIsDarkMode] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('auth')
    const darkStored = localStorage.getItem('theme') === 'dark'
    setIsDarkMode(darkStored)

    if (stored === 'true') router.push('/dashboard')
    if (darkStored) document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
  }, [router])

  const handleLogin = () => {
    if (id === 'admin' && password === '1234') {
      localStorage.setItem('auth', 'true')
      router.push('/dashboard')
    } else {
      setError('ID 또는 비밀번호가 올바르지 않습니다.')
    }
  }

  const toggleDarkMode = () => {
    const next = !isDarkMode
    setIsDarkMode(next)
    localStorage.setItem('theme', next ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', next)
  }

  return (
    <main className="flex items-center justify-center min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-white transition-colors duration-500 ease-in-out px-4 sm:px-6">
      <div className="w-full max-w-sm sm:max-w-md bg-zinc-100 dark:bg-zinc-900 p-6 sm:p-8 rounded-2xl shadow-xl transition-colors duration-500 space-y-6 relative">
        {/* 다크모드 토글 버튼 */}
        <button
          onClick={toggleDarkMode}
          className="absolute top-4 right-4 text-xs sm:text-sm bg-zinc-700 text-white px-3 py-1 rounded-md hover:bg-zinc-600 transition"
        >
          {isDarkMode ? '라이트 모드' : '다크 모드'}
        </button>

        <h1 className="text-2xl sm:text-3xl font-bold text-center">로그인</h1>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">ID</label>
            <input
              type="text"
              value={id}
              onChange={e => setId(e.target.value)}
              className="w-full px-4 py-2 text-base bg-zinc-200 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-md text-black dark:text-white transition-colors duration-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full px-4 py-2 text-base bg-zinc-200 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-md text-black dark:text-white transition-colors duration-300"
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </div>

        <button
          onClick={handleLogin}
          className="w-full py-3 sm:py-3.5 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold rounded-lg text-base sm:text-lg transition-all duration-300"
        >
          로그인
        </button>
      </div>
    </main>
  )
}
