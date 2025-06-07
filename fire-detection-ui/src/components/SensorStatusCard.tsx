import React from 'react'

export default function SensorStatusCard({ sensorData }: { sensorData: any }) {
  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl shadow text-zinc-900 dark:text-white space-y-2 transition-colors duration-500">
      <div className="text-lg font-semibold transition-colors duration-500">센서 정보</div>
      {sensorData ? (
        <ul className="space-y-1 transition-colors duration-500">
          <li>온도: {sensorData.temp ?? 'N/A'}°C</li>
          <li>습도: {sensorData.humidity ?? 'N/A'}%</li>
          <li>가스(MQ2): {sensorData.mq2 ?? 'N/A'}</li>
          <li>불꽃 감지: {sensorData.flame === 1 ? '감지됨' : '정상'}</li>
          <li className="text-sm text-zinc-500 dark:text-zinc-400 mt-1 transition-colors duration-500">
            측정 시각: {sensorData.timestamp?.replace('T', ' ').slice(0, 19) ?? 'N/A'}
          </li>
        </ul>
      ) : (
        <p className="text-zinc-500 dark:text-zinc-400 transition-colors duration-500">데이터 없음</p>
      )}
    </div>
  )
}
