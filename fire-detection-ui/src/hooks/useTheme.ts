import { useEffect, useState } from 'react'

export function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  useEffect(() => {
    const storedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (storedTheme) {
      setTheme(storedTheme)
      applyThemeWithTransition(storedTheme)
    } else {
      setTheme('dark')
      applyThemeWithTransition('dark')
      localStorage.setItem('theme', 'dark')
    }
  }, [])

  const applyThemeWithTransition = (newTheme: 'light' | 'dark') => {
    const root = document.documentElement

    // 🌟 트랜지션 클래스 추가
    root.classList.add('transition-colors', 'duration-500')

    // 모드 적용
    root.classList.toggle('dark', newTheme === 'dark')

    // 트랜지션 제거 타이머 (500ms 이후 제거)
    setTimeout(() => {
      root.classList.remove('transition-colors', 'duration-500')
    }, 500)
  }

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    applyThemeWithTransition(newTheme)
    localStorage.setItem('theme', newTheme)
  }

  return { theme, toggleTheme }
}
