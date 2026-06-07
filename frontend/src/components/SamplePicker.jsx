export default function SamplePicker({ samples, selectedId, onSelect }) {
  return (
    <div className="space-y-2">
      {samples.map((s) => (
        <button
          key={s.id}
          type="button"
          onClick={() => onSelect(s.id)}
          className={`w-full rounded-lg border p-3 text-left text-sm transition ${
            selectedId === s.id
              ? 'border-blue-500 bg-blue-50 font-medium'
              : 'border-slate-200 hover:border-slate-300'
          }`}
        >
          {s.display_name}
        </button>
      ))}
    </div>
  )
}
