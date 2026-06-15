import GrowthChart from '../components/GrowthChart'
import ProbabilityBars from '../components/ProbabilityBars'

export default function GrowthPredictionSection({ prediction }) {
  const mm5 = prediction.leg_length_diff_mm[prediction.leg_length_diff_mm.length - 1]
  const deg5 = prediction.angular_deg[prediction.angular_deg.length - 1]
  const remaining = prediction.remaining_growth_percent
  const normalRemaining = prediction.normal_remaining_percent
  // สัดส่วนศักยภาพที่เหลือเทียบเด็กปกติ (ใช้เติมวงแหวน gauge)
  const vsNormal = normalRemaining > 0
    ? Math.round((remaining / normalRemaining) * 100)
    : 0

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

      {/* Remaining Growth Potential — ศักยภาพการเติบโตที่เหลือ เทียบเด็กปกติ */}
      <div className="mb-5 rounded-xl border border-teal-100 bg-teal-50/60 p-4 dark:border-med-teal/20 dark:bg-med-teal/5">
        <p className="mb-3 text-xs font-medium uppercase tracking-wider text-teal-700 dark:text-med-teal">
          ศักยภาพการเติบโตที่เหลือ (Remaining Growth Potential)
        </p>
        <div className="flex items-center gap-5">
          {/* Donut gauge */}
          <RemainingGauge value={remaining} vsNormal={vsNormal} />
          <div className="flex-1 space-y-2 text-sm">
            <p className="text-slate-900 dark:text-slate-300">
              กระดูกฝั่งที่บาดเจ็บยังมีศักยภาพยืดยาวได้อีก
              <span className="ml-1 text-xl font-bold text-teal-600 dark:text-med-teal">{remaining}%</span>
            </p>
            <p className="text-xs text-slate-900 dark:text-slate-400">
              เทียบเด็กปกติวัยเดียวกัน (ยังเหลือ {normalRemaining}%) → คิดเป็น
              <span className="font-semibold text-teal-700 dark:text-med-teal"> {vsNormal}%</span> ของศักยภาพปกติ
            </p>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div className="h-full rounded-full bg-teal-500 transition-all duration-700"
                   style={{ width: `${Math.min(100, vsNormal)}%` }} />
            </div>
          </div>
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

      {/* กราฟความน่าจะเป็น 3 รูปแบบ */}
      <div className="mt-6">
        <div className="mb-3 flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-50 text-sm dark:bg-amber-500/20">📊</span>
          <div>
            <h4 className="font-semibold text-slate-900 dark:text-slate-200">โอกาสเกิดความผิดปกติ</h4>
            <p className="text-xs text-slate-900 dark:text-slate-400">แบ่งความน่าจะเป็นออกเป็น 3 รูปแบบ (รวม 100%)</p>
          </div>
        </div>
        <ProbabilityBars probabilities={prediction.probabilities} />
      </div>
    </div>
  )
}

/** เกจโดนัทแสดง % ศักยภาพที่เหลือเทียบเด็กปกติ */
function RemainingGauge({ value, vsNormal }) {
  const r = 32, c = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(100, vsNormal))
  const dash = (pct / 100) * c
  return (
    <div className="relative h-24 w-24 shrink-0">
      <svg viewBox="0 0 80 80" className="h-24 w-24 -rotate-90">
        <circle cx="40" cy="40" r={r} fill="none" strokeWidth="9"
                className="stroke-slate-200 dark:stroke-slate-700" />
        <circle cx="40" cy="40" r={r} fill="none" strokeWidth="9"
                stroke="#14b8a6" strokeLinecap="round"
                strokeDasharray={`${dash} ${c}`}
                className="transition-all duration-700" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold text-teal-600 dark:text-med-teal">{value}%</span>
        <span className="text-[10px] text-slate-500 dark:text-slate-400">เหลืออยู่</span>
      </div>
    </div>
  )
}
