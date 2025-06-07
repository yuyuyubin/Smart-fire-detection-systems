'use client'

import useSWR from 'swr'
import axios from 'axios'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Layout from '@/components/Layout'
import FireStatusCard from '@/components/FireStatusCard'
import SensorStatusCard from '@/components/SensorStatusCard'
import CameraFeed from '@/components/CameraFeed'
import LineChart from '@/components/LineChart'
import BoardStatusList from '@/components/BoardStatusList'
import PredictionLogs from '@/components/PredictionLogs'

const API = process.env.NEXT_PUBLIC_API_BASE_URL as string
const fetcher = (url: string) => axios.get(url).then(res => res.data)

interface SensorEntry {
  timestamp: string
  sensor_data: {
    temp: number
    humidity: number
    mq2: number
    flame: number
  }
}

interface ParsedSensorData {
  timestamp: string
  temperature: number
  humidity: number
  mq2: number
  flame: number
}

export default function DashboardPage() {
  const router = useRouter()
  const [isAuth, setIsAuth] = useState<boolean | null>(null)

  // 모든 훅은 무조건 최상단에서 호출
  const { data: fireStatus } = useSWR(`${API}/api/fire-status`, fetcher, { refreshInterval: 3000 })
  const { data: sensorData } = useSWR(`${API}/api/sensors`, fetcher, { refreshInterval: 3000 })
  const { data: imageData } = useSWR(`${API}/api/latest-image`, fetcher, { refreshInterval: 5000 })
  const { data: boardStatus } = useSWR(`${API}/api/board-status`, fetcher, { refreshInterval: 5000 })
  const { data: boardLogs } = useSWR(`${API}/api/board-latest-log`, fetcher, { refreshInterval: 5000 })
  const { data: graphData } = useSWR(`${API}/api/sensors/graph-data`, fetcher, { refreshInterval: 10000 })

  const [selectedBoard, setSelectedBoard] = useState('esp1')
  const [selectedMetric, setSelectedMetric] = useState('temperature')
  const [sensorHistory, setSensorHistory] = useState<ParsedSensorData[]>([])

  useEffect(() => {
    const auth = localStorage.getItem('auth')
    if (auth !== 'true') {
      router.push('/login')
    } else {
      setIsAuth(true)
    }
  }, [router])

  useEffect(() => {
    if (graphData && selectedBoard in graphData) {
      const parsed = (graphData[selectedBoard] as SensorEntry[]).map((entry) => ({
        timestamp: entry.timestamp,
        temperature: entry.sensor_data?.temp,
        humidity: entry.sensor_data?.humidity,
        mq2: entry.sensor_data?.mq2,
        flame: entry.sensor_data?.flame
      }))
      setSensorHistory(parsed)
    }
  }, [graphData, selectedBoard])

  // 인증 상태 확인 중이면 렌더링 보류
  if (isAuth === null) return null

  return (
    <Layout>
      <div className="flex flex-col xl:flex-row gap-6 px-6 pb-10 pt-6 min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-white transition-colors duration-500 ease-in-out">
        {/* 왼쪽 메인 컨텐츠 */}
        <div className="w-full xl:w-2/3 flex flex-col gap-6 transition-all duration-500 ease-in-out">
          <section className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-xl shadow transition-colors duration-500 ease-in-out">
            <h2 className="text-lg font-semibold mb-3 transition-colors duration-500">화재 상태</h2>
            <FireStatusCard fireStatus={fireStatus} />
          </section>

          <section className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-xl shadow transition-colors duration-500 ease-in-out">
            <h2 className="text-lg font-semibold mb-3 transition-colors duration-500">센서값</h2>
            <SensorStatusCard sensorData={sensorData} />
          </section>

          <section className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-xl shadow transition-colors duration-500 ease-in-out">
            <h2 className="text-lg font-semibold mb-3 transition-colors duration-500">실시간 카메라</h2>
            <CameraFeed streamUrl={`${API}/video_feed`} imageData={imageData || null} />
          </section>

          <section className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-xl shadow transition-colors duration-500 ease-in-out">
            <h2 className="text-lg font-semibold mb-3 transition-colors duration-500">센서 데이터 그래프</h2>
            <LineChart
              selectedBoard={selectedBoard}
              setSelectedBoard={setSelectedBoard}
              selectedMetric={selectedMetric}
              setSelectedMetric={setSelectedMetric}
              sensorHistory={sensorHistory}
            />
          </section>
        </div>

        {/* 오른쪽 사이드바 영역 */}
        <div className="w-full xl:w-1/3 flex flex-col gap-6 transition-all duration-500 ease-in-out">
          <section className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-xl shadow transition-colors duration-500 ease-in-out">
            <h2 className="text-lg font-semibold mb-3 transition-colors duration-500">보드 상태</h2>
            <BoardStatusList data={boardStatus || {}} />
          </section>

          <section className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-xl shadow transition-colors duration-500 ease-in-out">
            <h2 className="text-lg font-semibold mb-3 transition-colors duration-500">보드별 정보</h2>
            <PredictionLogs boardLogs={boardLogs || []} />
          </section>
        </div>
      </div>
    </Layout>
  )
}
