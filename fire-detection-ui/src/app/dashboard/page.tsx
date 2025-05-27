'use client'
import Layout from "@/components/Layout"

export default function DashboardPage() {
  return (
    <Layout>
      <div className="text-xl font-bold mb-4">📊 실시간 화재 감지 시스템</div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 🔥 화재 상태 카드 */}
        <div className="bg-zinc-800 p-4 rounded-xl shadow w-full">
          <div className="text-lg font-semibold mb-2">🔥 화재 상태</div>
          <p>
            현재 화재 발생 확률:{" "}
            <span className="text-orange-400 font-bold">41.2%</span>
          </p>
        </div>

        {/* 🧪 센서 정보 카드 */}
        <div className="bg-zinc-800 p-4 rounded-xl shadow w-full">
          <div className="text-lg font-semibold mb-2">🧪 센서 정보</div>
          <ul className="text-sm space-y-1">
            <li>온도: 29.3°C</li>
            <li>가스: 180ppm</li>
            <li>불꽃 감지: Yes</li>
          </ul>
        </div>

        {/* 📸 실시간 이미지 뷰 */}
        <div className="md:col-span-2 bg-zinc-800 p-4 rounded-xl shadow w-full">
          <div className="text-lg font-semibold mb-2">📸 실시간 카메라</div>
          <div className="bg-zinc-900 aspect-video w-full flex items-center justify-center text-zinc-500 rounded-md">
            [이미지 영역]
          </div>
        </div>
      </div>
    </Layout>
  )
}
