const COLOR = { high: 'text-red-600', medium: 'text-amber-600', low: 'text-slate-400' }
const TH = { high: 'ผลสูง', medium: 'ผลปานกลาง', low: 'ผลต่ำ' }

export default function FactorList({ factors }) {
  return (
    <ul className="space-y-1">
      {factors.map((f, i) => (
        <li key={i} className="flex items-center justify-between text-sm">
          <span className="text-slate-700">{f.label}</span>
          <span className={`font-medium ${COLOR[f.impact]}`}>{TH[f.impact]}</span>
        </li>
      ))}
    </ul>
  )
}
