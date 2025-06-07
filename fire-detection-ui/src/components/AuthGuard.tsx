'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token !== 'authenticated') {
      router.push('/login')
    }
  }, [router])

  return <>{children}</>
}
