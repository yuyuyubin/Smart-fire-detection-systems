'use client'

import Layout from '@/components/Layout'

export default function CameraPage() {
  return (
    <Layout>
      <div className="max-w-screen-xl px-8 py-6 mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">실시간 카메라 스트리밍</h1>
        <div className="bg-zinc-800 p-4 rounded-2xl shadow-xl">
          <div className="aspect-video bg-black rounded-md overflow-hidden">
            <iframe
              src={`${process.env.NEXT_PUBLIC_API_BASE_URL}/video_feed`}
              className="w-full h-full"
              title="Live Camera"
              allow="autoplay"
            ></iframe>
          </div>
        </div>
      </div>
    </Layout>
  )
}
