'use client'

import Layout from '@/components/Layout'

export default function SettingsPage() {
  return (
    <Layout>
      <div className="max-w-screen-md px-8 py-6 mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">시스템 설정</h1>
        <div className="bg-zinc-800 p-6 rounded-2xl shadow-xl space-y-4 text-white">
          <div>
            <p className="text-zinc-400 text-sm mb-1">API 서버 주소</p>
            <p className="font-medium">{process.env.NEXT_PUBLIC_API_BASE_URL}</p>
          </div>
          <div>
            <p className="text-zinc-400 text-sm mb-1">모델 버전</p>
            <p className="font-medium">v1.0.2</p>
          </div>
          <div>
            <p className="text-zinc-400 text-sm mb-1">자동 업데이트</p>
            <p className="font-medium">사용 안 함</p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
