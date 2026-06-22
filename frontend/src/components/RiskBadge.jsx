/* Light base styles for badges */
const LIGHT = {
  Low:    'border-emerald-200 bg-emerald-50 text-emerald-700',
  Medium: 'border-amber-200 bg-amber-50 text-amber-700',
  High:   'border-red-200 bg-red-50 text-red-700 animate-pulse-glow',
}
/* Dark overrides applied via risk-* CSS class defined in index.css */
const DARK = { Low: 'risk-low', Medium: 'risk-med', High: 'risk-high' }
const ICON = { Low: '✅', Medium: '⚠️', High: '🚨' }
const EN = { Low: 'Low Risk', Medium: 'Moderate Risk', High: 'High Risk' }

export default function RiskBadge({ level }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-sm font-bold whitespace-nowrap ${LIGHT[level]} ${DARK[level]}`}
      style={{ minWidth: '120px', justifyContent: 'center', flexShrink: 0 }}
    >
      <span className="text-base leading-none">{ICON[level]}</span>
      {EN[level]}
    </span>
  )
}
