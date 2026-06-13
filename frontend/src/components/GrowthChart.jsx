import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-lg p-3 text-xs">
      <p className="mb-1 font-semibold text-slate-900 dark:text-slate-200">{label}</p>
      {payload.map((item, i) => (
        <p key={i} style={{ color: item.stroke }} className="flex justify-between gap-4">
          <span className="text-slate-900 dark:text-slate-400">{item.name}</span>
          <span className="font-medium">{item.value}</span>
        </p>
      ))}
    </div>
  )
}

export default function GrowthChart({ prediction }) {
  const data = prediction.years.map((y, i) => ({
    year: `${y} ปี`,
    'ขาสั้นต่างกัน (mm)': prediction.leg_length_diff_mm[i],
    'มุมโก่ง (°)': prediction.angular_deg[i],
  }))

  // Check if dark mode is active for dynamic styling
  const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const axisColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
  const tickColor = isDark ? '#94a3b8' : '#64748b'

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
        <XAxis dataKey="year" tick={{ fill: tickColor, fontSize: 12 }} axisLine={{ stroke: axisColor }} />
        <YAxis yAxisId="left" tick={{ fill: tickColor, fontSize: 12 }} axisLine={{ stroke: axisColor }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: tickColor, fontSize: 12 }} axisLine={{ stroke: axisColor }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ color: tickColor, fontSize: 12, paddingTop: 8 }} />
        <Line yAxisId="left" type="monotone" dataKey="ขาสั้นต่างกัน (mm)"
              stroke="#ef4444" strokeWidth={2.5} dot={{ fill: '#ef4444', r: 4 }} activeDot={{ r: 6, fill: '#ef4444', stroke: 'rgba(239,68,68,0.3)', strokeWidth: 6 }} />
        <Line yAxisId="right" type="monotone" dataKey="มุมโก่ง (°)"
              stroke="#3b82f6" strokeWidth={2.5} dot={{ fill: '#3b82f6', r: 4 }} activeDot={{ r: 6, fill: '#3b82f6', stroke: 'rgba(59,130,246,0.3)', strokeWidth: 6 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
