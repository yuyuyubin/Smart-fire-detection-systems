'use client'

import useSWR from 'swr'
import axios from 'axios'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'

const fetcher = (url: string) => axios.get(url).then(res => res.data)

export default function LogsPage() {
  const { data, error, isLoading } = useSWR(
    '/api-proxy/api/sensors/graph-data', // ✅ 프록시 경로로 수정
    fetcher
  )

  const [selectedBoard, setSelectedBoard] = useState<string>('')

  useEffect(() => {
    if (data && !selectedBoard) {
      const boardList = Object.keys(data)
      if (boardList.length > 0) setSelectedBoard(boardList[0])
    }
  }, [data, selectedBoard])

  const logs = selectedBoard && data && data[selectedBoard]
    ? [...data[selectedBoard]].slice(-10).reverse()
    : []

  return (
    <Layout>
      <div className="max-w-screen-xl px-4 sm:px-6 md:px-8 py-6 mx-auto transition-colors duration-500 text-black dark:text-white">
        <h1 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8 text-center transition-colors duration-500">
          센서 데이터 로그
        </h1>

        {data && (
          <div className="mb-6 flex justify-start">
            <select
              value={selectedBoard}
              onChange={e => setSelectedBoard(e.target.value)}
              className="bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white px-4 py-2 rounded-lg text-sm sm:text-base shadow-md transition-colors duration-500 hover:bg-zinc-200 dark:hover:bg-zinc-700"
            >
              {Object.keys(data).map(boardId => (
                <option key={boardId} value={boardId}>{boardId}</option>
              ))}
            </select>
          </div>
        )}

        {error && <p className="text-red-400 text-center">데이터 불러오기 실패</p>}
        {isLoading && <p className="text-zinc-400 text-center">로딩 중...</p>}

        {/* 테이블: 데스크탑 전용 */}
        {logs.length > 0 && (
          <div className="hidden md:block bg-white dark:bg-zinc-900 p-6 rounded-2xl shadow-xl overflow-auto transition-colors duration-500">
            <table className="w-full text-sm text-zinc-900 dark:text-white table-auto transition-colors duration-500">
              <thead className="border-b border-zinc-300 dark:border-zinc-700 transition-colors duration-500">
                <tr>
                  <th className="px-4 py-3 text-left">Timestamp</th>
                  <th className="px-4 py-3 text-left">Temp (°C)</th>
                  <th className="px-4 py-3 text-left">Humidity (%)</th>
                  <th className="px-4 py-3 text-left">MQ2</th>
                  <th className="px-4 py-3 text-left">Flame</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((entry, idx) => (
                  <tr key={idx} className="border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors duration-300">
                    <td className="px-4 py-2">{entry.timestamp}</td>
                    <td className="px-4 py-2">{entry.sensor_data?.temp}</td>
                    <td className="px-4 py-2">{entry.sensor_data?.humidity}</td>
                    <td className="px-4 py-2">{entry.sensor_data?.mq2}</td>
                    <td className="px-4 py-2">{entry.sensor_data?.flame}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 카드 뷰: 모바일 전용 */}
        <div className="md:hidden space-y-4">
          {logs.map((entry, idx) => (
            <div key={idx} className="bg-white dark:bg-zinc-900 rounded-xl shadow p-4 transition-colors duration-500">
              <p className="text-sm mb-2 text-zinc-500">{entry.timestamp}</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <div>
                  <span className="font-medium">온도:</span> {entry.sensor_data?.temp} °C
                </div>
                <div>
                  <span className="font-medium">습도:</span> {entry.sensor_data?.humidity} %
                </div>
                <div>
                  <span className="font-medium">MQ2:</span> {entry.sensor_data?.mq2}
                </div>
                <div>
                  <span className="font-medium">Flame:</span> {entry.sensor_data?.flame}
                </div>
              </div>
            </div>
          ))}
        </div>

        {!isLoading && logs.length === 0 && (
          <p className="text-zinc-400 text-center">로그 데이터가 없습니다.</p>
        )}
      </div>
    </Layout>
  )
}
