import FactorList from '../components/FactorList'
import RiskBadge from '../components/RiskBadge'
import XrayOverlay from '../components/XrayOverlay'

const RECOMMENDATION = {
  High: 'จากข้อมูลพบการทำลายของ Growth Plate ระดับสูง ควรพิจารณาการผ่าตัด Bar resection หรือ Epiphysiodesis เพื่อป้องกัน Deformity ที่รุนแรง ในอนาคต ติดตามอาการอย่างใกล้ชิดทุก 3-6 เดือน',
  Medium: 'พบการทำลายของ Growth Plate ระดับปานกลาง ควรติดตามอาการอย่างใกล้ชิด ทุก 6 เดือน และพิจารณาแนวทางการรักษาเพิ่มเติมหาก Deformity มีแนวโน้มเพิ่มขึ้น',
  Low: 'พบการทำลายของ Growth Plate ระดับต่ำ มีแนวโน้มที่ดี ควรติดตามผลทุก 6-12 เดือน เพื่อเฝ้าระวังการเปลี่ยนแปลง',
}

export default function AnalysisSection({ result }) {
  return (
    <div className="space-y-6">
      {/* Top: X-ray + Hero metrics */}
      <div className="grid gap-6 md:grid-cols-2">
        <XrayOverlay image={result.overlay_image} />
        <div className="flex flex-col justify-center space-y-5">
          {/* Damage % hero */}
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-900">Physeal Plate Damage</p>
            <p className="text-gradient-red text-7xl font-bold leading-tight">{result.damage_percent}%</p>
          </div>

          {/* Risk badge */}
          <RiskBadge level={result.risk_level} />

          {/* Salter-Harris + Bend direction */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-3 dark:border-slate-600 dark:bg-slate-700/50">
              <span className="text-xs text-slate-900">Salter-Harris Classification</span>
              <p className="text-xl font-bold text-slate-900 dark:text-slate-100">Grade {result.salter_harris}</p>
            </div>
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-3 dark:border-slate-600 dark:bg-slate-700/50">
              <span className="text-xs text-slate-900">ทิศทางการโก่ง (Deformity)</span>
              <p className="text-xl font-bold text-slate-900 dark:text-slate-100">{result.bend_direction}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Factors + Recommendation */}
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <div className="mb-3 flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 text-sm dark:bg-med-blue/20">📊</span>
            <h3 className="font-semibold text-slate-900 dark:text-slate-200">ปัจจัยที่ส่งผลต่อความเสี่ยง</h3>
          </div>
          <FactorList factors={result.factors} />
        </div>
        <div>
          <div className="mb-3 flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-teal-50 text-sm dark:bg-med-teal/20">💡</span>
            <h3 className="font-semibold text-slate-900 dark:text-slate-200">ข้อเสนอแนะทางคลินิกเบื้องต้น</h3>
          </div>
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-4 text-sm leading-relaxed text-slate-900 dark:border-slate-600 dark:bg-slate-700/50 dark:text-slate-300">
            {RECOMMENDATION[result.risk_level] || RECOMMENDATION.Low}
          </div>
        </div>
      </div>
    </div>
  )
}
