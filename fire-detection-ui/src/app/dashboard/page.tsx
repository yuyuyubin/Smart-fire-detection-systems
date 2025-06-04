'use client'

import useSWR from 'swr'
import axios from 'axios'
import Layout from '@/components/Layout'

const API = process.env.NEXT_PUBLIC_API_BASE_URL
const fetcher = (url: string) => axios.get(url).then(res => res.data)

export default function DashboardPage() {
  const { data: fireStatus, error: fireError, isLoading: fireLoading } = useSWR(
    `${API}/api/fire-status`, fetcher, { refreshInterval: 3000 }
  )

  const { data: sensorData, error: sensorError, isLoading: sensorLoading } = useSWR(
    `${API}/api/sensors`, fetcher, { refreshInterval: 3000 }
  )

  const { data: imageData, error: imageError, isLoading: imageLoading } = useSWR(
    `${API}/api/latest-image`, fetcher, { refreshInterval: 5000 }
  )

  return (
    <Layout>
      {/* 제목 */}
      <div className="text-xl font-semibold text-white max-w-screen-lg ml-8 px-5 mb-4 ">
        실시간 화재 감지 시스템
      </div>

      {/* 전체 콘텐츠 */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 max-w-screen-lg ml-7 px-4">

        {/* 왼쪽 영역 */}
        <div className="xl:col-span-8 space-y-4">
          {/* 화재 상태 */}
          <div className="bg-zinc-800 p-5 rounded-2xl shadow-md space-y-2">
            <div className="text-lg font-semibold text-white">화재 상태</div>
            {fireError ? (
              <p className="text-red-400 text-base">서버 연결 실패</p>
            ) : fireLoading ? (
              <p className="text-zinc-400 text-base">불러오는 중...</p>
            ) : fireStatus && fireStatus.probability !== undefined ? (
              <div className="text-base text-white space-y-1">
                <p>예측 확률: <span className="font-bold text-orange-400">{fireStatus.probability.toFixed(1)}%</span></p>
                <p>판단 상태: <span className="font-semibold capitalize">{fireStatus.status}</span></p>
              </div>
            ) : (
              <p className="text-zinc-400 text-base">데이터 없음</p>
            )}
          </div>

          {/* 센서 정보 */}
          <div className="bg-zinc-800 p-5 rounded-2xl shadow-md space-y-2">
            <div className="text-lg font-semibold text-white">센서 정보</div>
            {sensorError ? (
              <p className="text-red-400 text-base">센서 데이터 불러오기 실패</p>
            ) : sensorLoading ? (
              <p className="text-zinc-400 text-base">불러오는 중...</p>
            ) : sensorData ? (
              <ul className="text-base text-white space-y-1">
                <li>온도: <span className="font-medium">{sensorData.temperature ?? 'N/A'}°C</span></li>
                <li>습도: <span className="font-medium">{sensorData.humidity ?? 'N/A'}%</span></li>
                <li>가스(MQ2): <span className="font-medium">{sensorData.mq2 ?? 'N/A'}</span></li>
                <li>불꽃 감지: <span className="font-medium">{sensorData.flame === 1 ? '감지됨' : '정상'}</span></li>
                <li className="text-sm text-zinc-400 mt-1">
                  측정 시각: {sensorData.timestamp?.replace('T', ' ').slice(0, 19) ?? 'N/A'}
                </li>
              </ul>
            ) : (
              <p className="text-zinc-400 text-base">데이터 없음</p>
            )}
          </div>

          {/* 실시간 감지 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 영상 */}
            <div className="bg-zinc-800 p-4 rounded-2xl shadow-md">
              <div className="text-base font-semibold text-white mb-2">실시간 감지 영상</div>
              <div className="aspect-video bg-black rounded-md overflow-hidden">
                <iframe
                  src={`${API}/video_feed`}
                  className="w-full h-full max-w-full"
                  title="Live Stream"
                  allow="autoplay"
                ></iframe>
              </div>
            </div>

            {/* 이미지 */}
            <div className="bg-zinc-800 p-4 rounded-2xl shadow-md">
              <div className="text-base font-semibold text-white mb-2">최신 감지 이미지</div>
              {imageError ? (
                <p className="text-red-400 text-base">이미지 로딩 실패</p>
              ) : imageLoading ? (
                <p className="text-zinc-400 text-base">이미지 불러오는 중...</p>
              ) : imageData?.image_url ? (
                <img
                  src={`${API}${imageData.image_url}`}
                  alt="Latest detection"
                  className="w-full max-w-full max-h-[300px] object-contain rounded-md border border-zinc-700"
                />
              ) : (
                <p className="text-zinc-400 text-base">이미지가 아직 없습니다</p>
              )}
            </div>
          </div>
        </div>

        {/* 우측 요약 */}
        <div className="xl:col-span-4 space-y-4">
          <div className="bg-zinc-800 p-5 rounded-2xl shadow-md text-white space-y-3">
            <div className="text-lg font-semibold">시스템 요약</div>
            <div className="space-y-1 text-sm text-zinc-300">
              <div>
                <div className="text-zinc-400">API 연결</div>
                <div className="font-medium text-white">정상</div>
              </div>
              <div>
                <div className="text-zinc-400">모델 버전</div>
                <div className="font-medium text-white">v1.0.2</div>
              </div>
              <div className="border-t border-zinc-700 pt-2">
                <div className="text-zinc-400">최근 화재</div>
                <div className="font-medium text-white">없음</div>
              </div>
              <div>
                <div className="text-zinc-400">모델 상태</div>
                <div className="font-medium text-white">안정화됨</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
