'use client'

import Layout from '@/components/Layout'

export default function CameraPage() {
  return (
    <Layout>
      <div className="max-w-screen-xl px-6 py-8 mx-auto transition-colors duration-500 ease-in-out text-zinc-900 dark:text-white">
        <h1 className="text-3xl font-bold mb-4 transition-colors duration-500">
          실시간 화재 감지 카메라
        </h1>
        <p className="mb-6 text-zinc-600 dark:text-zinc-400 transition-colors duration-500">
          아래 스트리밍 화면은 라즈베리파이 카메라를 통해 실시간으로 전송되는 영상을 보여줍니다. 화재가 감지되면 자동으로 서버에 감지 이미지가 저장됩니다.
        </p>

        <div className="bg-zinc-100 dark:bg-zinc-900 p-5 rounded-2xl shadow-xl transition-colors duration-500 ease-in-out">
          <div className="aspect-video bg-black rounded-lg overflow-hidden border border-zinc-700">
            <iframe
              src={`${process.env.NEXT_PUBLIC_API_BASE_URL}/video_feed`}
              className="w-full h-full"
              title="Live Fire Detection Camera"
              allow="autoplay"
            ></iframe>
          </div>
        </div>
      </div>
    </Layout>
  )
}
