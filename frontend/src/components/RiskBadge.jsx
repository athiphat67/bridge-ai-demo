const STYLE = {
  Low: 'bg-green-100 text-green-800 border-green-300',
  Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  High: 'bg-red-100 text-red-700 border-red-300',
}
const TH = { Low: 'ความเสี่ยงต่ำ', Medium: 'ความเสี่ยงปานกลาง', High: 'ความเสี่ยงสูง' }

export default function RiskBadge({ level }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-4 py-1 text-lg font-semibold ${STYLE[level]}`}>
      {TH[level]} · {level}
    </span>
  )
}
