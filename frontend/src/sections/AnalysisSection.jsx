import BoneDirectionGraphic from '../components/BoneDirectionGraphic'
import FactorList from '../components/FactorList'
import RiskBadge from '../components/RiskBadge'
import XrayOverlay from '../components/XrayOverlay'
import GrowthPredictionSection from './GrowthPredictionSection'

const RECOMMENDATION = {
  High: 'High-grade growth plate damage identified. Consider surgical intervention (Bar Resection or Epiphysiodesis) to prevent severe future deformity. Close follow-up every 3–6 months is recommended.',
  Medium: 'Moderate growth plate damage detected. Close monitoring every 6 months is recommended. Consider additional treatment options if deformity continues to progress.',
  Low: 'Low-grade growth plate damage with a favourable prognosis. Routine follow-up every 6–12 months is advised to monitor for changes.',
}

const RISK_COLOR = {
  High:   { bar: 'bg-red-500',    text: 'text-red-500 dark:text-red-400',    bg: 'bg-red-50 dark:bg-red-500/10',    border: 'border-red-200 dark:border-red-500/30' },
  Medium: { bar: 'bg-amber-500',  text: 'text-amber-500 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-500/10', border: 'border-amber-200 dark:border-amber-500/30' },
  Low:    { bar: 'bg-emerald-500', text: 'text-emerald-500 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-500/10', border: 'border-emerald-200 dark:border-emerald-500/30' },
}

