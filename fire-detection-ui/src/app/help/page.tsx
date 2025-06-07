'use client'

import Layout from '@/components/Layout'

export default function HelpPage() {
  return (
    <Layout>
      <div className="max-w-screen-md px-8 py-6 mx-auto text-black dark:text-white transition-colors duration-500">
        <h1 className="text-4xl font-extrabold mb-8 text-center tracking-tight">
          도움말 & 자주 묻는 질문
        </h1>

        <div className="bg-zinc-100 dark:bg-zinc-900 p-6 rounded-2xl shadow-xl space-y-8 transition-colors duration-500">
          {/* 시스템 개요 */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">이 시스템은 어떤 기능을 하나요?</h2>
            <p className="text-zinc-700 dark:text-zinc-300 leading-relaxed">
              이 시스템은 화재를 실시간으로 탐지하고, 센서 및 이미지 기반 데이터를 이용해 위험 여부를 판단합니다.
              대시보드에서는 화재 예측 결과, 센서 데이터, 스트리밍 영상 및 로그 등을 확인할 수 있습니다.
            </p>
          </section>

          {/* FAQ */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">자주 묻는 질문</h2>
            <ul className="space-y-5">
              <li>
                <p className="font-medium text-orange-500">Q. 실시간 카메라 영상이 보이지 않아요.</p>
                <p className="text-zinc-700 dark:text-zinc-300">
                  라즈베리파이 카메라 또는 스트리밍 서버가 꺼져있을 수 있습니다. 관리자에게 시스템 상태를 확인해 주세요.
                </p>
              </li>
              <li>
                <p className="font-medium text-orange-500">Q. 센서 데이터가 업데이트되지 않아요.</p>
                <p className="text-zinc-700 dark:text-zinc-300">
                  센서 보드와 서버 간의 네트워크 연결 상태를 확인하거나 보드의 전원을 재확인해 보세요.
                </p>
              </li>
              <li>
                <p className="font-medium text-orange-500">Q. 화재 알림 기준은 어떻게 되나요?</p>
                <p className="text-zinc-700 dark:text-zinc-300">
                  센서 예측 확률과 이미지 신뢰도가 일정 임계치를 넘으면 &quot;화재 발생&quot;으로 판단하고 알림을 보냅니다.
                </p>
              </li>
            </ul>
          </section>

          {/* 문의 */}
          <section>
            <h2 className="text-2xl font-semibold mb-2">문의</h2>
            <p className="text-zinc-700 dark:text-zinc-300">
              기타 문제가 발생하면 관리자에게 문의하세요: <span className="underline"></span>
            </p>
          </section>
        </div>
      </div>
    </Layout>
  )
}
