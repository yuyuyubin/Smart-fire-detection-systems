import React from 'react'

export default function FireStatusCard({ fireStatus }: { fireStatus: any }) {
  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl shadow text-zinc-900 dark:text-white space-y-2 transition-colors duration-500 ease-in-out">
      <div className="text-lg font-semibold transition-colors duration-500 ease-in-out">
        화재 상태
      </div>

      {fireStatus ? (
        <div className="space-y-1 transition-colors duration-500 ease-in-out">
          <p className="transition-colors duration-500 ease-in-out">
            센서 예측 확률:{' '}
            <span className="font-bold text-orange-400 transition-colors duration-500 ease-in-out">
              {fireStatus.sensor_fire_probability?.toFixed(1)}%
            </span>
          </p>
          <p className="transition-colors duration-500 ease-in-out">
            이미지 예측 확률:{' '}
            <span className="font-bold text-orange-400 transition-colors duration-500 ease-in-out">
              {fireStatus.image_fire_confidence?.toFixed(1)}%
            </span>
          </p>
          <p className="transition-colors duration-500 ease-in-out">
            화재 감지 여부:{' '}
            <span
              className={`font-semibold transition-colors duration-500 ease-in-out ${
                fireStatus.fire_detected ? 'text-red-400' : 'text-green-400'
              }`}
            >
              {fireStatus.fire_detected ? '화재 발생' : '정상'}
            </span>
          </p>
        </div>
      ) : (
        <p className="text-zinc-500 dark:text-zinc-400 transition-colors duration-500 ease-in-out">
          데이터 없음
        </p>
      )}
    </div>
  )
}
