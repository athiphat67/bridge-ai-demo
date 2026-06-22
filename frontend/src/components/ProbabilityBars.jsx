/**
 * กราฟความน่าจะเป็น — แท่งแนวนอน 3 รูปแบบ (รวม = 100%)
 *   ขาโก่งออก (Varus) · ขาฉิ่งเข้า (Valgus) · หยุดโต (Arrest)
 */
const ROWS = [
  { key: 'varus_percent',  label: 'Bow-legged',     sub: 'Varus',  color: '#f59e0b', icon: '⟨ ⟩' },
  { key: 'valgus_percent', label: 'Knock-kneed',    sub: 'Valgus', color: '#3b82f6', icon: '⟩ ⟨' },
  { key: 'arrest_percent', label: 'Growth Arrest',  sub: 'Arrest', color: '#ef4444', icon: '⊘' },
]

export default function ProbabilityBars({ probabilities }) {
  if (!probabilities) return null
  // แถวที่มีค่าสูงสุด = ผลลัพธ์ที่น่าจะเกิดมากที่สุด (เน้นไฮไลต์)
  const top = ROWS.reduce((a, b) =>
    probabilities[b.key] > probabilities[a.key] ? b : a)

  return (
    <div className="space-y-3">
      {ROWS.map((r) => {
        const v = probabilities[r.key] ?? 0
        const isTop = r.key === top.key
        return (
          <div key={r.key}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="flex items-center gap-2 text-slate-900 dark:text-slate-300">
                <span className="font-mono" style={{ color: r.color }}>{r.icon}</span>
                <span className={isTop ? 'font-bold' : 'font-medium'}>{r.label}</span>
                <span className="text-slate-400">{r.sub}</span>
              </span>
              <span className="font-bold tabular-nums" style={{ color: r.color }}>
                {v.toFixed(1)}%
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700/60">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(100, v)}%`,
                  backgroundColor: r.color,
                  opacity: isTop ? 1 : 0.55,
                }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
