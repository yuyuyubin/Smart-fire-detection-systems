'use client'

import Layout from '@/components/Layout'

export default function SettingsPage() {
  return (
    <Layout>
      <div className="max-w-screen-md px-8 py-6 mx-auto text-black dark:text-white transition-colors duration-500">
        <h1 className="text-4xl font-extrabold mb-10 text-center tracking-tight">
          시스템 설정
        </h1>

        <div className="bg-zinc-100 dark:bg-zinc-900 p-6 rounded-2xl shadow-xl space-y-6 transition-colors duration-500">
          {/* API 서버 주소 (마스킹 처리) */}
          <div className="border-b border-zinc-300 dark:border-zinc-700 pb-4">
            <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-1">API 서버 주소</p>
            <p className="font-medium text-zinc-400">http://18.234.***.***:5000</p>
          </div>

          {/* 모델 버전 */}
          <div className="border-b border-zinc-300 dark:border-zinc-700 pb-4">
            <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-1">딥러닝 모델 버전</p>
            <p className="font-medium">YOLOv8 + 센서 모델 v1.0.2</p>
          </div>

          {/* 자동 업데이트 */}
          <div className="border-b border-zinc-300 dark:border-zinc-700 pb-4">
            <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-1">자동 업데이트</p>
            <p className="font-medium">현재: <span className="text-red-400">사용 안 함</span></p>
          </div>

          {/* 데이터 로그 */}
          <div>
            <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-1">로그 파일 저장 위치</p>
            <p className="font-medium">/data/board_logs/*.json, /data/fire_log.json 등</p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
