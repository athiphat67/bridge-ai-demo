import { useEffect, useState } from 'react'
import { analyze, getSamples, extractErrorMessage } from '../api/client'
import ClinicalForm from '../components/ClinicalForm'
import SamplePicker from '../components/SamplePicker'
import AnalysisSection from '../sections/AnalysisSection'

const DEFAULT_CLINICAL = {
  age_years: 8, bone_age_years: 8, gender: 'male',
  weight_kg: 28, height_cm: 128, location: 'medial', medical_history: '',
}

const FALLBACK_SAMPLES = [
  { id: 'case_normal', display_name: 'Female, 11 yr — Normal Growth Plate' },
  { id: 'case_low', display_name: 'Male, 14 yr — SH Type I Lateral' },
  { id: 'case_medium', display_name: 'Female, 11 yr — SH Type III Lateral Tibia' },
  { id: 'case_high', display_name: 'Male, 13 yr — SH Type IV Medial Tibia' },
]

export default function Dashboard() {
  const [mode, setMode] = useState('sample')
  const [samples, setSamples] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [clinical, setClinical] = useState(DEFAULT_CLINICAL)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('Preparing X-ray image…')
  const [error, setError] = useState(null)

  // ── Theme toggle ──
  const [dark, setDark] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        return localStorage.getItem('bridge-ai-theme') === 'dark'
      } catch {
        return false
      }
    }
    return false
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try {
      localStorage.setItem('bridge-ai-theme', dark ? 'dark' : 'light')
    } catch {
      // ponytail: ignore storage failures so the UI still renders in privacy-restricted browsers
    }
  }, [dark])

  useEffect(() => {
    let alive = true
    getSamples()
      .then((data) => {
        if (!alive) return
        setSamples(Array.isArray(data) && data.length ? data : FALLBACK_SAMPLES)
      })
      .catch(() => {
        if (!alive) return
        setSamples(FALLBACK_SAMPLES)
      })
    return () => { alive = false }
  }, [])

  const usingSample = mode === 'sample'

  useEffect(() => {
    if (usingSample && !selectedId && samples.length) {
      setSelectedId(samples[0].id)
    }
  }, [usingSample, selectedId, samples])

  const pickSample = (id) => { setSelectedId(id); setImageFile(null) }
  const pickFile = (e) => { setImageFile(e.target.files[0] || null); setSelectedId(null) }

  const handleAnalyze = async () => {
    setLoading(true); setError(null);
    setLoadingText('Preparing X-ray image…');

    let step = 0;
    const steps = [
      'Preparing X-ray image…',
      'Scanning bone structure…',
      'Evaluating damage…',
      'Calculating growth model…',
    ];
    const interval = setInterval(() => {
      step++;
      setLoadingText(steps[step % steps.length]);
    }, 800);

    try {
      const res = usingSample
        ? await analyze({ mode, sampleId: selectedId })
        : await analyze({ mode, image: imageFile, clinical })
      setResult(res)
    } catch (err) {
      console.error('[Bridge AI] analyze error:', err)
      setError(extractErrorMessage(err))
    } finally {
      clearInterval(interval);
      setLoading(false)
    }
  }

  const canAnalyze = usingSample ? !!selectedId : !!imageFile

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-100 text-slate-900 transition-colors duration-300 dark:bg-[#0f172a] dark:from-[#0f172a] dark:via-[#0f172a] dark:to-[#0f172a] dark:text-slate-200">
      {/* ── Header ── */}
      <header className="glass sticky top-0 z-50 px-6 py-4">
        <div className="mx-auto flex max-w-[1600px] items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-med-blue to-med-cyan shadow-glow-blue">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-bold text-gradient">
              Bridge AI — Pediatric Knee Growth Analysis
            </h1>
            <p className="text-xs text-slate-900 dark:text-slate-400">Clinical Decision Support System (Demo)</p>
          </div>
          {/* Theme toggle */}
          <button
            onClick={() => setDark(!dark)}
            className="theme-toggle"
            aria-label="Toggle light/dark theme"
          />
        </div>
      </header>

      {/* ── Main ── */}
      <main className="mx-auto grid max-w-[1600px] grid-cols-1 gap-6 p-6 lg:grid-cols-[400px_1fr]">
        {/* Left: input */}
        <section className="glass space-y-5 rounded-2xl p-5">
          {/* Section header */}
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-med-blue/10 text-sm dark:bg-med-blue/20">⚙️</span>
            <h2 className="font-semibold text-slate-900 dark:text-slate-200">Analysis Settings</h2>
          </div>

          <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-600 dark:bg-slate-700/50">
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                {usingSample ? 'Sample mode' : 'Real model mode'}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {usingSample ? 'Metadata-backed demo cases' : 'C1 YOLO + C2 ResNet'}
              </p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={!usingSample}
              aria-label="Use real vision models"
              onClick={() => { setMode(usingSample ? 'real' : 'sample'); setResult(null); setError(null) }}
              className={`relative h-7 w-12 rounded-full transition ${usingSample ? 'bg-slate-300 dark:bg-slate-600' : 'bg-med-blue'}`}
            >
              <span className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow transition-all ${usingSample ? 'left-1' : 'left-6'}`} />
            </button>
          </div>

          {usingSample ? (
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-900">Select a Sample Case</p>
              <SamplePicker samples={samples.length ? samples : FALLBACK_SAMPLES} selectedId={selectedId} onSelect={pickSample} />
            </div>
          ) : (
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-900">Upload X-ray + Clinical Data</p>
              <label className="group mb-3 flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-slate-200 p-3 transition hover:border-med-cyan hover:bg-cyan-50/50 dark:border-slate-600 dark:hover:border-med-cyan dark:hover:bg-slate-700/50">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-50 text-lg transition group-hover:bg-cyan-100 dark:bg-med-cyan/10 dark:group-hover:bg-med-cyan/20">📁</span>
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-300">{imageFile ? imageFile.name : 'Select X-ray image'}</p>
                  <p className="text-xs text-slate-900">PNG, JPG (recommended 800–1200px)</p>
                </div>
                <input type="file" accept="image/*" onChange={pickFile} className="hidden" />
              </label>
              <ClinicalForm value={clinical} onChange={setClinical} disabled={false} />
            </div>
          )}

          {/* Analyze button */}
          <button
            onClick={handleAnalyze}
            disabled={!canAnalyze || loading}
            className="btn-analyze w-full rounded-xl py-3.5 text-sm"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                {loadingText}
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                Analyze X-ray
              </span>
            )}
          </button>
          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-500/30 dark:bg-red-900/30">
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-red-500">⚠️</span>
                <div>
                  <p className="text-sm font-medium text-red-700 dark:text-red-300">Analysis Failed</p>
                  <p className="mt-0.5 text-xs leading-relaxed text-red-600 dark:text-red-400">{error}</p>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Right: results */}
        <section className="space-y-6">
          {!result ? (
            <div className="glass group relative flex h-[460px] flex-col items-center justify-center overflow-hidden rounded-2xl">
              {/* Skeleton background */}
              <div className="absolute inset-0 flex items-center justify-center opacity-[0.03] transition-opacity duration-1000 group-hover:opacity-[0.06] dark:opacity-[0.08] dark:group-hover:opacity-[0.15]">
                <div className="relative h-[300px] w-[200px] rounded-3xl border-8 border-current">
                  <div className="absolute left-0 right-0 top-1/2 h-4 bg-current" />
                </div>
              </div>
              <div className="z-10 flex flex-col items-center animate-pulse">
                <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-slate-100 text-4xl shadow-inner dark:bg-slate-800">
                  🔬
                </div>
                <p className="text-lg font-medium text-slate-900 dark:text-slate-200">System ready for analysis</p>
                <p className="mt-2 max-w-xs text-center text-sm text-slate-500 dark:text-slate-400">
                  Select a sample case or upload an X-ray image,<br /> then press <b>"Analyze X-ray"</b>
                </p>
              </div>
            </div>
          ) : (
            <div className="glass animate-fade-in rounded-2xl p-6">
              <AnalysisSection result={result} clinical={clinical} usingSample={usingSample} />
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
