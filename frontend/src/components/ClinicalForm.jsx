const FIELD = 'mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none disabled:bg-slate-100'

export default function ClinicalForm({ value, onChange, disabled }) {
  const set = (k) => (e) => onChange({ ...value, [k]: e.target.value })
  const toggleSteroid = (e) =>
    onChange({ ...value, medical_history: e.target.checked ? 'corticosteroid' : '' })

  return (
    <div className="grid grid-cols-2 gap-3">
      <label className="text-xs text-slate-500">อายุจริง (ปี)
        <input type="number" className={FIELD} value={value.age_years}
               onChange={set('age_years')} disabled={disabled} />
      </label>
      <label className="text-xs text-slate-500">อายุกระดูก (ปี)
        <input type="number" className={FIELD} value={value.bone_age_years}
               onChange={set('bone_age_years')} disabled={disabled} />
      </label>
      <label className="text-xs text-slate-500">เพศ
        <select className={FIELD} value={value.gender} onChange={set('gender')} disabled={disabled}>
          <option value="male">ชาย</option>
          <option value="female">หญิง</option>
        </select>
      </label>
      <label className="text-xs text-slate-500">ตำแหน่ง Bar
        <select className={FIELD} value={value.location} onChange={set('location')} disabled={disabled}>
          <option value="medial">Medial (ด้านใน)</option>
          <option value="lateral">Lateral (ด้านนอก)</option>
        </select>
      </label>
      <label className="text-xs text-slate-500">น้ำหนัก (kg)
        <input type="number" className={FIELD} value={value.weight_kg}
               onChange={set('weight_kg')} disabled={disabled} />
      </label>
      <label className="text-xs text-slate-500">ส่วนสูง (cm)
        <input type="number" className={FIELD} value={value.height_cm}
               onChange={set('height_cm')} disabled={disabled} />
      </label>
      <label className="col-span-2 mt-1 flex items-center gap-2 text-sm text-slate-600">
        <input type="checkbox" checked={value.medical_history === 'corticosteroid'}
               onChange={toggleSteroid} disabled={disabled} />
        มีประวัติใช้ Corticosteroid
      </label>
    </div>
  )
}
