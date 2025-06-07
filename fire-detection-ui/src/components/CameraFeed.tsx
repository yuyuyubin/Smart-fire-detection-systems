'use client'

import Image from 'next/image'

interface CameraFeedProps {
  imageData: {
    image_url?: string
  } | null
  streamUrl: string
}

export default function CameraFeed({ imageData, streamUrl }: CameraFeedProps) {
  const imageUrl =
    imageData?.image_url && process.env.NEXT_PUBLIC_API_BASE_URL
      ? `${process.env.NEXT_PUBLIC_API_BASE_URL}${imageData.image_url}`
      : null

  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl shadow text-zinc-900 dark:text-white transition-colors duration-500 ease-in-out">
      <h3 className="text-lg font-semibold mb-4">실시간 감지 영상</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 실시간 스트리밍 */}
        <div>
          <h4 className="text-sm mb-2 text-zinc-500 dark:text-zinc-300 transition-colors duration-500">실시간 스트리밍</h4>
          <iframe
            src={streamUrl}
            width="100%"
            height="300"
            className="rounded border border-zinc-300 dark:border-zinc-700 transition-colors duration-500"
          />
        </div>

        {/* 최신 감지 이미지 */}
        <div>
          <h4 className="text-sm mb-2 text-zinc-500 dark:text-zinc-300 transition-colors duration-500">최신 감지 이미지</h4>
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt="Latest Detected"
              width={640}
              height={360}
              unoptimized
              className="w-full h-[300px] object-contain rounded border border-zinc-300 dark:border-zinc-700 transition-colors duration-500"
            />
          ) : (
            <p className="text-zinc-500 dark:text-zinc-400 transition-colors duration-500">이미지 없음</p>
          )}
        </div>
      </div>
    </div>
  )
}
