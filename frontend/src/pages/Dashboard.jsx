import { useEffect, useState } from 'react'
import { analyze, getSamples } from '../api/client'
import ClinicalForm from '../components/ClinicalForm'
import SamplePicker from '../components/SamplePicker'
import AnalysisSection from '../sections/AnalysisSection'
import GrowthPredictionSection from '../sections/GrowthPredictionSection'

const DEFAULT_CLINICAL = {
  age_years: 8, bone_age_years: 8, gender: 'male',
  weight_kg: 28, height_cm: 128, location: 'medial', medical_history: '',
}

export default function Dashboard() {
  const [samples, setSamples] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [clinical, setClinical] = useState(DEFAULT_CLINICAL)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { getSamples().then(setSamples).catch(() => {}) }, [])

  const usingSample = !!selectedId

  const pickSample = (id) => { setSelectedId(id); setImageFile(null) }
  const pickFile = (e) => { setImageFile(e.target.files[0] || null); setSelectedId(null) }

  const handleAnalyze = async () => {
    setLoading(true); setError(null)
    try {
      const res = usingSample
        ? await analyze({ sampleId: selectedId })
        : await analyze({ image: imageFile, clinical })
      setResult(res)
    } catch (err) {
      setError(err.response?.data?.detail || 'วิเคราะห์ไม่สำเร็จ')
    } finally {
      setLoading(false)
    }
  }

  const canAnalyze = usingSample || imageFile

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">
          Bridge AI — วิเคราะห์การเจริญเติบโตของกระดูกเข่าเด็ก
        </h1>
        <p className="text-sm text-slate-500">ระบบสนับสนุนการตัดสินใจทางคลินิก (เดโม่)</p>
      </header>

      <main className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-[380px_1fr]">
        {/* ซ้าย: input */}
        <section className="space-y-5 rounded-xl border bg-white p-5">
          <div>
            <h2 className="mb-2 text-sm font-semibold text-slate-700">1. เลือกเคสตัวอย่าง</h2>
            <SamplePicker samples={samples} selectedId={selectedId} onSelect={pickSample} />
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className="h-px flex-1 bg-slate-200" />หรืออัปโหลดเอง<span className="h-px flex-1 bg-slate-200" />
          </div>

          <div>
            <h2 className="mb-2 text-sm font-semibold text-slate-700">2. อัปโหลด X-ray + ข้อมูลคลินิก</h2>
            <input type="file" accept="image/*" onChange={pickFile}
                   className="mb-3 block w-full text-sm" />
            <ClinicalForm value={clinical} onChange={setClinical} disabled={usingSample} />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!canAnalyze || loading}
            className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:bg-slate-300"
          >
            {loading ? 'กำลังประมวลผล…' : 'วิเคราะห์'}
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </section>

        {/* ขวา: ผลลัพธ์ */}
        <section className="space-y-6">
          {!result ? (
            <div className="flex h-64 items-center justify-center rounded-xl border border-dashed bg-white text-slate-400">
              เลือกเคสตัวอย่างหรืออัปโหลดภาพ แล้วกด “วิเคราะห์”
            </div>
          ) : (
            <>
              <div className="rounded-xl border bg-white p-5">
                <AnalysisSection result={result} />
              </div>
              <div className="rounded-xl border bg-white p-5">
                <GrowthPredictionSection prediction={result.growth_prediction} />
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  )
}
