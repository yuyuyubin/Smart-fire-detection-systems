'use client'

import useSWR from 'swr'
import axios from 'axios'
import Layout from '@/components/Layout'

const fetcher = (url: string) => axios.get(url).then(res => res.data)

export default function LogsPage() {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/fire-events`, fetcher
  )

  return (
    <Layout>
      <div className="max-w-screen-xl px-8 py-6 mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">화재 감지 이력</h1>
        <div className="bg-zinc-800 p-6 rounded-2xl shadow-xl">
          {error ? (
            <p className="text-red-400">불러오기 실패</p>
          ) : isLoading ? (
            <p className="text-zinc-400">로딩 중...</p>
          ) : data && data.length > 0 ? (
            <ul className="divide-y divide-zinc-700">
              {data.map((event: any, idx: number) => (
                <li key={idx} className="py-3 text-white">
                  <p className="text-sm text-zinc-400">{event.timestamp}</p>
                  <p className="text-base font-medium">확률: {event.probability}%</p>
                  <p className="text-sm">상태: {event.status}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-zinc-400">이력이 없습니다.</p>
          )}
        </div>
      </div>
    </Layout>
  )
}
