const BAR_COLOR = {
  high: 'bg-red-500',
  medium: 'bg-amber-500',
  low: 'bg-slate-400',
}
const BAR_WIDTH = { high: 'w-full', medium: 'w-2/3', low: 'w-1/3' }
const DOT_COLOR = {
  high: 'bg-red-500 dark:bg-red-400',
  medium: 'bg-amber-500 dark:bg-amber-400',
  low: 'bg-slate-300 dark:bg-slate-500',
}
const TH = { high: 'ผลสูง 100%', medium: 'ผลปานกลาง 66%', low: 'ผลต่ำ 33%' }

export default function FactorList({ factors }) {
  return (
    <ul className="flex h-full flex-col gap-4">
      {factors.map((f, i) => (
        <li key={i} className="flex flex-1 flex-col justify-center rounded-lg border border-slate-100 bg-white p-4 transition hover:shadow-card dark:border-slate-600 dark:bg-slate-700/50 dark:hover:bg-slate-700">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="flex items-center gap-2 text-slate-900 dark:text-slate-200">
              <span className={`h-2 w-2 rounded-full ${DOT_COLOR[f.impact]}`} />
              {f.label}
            </span>
            <span className={`text-xs font-medium ${
              f.impact === 'high' ? 'text-red-600 dark:text-red-400'
              : f.impact === 'medium' ? 'text-amber-600 dark:text-amber-400'
              : 'text-slate-900 dark:text-slate-500'
            }`}>
              {TH[f.impact]}
            </span>
          </div>
          <div className="mt-2 h-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
            <div className={`h-full rounded-full ${BAR_COLOR[f.impact]} ${BAR_WIDTH[f.impact]} transition-all duration-700`} />
          </div>
        </li>
      ))}
    </ul>
  )
}
