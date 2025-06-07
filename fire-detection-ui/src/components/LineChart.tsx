'use client'

import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import React from 'react'

interface ParsedSensorData {
  timestamp: string
  temperature: number
  humidity: number
  mq2: number
  flame: number
}

interface LineChartProps {
  selectedBoard: string
  setSelectedBoard: (boardId: string) => void
  selectedMetric: string
  setSelectedMetric: (metric: string) => void
  sensorHistory: ParsedSensorData[]
}

export default function LineChart({
  selectedBoard,
  setSelectedBoard,
  selectedMetric,
  setSelectedMetric,
  sensorHistory
}: LineChartProps) {
  const colorMap: Record<string, string> = {
    temperature: '#60a5fa',
    humidity: '#34d399',
    mq2: '#facc15',
    flame: '#f87171'
  }

  return (
    <div className="bg-white dark:bg-zinc-800 p-4 rounded-xl shadow-md text-zinc-900 dark:text-white transition-colors duration-500">
      <div className="flex flex-col md:flex-row gap-3 mb-4 items-start md:items-center justify-between">
        <div className="flex gap-3">
          <label className="text-sm font-medium transition-colors duration-500">
            보드 선택
            <select
              className="ml-2 bg-zinc-200 dark:bg-zinc-700 px-3 py-1 rounded text-zinc-900 dark:text-white transition-colors duration-500"
              value={selectedBoard}
              onChange={(e) => setSelectedBoard(e.target.value)}
            >
              <option value="esp1">ESP1</option>
              <option value="esp2">ESP2</option>
              <option value="esp3">ESP3</option>
            </select>
          </label>

          <label className="text-sm font-medium transition-colors duration-500">
            센서 선택
            <select
              className="ml-2 bg-zinc-200 dark:bg-zinc-700 px-3 py-1 rounded text-zinc-900 dark:text-white transition-colors duration-500"
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
            >
              <option value="temperature">온도</option>
              <option value="humidity">습도</option>
              <option value="mq2">가스 (MQ2)</option>
              <option value="flame">불꽃</option>
            </select>
          </label>
        </div>
      </div>

      {sensorHistory.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <ReLineChart
            data={sensorHistory}
            margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis
              dataKey="timestamp"
              tick={{ fill: '#8884d8', fontSize: 12 }}
              minTickGap={25}
            />
            <YAxis tick={{ fill: '#8884d8', fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: 'none' }}
              labelStyle={{ color: '#fff' }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend wrapperStyle={{ color: '#fff' }} />
            <Line
              type="monotone"
              dataKey={selectedMetric}
              stroke={colorMap[selectedMetric]}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </ReLineChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-zinc-400 dark:text-zinc-300 mt-4 transition-colors duration-500">
          그래프를 표시할 데이터가 없습니다.
        </p>
      )}
    </div>
  )
}
