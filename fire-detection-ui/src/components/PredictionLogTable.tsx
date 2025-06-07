// components/PredictionLogTable.tsx
interface PredictionLogsProps {
  logs: any[];
}

export default function PredictionLogTable({ logs }: PredictionLogsProps) {
  if (!logs || logs.length === 0) {
    return (
      <div className="bg-zinc-800 p-4 rounded text-white">
        <h3 className="text-lg font-semibold mb-2">예측 로그</h3>
        <p className="text-zinc-400">예측 로그 데이터가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-800 p-4 rounded text-white overflow-x-auto">
      <h3 className="text-lg font-semibold mb-2">예측 로그</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-600">
            <th className="py-1 px-2 text-left">시간</th>
            <th className="py-1 px-2 text-left">보드</th>
            <th className="py-1 px-2 text-left">센서 화재확률</th>
            <th className="py-1 px-2 text-left">이미지 신뢰도</th>
            <th className="py-1 px-2 text-left">최종 점수</th>
            <th className="py-1 px-2 text-left">결과</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, index) => (
            <tr key={index} className="border-b border-zinc-700">
              <td className="py-1 px-2">{log.timestamp}</td>
              <td className="py-1 px-2">{log.board_id}</td>
              <td className="py-1 px-2">{log.sensor_fire_probability}%</td>
              <td className="py-1 px-2">{log.image_fire_confidence}%</td>
              <td className="py-1 px-2">{log.final_score}%</td>
              <td className="py-1 px-2">
                {log.fire_detected ? '화재' : '정상'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
