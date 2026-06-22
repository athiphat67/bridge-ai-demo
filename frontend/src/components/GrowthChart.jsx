import {
  Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer,
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
    year: `${y} yr`,
    'Leg Length Discrepancy (mm)': prediction.leg_length_diff_mm[i],
    'Angular Deformity (°)': prediction.angular_deg[i],
  }))

  // Check if dark mode is active for dynamic styling
  const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const axisColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
  const tickColor = isDark ? '#94a3b8' : '#64748b'

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorRed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorBlue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
        <XAxis dataKey="year" tick={{ fill: tickColor, fontSize: 12 }} axisLine={{ stroke: axisColor }} />
        <YAxis yAxisId="left" tick={{ fill: tickColor, fontSize: 12 }} axisLine={{ stroke: axisColor }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: tickColor, fontSize: 12 }} axisLine={{ stroke: axisColor }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ color: tickColor, fontSize: 12, paddingTop: 8 }} />
        <Area yAxisId="left" type="monotone" dataKey="Leg Length Discrepancy (mm)"
              stroke="#ef4444" fillOpacity={1} fill="url(#colorRed)" strokeWidth={2.5} dot={{ fill: '#ef4444', r: 4 }} activeDot={{ r: 6, fill: '#ef4444', stroke: 'rgba(239,68,68,0.3)', strokeWidth: 6 }} />
        <Area yAxisId="right" type="monotone" dataKey="Angular Deformity (°)"
              stroke="#3b82f6" fillOpacity={1} fill="url(#colorBlue)" strokeWidth={2.5} dot={{ fill: '#3b82f6', r: 4 }} activeDot={{ r: 6, fill: '#3b82f6', stroke: 'rgba(59,130,246,0.3)', strokeWidth: 6 }} />
      </AreaChart>
    </ResponsiveContainer>
  )
}
