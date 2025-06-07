import React from 'react'

interface BoardStatus {
  board_id: string
  ip_address: string
  timestamp: string
}

export default function BoardStatusList({ data }: { data: Record<string, BoardStatus> }) {
  const boardEntries = Object.entries(data || {})

  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl shadow text-zinc-900 dark:text-white transition-colors duration-500 ease-in-out">
      <h3 className="text-lg font-semibold mb-3">보드 상태</h3>
      {boardEntries.length > 0 ? (
        boardEntries.map(([boardId, board]) => (
          <div key={boardId} className="mb-4 border-b border-zinc-300 dark:border-zinc-700 pb-3 transition-colors duration-500">
            <p className="font-semibold">
              {board.board_id}{' '}
              <span className="text-zinc-500 dark:text-zinc-400">(IP: {board.ip_address || '-'})</span>
            </p>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
              ⏱️ 마지막 접속: {board.timestamp || '-'}
            </p>
          </div>
        ))
      ) : (
        <p className="text-zinc-500 dark:text-zinc-400">현재 접속된 보드가 없습니다.</p>
      )}
    </div>
  )
}