export default function AnalysisSection({ result, clinical }) {
  const src = result.clinical_used || clinical
  const bmi = (src?.weight_kg && src?.height_cm)
    ? (src.weight_kg / Math.pow(src.height_cm / 100, 2)).toFixed(1)
    : null

  const rc = RISK_COLOR[result.risk_level] || RISK_COLOR.Low

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
      {/* ── ROW 1: Diagnosis ── */}

      {/* 1. X-Ray Image */}
      <div className="glass flex items-center justify-center rounded-2xl p-4 md:col-span-6 xl:col-span-4">
        <XrayOverlay image={result.overlay_image} />
      </div>

      {/* 2. Hero Metrics — redesigned */}
      <div className="glass flex flex-col gap-4 rounded-2xl p-5 md:col-span-6 xl:col-span-4">

        {/* Damage bar row */}
        <div
          className={`rounded-xl border p-4 ${rc.bg} ${rc.border}`}
          style={{ flexShrink: 0, minHeight: '110px' }}
        >
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">
            {result.metric_label || 'Physeal Plate Damage'}
          </p>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className={`text-4xl xl:text-5xl font-extrabold leading-none tabular-nums ${rc.text}`}>
              {result.damage_percent}%
            </span>
            <div className="shrink-0">
              <RiskBadge level={result.risk_level} />
            </div>
          </div>
          {/* Mini progress bar */}
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
            <div
              className={`h-full rounded-full transition-all duration-700 ${rc.bar}`}
              style={{ width: `${Math.min(100, result.damage_percent)}%` }}
            />
          </div>
        </div>
        {result.model_note && (
          <p className="rounded-lg bg-amber-50 p-2 text-xs leading-relaxed text-amber-800 dark:bg-amber-500/10 dark:text-amber-300">
            {result.model_note}
          </p>
        )}

        {/* Remaining Growth */}
        <div className="rounded-xl border border-teal-200/60 bg-teal-50/60 p-4 dark:border-teal-500/20 dark:bg-teal-500/5" style={{ flexShrink: 0 }}>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-teal-600 dark:text-teal-400">
            Remaining Growth Potential
          </p>
          <div className="flex flex-wrap items-baseline gap-2">
            <span className="text-4xl font-extrabold leading-none tabular-nums text-teal-600 dark:text-teal-400">
              {result.growth_prediction.remaining_growth_percent}%
            </span>
            <span className="text-sm text-teal-600/70 dark:text-teal-400/70">of normal</span>
          </div>
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
            <div
              className="h-full rounded-full bg-teal-500 transition-all duration-700"
              style={{ width: `${Math.min(100, result.growth_prediction.remaining_growth_percent)}%` }}
            />
          </div>
        </div>

        {/* Salter-Harris Type + BMI */}
        <div className="grid grid-cols-2 gap-3" style={{ flexShrink: 0 }}>
          <div className="rounded-xl border border-slate-200/60 bg-white/60 p-3 dark:border-slate-600/50 dark:bg-slate-700/30" style={{ minHeight: '92px' }}>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Salter-Harris
            </p>
            <p className="mt-1 text-xl xl:text-2xl font-extrabold text-slate-800 dark:text-slate-100 whitespace-nowrap">
              Type {result.salter_harris}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200/60 bg-white/60 p-3 dark:border-slate-600/50 dark:bg-slate-700/30" style={{ minHeight: '92px' }}>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              BMI
            </p>
            <p className="mt-1 text-2xl font-extrabold text-slate-800 dark:text-slate-100">
              {bmi !== null ? bmi : '—'}
            </p>
            {bmi !== null && (
              <p className="text-[10px] text-slate-400">
                {bmi < 18.5 ? 'Underweight' : bmi < 25 ? 'Normal' : bmi < 30 ? 'Overweight' : 'Obese'}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* 3. Clinical Recommendation */}
      <div className="glass flex flex-col rounded-2xl p-6 md:col-span-12 xl:col-span-4 bg-gradient-to-br from-teal-50/70 to-emerald-50/40 dark:from-teal-900/30 dark:to-emerald-900/10 border border-teal-100 dark:border-teal-800/30 relative overflow-hidden">
        <div className="absolute -right-4 -top-4 opacity-10 dark:opacity-[0.03]">
          <svg className="h-32 w-32 text-teal-600 dark:text-teal-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" /></svg>
        </div>
        <div className="relative z-10 flex-1 flex flex-col">
          <div className="mb-4 flex items-start gap-3">
            <span className="shrink-0 flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100 text-lg shadow-sm dark:bg-med-teal/40 mt-1">💡</span>
            <h3 className="text-lg font-semibold text-teal-950 dark:text-teal-100 leading-snug pt-1">Clinical Recommendation</h3>
          </div>
          <div className="flex-1 rounded-xl bg-white/70 p-5 text-sm leading-relaxed text-slate-800 shadow-sm backdrop-blur-md dark:bg-slate-900/40 dark:text-slate-200">
            {RECOMMENDATION[result.risk_level] || RECOMMENDATION.Low}
          </div>
        </div>
      </div>

      {/* ── ROW 2: Deformity ── */}

      {/* 4. Deformity Direction */}
      <div className="glass flex flex-col rounded-2xl p-6 md:col-span-6 xl:col-span-6">
        <div className="mb-3 flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-sm dark:bg-amber-500/20">🦴</span>
          <h3 className="font-semibold text-slate-900 dark:text-slate-200">Deformity Direction</h3>
        </div>
        <div className="flex-1 flex items-center justify-center rounded-xl border border-slate-200/60 bg-white/50 p-4 dark:border-slate-600/50 dark:bg-slate-700/30">
          <BoneDirectionGraphic direction={result.bend_direction} />
        </div>
      </div>

      {/* 5. Risk Factors */}
      <div className="glass flex flex-col rounded-2xl p-6 md:col-span-6 xl:col-span-6">
        <div className="mb-5 flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-lg shadow-sm dark:bg-med-blue/20">📋</span>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-200">Risk Factors (Explainability)</h3>
        </div>
        <div className="flex-1 flex flex-col">
          <FactorList factors={result.factors} />
        </div>
      </div>

      {/* ── ROW 3: Growth Prediction ── */}

      {/* 6. Growth Chart */}
      <div className="glass flex flex-col rounded-2xl p-6 md:col-span-12 xl:col-span-12 min-h-[400px]">
        <GrowthPredictionSection prediction={result.growth_prediction} />
      </div>
    </div>
  )
}
