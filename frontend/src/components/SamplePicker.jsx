const RISK_ICON = {
  normal: '✅', case_normal: '✅',
  low: '🟢', case_low: '🟢',
  medium: '🟡', case_medium: '🟡',
  high: '🔴', case_high: '🔴',
}

function getIcon(id) {
  if (!id) return '🔬'
  const lower = id.toLowerCase()
  for (const [key, icon] of Object.entries(RISK_ICON)) {
    if (lower.includes(key)) return icon
  }
  return '🔬'
}

export default function SamplePicker({ samples, selectedId, onSelect }) {
  return (
    <div className="space-y-2">
      {samples.map((s) => (
        <button
          key={s.id}
          type="button"
          onClick={() => onSelect(s.id)}
          className={`group flex w-full items-center gap-3 rounded-xl p-3 text-left text-sm transition-all duration-300 ${
            selectedId === s.id
              ? 'border border-med-blue/40 bg-blue-50 shadow-md dark:border-blue-500 dark:bg-blue-950/50 dark:shadow-glow-blue'
              : 'border border-slate-100 bg-white hover:border-slate-200 hover:shadow-card dark:border-slate-600 dark:bg-slate-700/50 dark:hover:border-slate-500 dark:hover:bg-slate-700'
          }`}
        >
          <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-base transition-transform duration-300 group-hover:scale-110 ${
            selectedId === s.id ? 'bg-blue-100 dark:bg-blue-900/50' : 'bg-slate-50 dark:bg-slate-700'
          }`}>
            {getIcon(s.id)}
          </span>
          <span className={`${selectedId === s.id ? 'font-medium text-blue-700 dark:text-slate-100' : 'text-slate-900 dark:text-slate-300'}`}>
            {s.display_name}
          </span>
        </button>
      ))}
    </div>
  )
}
