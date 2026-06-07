import FactorList from '../components/FactorList'
import RiskBadge from '../components/RiskBadge'
import XrayOverlay from '../components/XrayOverlay'

export default function AnalysisSection({ result }) {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <XrayOverlay image={result.overlay_image} />
      <div className="space-y-5">
        <div>
          <p className="text-sm text-slate-500">Physeal Plate Damage</p>
          <p className="text-6xl font-bold text-red-600">{result.damage_percent}%</p>
        </div>
        <RiskBadge level={result.risk_level} />
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-slate-500">Salter-Harris</span>
            <p className="text-lg font-semibold">Grade {result.salter_harris}</p>
          </div>
          <div>
            <span className="text-slate-500">ทิศการโก่ง</span>
            <p className="text-lg font-semibold">{result.bend_direction}</p>
          </div>
        </div>
        <div>
          <p className="mb-2 text-sm font-medium text-slate-600">ทำไมได้คะแนนนี้</p>
          <FactorList factors={result.factors} />
        </div>
      </div>
    </div>
  )
}
