import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'

export default function GrowthChart({ prediction }) {
  const data = prediction.years.map((y, i) => ({
    year: `${y} ปี`,
    'ขาสั้นต่างกัน (mm)': prediction.leg_length_diff_mm[i],
    'มุมโก่ง (°)': prediction.angular_deg[i],
  }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="year" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <Line yAxisId="left" type="monotone" dataKey="ขาสั้นต่างกัน (mm)"
              stroke="#dc2626" strokeWidth={2} />
        <Line yAxisId="right" type="monotone" dataKey="มุมโก่ง (°)"
              stroke="#2563eb" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}
