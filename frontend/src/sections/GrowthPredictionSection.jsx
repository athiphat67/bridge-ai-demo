import GrowthChart from '../components/GrowthChart'

export default function GrowthPredictionSection({ prediction }) {
  const mm5 = prediction.leg_length_diff_mm[prediction.leg_length_diff_mm.length - 1]
  return (
    <div>
      <h3 className="text-lg font-semibold">Growth Prediction — แนวโน้ม 1 / 3 / 5 ปี</h3>
      <p className="mb-4 text-sm text-slate-500">
        คาดการณ์ความต่างความยาวขาและมุมโก่งหากไม่ได้รับการรักษา (สูงสุด ~{mm5} mm ใน 5 ปี)
      </p>
      <GrowthChart prediction={prediction} />
    </div>
  )
}
