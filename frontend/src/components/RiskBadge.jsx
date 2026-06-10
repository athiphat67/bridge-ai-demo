/* Light base styles for badges */
const LIGHT = {
  Low:    'border-emerald-200 bg-emerald-50 text-emerald-700',
  Medium: 'border-amber-200 bg-amber-50 text-amber-700',
  High:   'border-red-200 bg-red-50 text-red-700 animate-pulse-glow',
}
/* Dark overrides applied via risk-* CSS class defined in index.css */
const DARK = { Low: 'risk-low', Medium: 'risk-med', High: 'risk-high' }
const ICON = { Low: '✅', Medium: '⚠️', High: '🚨' }
const TH = { Low: 'ความเสี่ยงต่ำ', Medium: 'ความเสี่ยงปานกลาง', High: 'ความเสี่ยงระดับสูง' }

export default function RiskBadge({ level }) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-xl border px-5 py-2 text-lg font-semibold ${LIGHT[level]} ${DARK[level]}`}>
      <span className="text-xl">{ICON[level]}</span>
      {TH[level]} · {level} Risk
    </span>
  )
}
