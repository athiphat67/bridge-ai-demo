import GrowthChart from '../components/GrowthChart'

export default function GrowthPredictionSection({ prediction }) {
  const mm5 = prediction.leg_length_diff_mm[prediction.leg_length_diff_mm.length - 1]
  const deg5 = prediction.angular_deg[prediction.angular_deg.length - 1]

  return (
    <div>
      {/* Section header */}
      <div className="mb-4 flex items-center gap-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-base dark:bg-med-indigo/20">📈</span>
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">ทำนายแนวโน้มการเจริญเติบโต 1 / 3 / 5 ปี</h3>
          <p className="text-xs text-slate-900">
            คาดการณ์ความต่างความยาวขาและมุมโก่งหากไม่ได้รับการรักษา
          </p>
        </div>
      </div>

      {/* Summary mini-cards */}
      <div className="mb-5 grid grid-cols-2 gap-3">
        <div className="rounded-lg border border-red-100 bg-red-50 p-3 dark:border-red-500/10 dark:bg-red-500/5">
          <p className="text-xs text-slate-900 dark:text-slate-400">ขาสั้นต่างกันสูงสุด (5 ปี)</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">~{mm5} mm</p>
        </div>
        <div className="rounded-lg border border-blue-100 bg-blue-50 p-3 dark:border-med-blue/20 dark:bg-med-blue/5">
          <p className="text-xs text-slate-900 dark:text-slate-400">มุมโก่งสูงสุด (5 ปี)</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">~{deg5}°</p>
        </div>
      </div>

      {/* Chart */}
      <GrowthChart prediction={prediction} />
    </div>
  )
}
