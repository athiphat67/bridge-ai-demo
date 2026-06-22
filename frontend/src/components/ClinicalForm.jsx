export default function ClinicalForm({ value, onChange, disabled }) {
  const set = (k) => (e) => onChange({ ...value, [k]: e.target.value })
  const toggleSteroid = (e) =>
    onChange({ ...value, medical_history: e.target.checked ? 'corticosteroid' : '' })

  return (
    <div className="grid grid-cols-2 gap-3">
      <label className="space-y-1">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-900 dark:text-slate-400">
          <span className="text-sm">📅</span> Chronological Age (yrs)
        </span>
        <input type="number" className="glass-input w-full rounded-lg px-3 py-2 text-sm"
               value={value.age_years} onChange={set('age_years')} disabled={disabled} />
      </label>
      <label className="space-y-1">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-900 dark:text-slate-400">
          <span className="text-sm">🦴</span> Bone Age (yrs)
        </span>
        <input type="number" className="glass-input w-full rounded-lg px-3 py-2 text-sm"
               value={value.bone_age_years} onChange={set('bone_age_years')} disabled={disabled} />
      </label>
      <label className="space-y-1">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-900 dark:text-slate-400">
          <span className="text-sm">👤</span> Sex
        </span>
        <select className="glass-input w-full rounded-lg px-3 py-2 text-sm"
                value={value.gender} onChange={set('gender')} disabled={disabled}>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </label>
      <label className="space-y-1">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-900 dark:text-slate-400">
          <span className="text-sm">📍</span> Bar Location
        </span>
        <select className="glass-input w-full rounded-lg px-3 py-2 text-sm"
                value={value.location} onChange={set('location')} disabled={disabled}>
          <option value="medial">Medial (inner)</option>
          <option value="lateral">Lateral (outer)</option>
        </select>
      </label>
      <label className="space-y-1">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-900 dark:text-slate-400">
          <span className="text-sm">⚖️</span> Weight (kg)
        </span>
        <input type="number" className="glass-input w-full rounded-lg px-3 py-2 text-sm"
               value={value.weight_kg} onChange={set('weight_kg')} disabled={disabled} />
      </label>
      <label className="space-y-1">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-900 dark:text-slate-400">
          <span className="text-sm">📏</span> Height (cm)
        </span>
        <input type="number" className="glass-input w-full rounded-lg px-3 py-2 text-sm"
               value={value.height_cm} onChange={set('height_cm')} disabled={disabled} />
      </label>
      <label className="col-span-2 mt-1 flex cursor-pointer items-center gap-2.5 rounded-lg border border-slate-100 bg-slate-50 p-2.5 text-sm text-slate-900 transition hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-700/50 dark:text-slate-300 dark:hover:bg-slate-700">
        <input type="checkbox" checked={value.medical_history === 'corticosteroid'}
               onChange={toggleSteroid} disabled={disabled}
               className="h-4 w-4 rounded border-slate-300 text-med-blue focus:ring-med-blue/30 dark:border-white/20 dark:bg-navy-800" />
        💊 History of Corticosteroid Use
      </label>
    </div>
  )
}
