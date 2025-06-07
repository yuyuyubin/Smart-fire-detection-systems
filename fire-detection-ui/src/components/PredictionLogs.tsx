interface BoardLog {
  board_id: string
  sensor_fire_probability: number | null
  image_fire_confidence: number | null
  final_score: number | null
  fire_detected: boolean
  timestamp: string
}

interface PredictionLogsProps {
  boardLogs: BoardLog[]
}

export default function PredictionLogs({ boardLogs }: PredictionLogsProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl shadow text-zinc-900 dark:text-white space-y-2 transition-colors duration-500">
      <div className="text-lg font-semibold transition-colors duration-500">보드별 최신 예측</div>

      {boardLogs.length > 0 ? (
        boardLogs.map((log) => (
          <div
            key={log.board_id}
            className="text-sm border-b border-zinc-200 dark:border-zinc-700 pb-3 mb-3 transition-colors duration-500"
          >
            <p>
              보드: <span className="text-orange-500">{log.board_id}</span>
            </p>
            <p>
              센서 화재 확률:{' '}
              <span className="text-orange-500">
                {(log.sensor_fire_probability ?? 0).toFixed(1)}%
              </span>
            </p>
            <p>
              이미지 신뢰도:{' '}
              <span className="text-orange-500">
                {(log.image_fire_confidence ?? 0).toFixed(1)}%
              </span>
            </p>
            <p>
              최종 점수:{' '}
              <span className="text-orange-500">
                {(log.final_score ?? 0).toFixed(1)}%
              </span>
            </p>
            <p>
              화재 여부:{' '}
              <span
                className={`font-bold ${
                  log.fire_detected ? 'text-red-500' : 'text-green-500'
                }`}
              >
                {log.fire_detected ? '🔥 화재 발생' : '✅ 정상'}
              </span>
            </p>
            <p className="text-zinc-500 dark:text-zinc-400 mt-1">
              ⏱️ {log.timestamp}
            </p>
          </div>
        ))
      ) : (
        <p className="text-zinc-500 dark:text-zinc-400">예측 데이터 없음</p>
      )}
    </div>
  )
}
