import BoneDirectionGraphic from '../components/BoneDirectionGraphic'
import FactorList from '../components/FactorList'
import RiskBadge from '../components/RiskBadge'
import XrayOverlay from '../components/XrayOverlay'
import GrowthPredictionSection from './GrowthPredictionSection'

const RECOMMENDATION = {
  High: 'จากข้อมูลพบการทำลายของ Growth Plate ระดับสูง ควรพิจารณาการผ่าตัด Bar resection หรือ Epiphysiodesis เพื่อป้องกัน Deformity ที่รุนแรง ในอนาคต ติดตามอาการอย่างใกล้ชิดทุก 3-6 เดือน',
  Medium: 'พบการทำลายของ Growth Plate ระดับปานกลาง ควรติดตามอาการอย่างใกล้ชิด ทุก 6 เดือน และพิจารณาแนวทางการรักษาเพิ่มเติมหาก Deformity มีแนวโน้มเพิ่มขึ้น',
  Low: 'พบการทำลายของ Growth Plate ระดับต่ำ มีแนวโน้มที่ดี ควรติดตามผลทุก 6-12 เดือน เพื่อเฝ้าระวังการเปลี่ยนแปลง',
}

export default function AnalysisSection({ result }) {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
      {/* ── ROW 1: Diagnosis ── */}

      {/* 1. X-Ray Image */}
      <div className="glass flex items-center justify-center rounded-2xl p-6 md:col-span-6 xl:col-span-4">
        <XrayOverlay image={result.overlay_image} />
      </div>

      {/* 2. Hero Metrics */}
      <div className="glass flex flex-col justify-center space-y-6 rounded-2xl p-6 md:col-span-6 xl:col-span-4 bg-gradient-to-br from-slate-50/50 to-slate-100/30 dark:from-slate-800/40 dark:to-slate-800/10 shadow-sm border border-slate-100 dark:border-slate-700/50">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-900 dark:text-slate-400">Damage</p>
            <p className="text-gradient-red text-6xl font-bold leading-tight drop-shadow-sm">{result.damage_percent}%</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-900 dark:text-slate-400">Remaining Growth</p>
            <p className="text-gradient text-6xl font-bold leading-tight drop-shadow-sm">{result.remaining_growth_percent}%</p>
          </div>
        </div>

        <div>
          <RiskBadge level={result.risk_level} />
        </div>

        <div className="rounded-lg border border-slate-200/60 bg-white/50 p-4 dark:border-slate-600/50 dark:bg-slate-700/30">
          <span className="text-xs text-slate-900 dark:text-slate-400">Salter-Harris Classification</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">Grade {result.salter_harris}</p>
        </div>
      </div>

      {/* 3. Clinical Recommendation */}
      <div className="glass flex flex-col rounded-2xl p-6 md:col-span-12 xl:col-span-4 bg-gradient-to-br from-teal-50/70 to-emerald-50/40 dark:from-teal-900/30 dark:to-emerald-900/10 border border-teal-100 dark:border-teal-800/30 relative overflow-hidden">
        <div className="absolute -right-4 -top-4 opacity-10 dark:opacity-[0.03]">
          <svg className="h-32 w-32 text-teal-600 dark:text-teal-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" /></svg>
        </div>
        <div className="relative z-10 flex-1 flex flex-col">
          <div className="mb-4 flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100 text-lg shadow-sm dark:bg-med-teal/40">💡</span>
            <h3 className="text-lg font-semibold text-teal-950 dark:text-teal-100">ข้อเสนอแนะทางคลินิก</h3>
          </div>
          <div className="flex-1 rounded-xl bg-white/70 p-5 text-base leading-relaxed text-slate-800 shadow-sm backdrop-blur-md dark:bg-slate-900/40 dark:text-slate-200">
            {RECOMMENDATION[result.risk_level] || RECOMMENDATION.Low}
          </div>
        </div>
      </div>

      {/* ── ROW 2: Prediction & Deformity ── */}

      {/* 4. Deformity & Probabilities */}
      <div className="glass flex flex-col space-y-6 rounded-2xl p-6 md:col-span-6 xl:col-span-6">
        {/* Deformity */}
        <div className="group relative overflow-hidden rounded-xl border border-slate-200/60 bg-white/50 p-4 dark:border-slate-600/50 dark:bg-slate-700/30">
          <span className="text-xs text-slate-900 dark:text-slate-400">ทิศทางการโก่ง (Deformity)</span>
          <div className="mt-4 flex w-full justify-center">
            <BoneDirectionGraphic direction={result.bend_direction} />
          </div>
        </div>

        {/* Probability Chart */}
        <div className="flex-1">
          <div className="mb-3 flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-sm dark:bg-med-indigo/20">🎯</span>
            <h3 className="font-semibold text-slate-900 dark:text-slate-200">โอกาสเกิดความผิดปกติ</h3>
          </div>
          <div className="space-y-4 rounded-xl border border-slate-200/60 bg-white/50 p-5 dark:border-slate-600/50 dark:bg-slate-700/30">
            {/* Valgus */}
            <div>
              <div className="mb-1.5 flex justify-between text-xs font-medium">
                <span className="text-slate-900 dark:text-slate-300">ขาฉิ่งเข้า (Valgus)</span>
                <span className="text-slate-900 dark:text-slate-300">{result.probability.valgus_percent}%</span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-600 shadow-inner">
                <div className="h-full rounded-full bg-blue-500 transition-all duration-1000" style={{ width: `${result.probability.valgus_percent}%` }} />
              </div>
            </div>
            {/* Varus */}
            <div>
              <div className="mb-1.5 flex justify-between text-xs font-medium">
                <span className="text-slate-900 dark:text-slate-300">ขาโก่งออก (Varus)</span>
                <span className="text-slate-900 dark:text-slate-300">{result.probability.varus_percent}%</span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-600 shadow-inner">
                <div className="h-full rounded-full bg-amber-500 transition-all duration-1000" style={{ width: `${result.probability.varus_percent}%` }} />
              </div>
            </div>
            {/* Arrest */}
            <div>
              <div className="mb-1.5 flex justify-between text-xs font-medium">
                <span className="text-slate-900 dark:text-slate-300">กระดูกหยุดโต (Growth Arrest)</span>
                <span className="text-slate-900 dark:text-slate-300">{result.probability.arrest_percent}%</span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-600 shadow-inner">
                <div className="h-full rounded-full bg-red-500 transition-all duration-1000" style={{ width: `${result.probability.arrest_percent}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Factors */}
      <div className="glass flex flex-col rounded-2xl p-6 md:col-span-6 xl:col-span-6">
        <div className="mb-5 flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-lg shadow-sm dark:bg-med-blue/20">📊</span>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-200">ปัจจัยที่ส่งผลต่อความเสี่ยง (Explainability Factors)</h3>
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
