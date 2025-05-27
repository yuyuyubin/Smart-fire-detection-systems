import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Fire Detection System',
  description: 'Smart fire detection UI for capstone project',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  )
}
