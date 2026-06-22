/**
 * กราฟิกทิศทางการเติบโต — แสดงภาพกระดูกจำลองอย่างง่าย + ลูกศรแรงดัน
 * ชี้ให้เห็นว่า physeal bar จะดันให้กระดูกเอียงไปทางไหน
 *
 *  Varus  (ขาโก่งออก / bow legs)   → ปลายล่างเอียงออกด้านนอก, เข่าถ่างออก
 *  Valgus (ขาฉิ่งเข้า / knock knees) → ปลายล่างเอียงเข้าด้านใน, เข่าชนกัน
 */
const CONFIG = {
  Varus: {
    label: 'Bow-legged',
    tilt: 14,
    arrowDir: 1,
    color: '#f59e0b',
    barSide: 'medial',
  },
  Valgus: {
    label: 'Knock-kneed',
    tilt: -14,
    arrowDir: -1,
    color: '#3b82f6',
    barSide: 'lateral',
  },
}

export default function BoneDirectionGraphic({ direction }) {
  const c = CONFIG[direction] || CONFIG.Varus

  // จุดศูนย์กลางที่ growth plate (เข่า)
  const cx = 70, plateY = 88
  // กระดูกท่อนล่าง (tibia) เอียงตาม tilt
  const rad = (c.tilt * Math.PI) / 180
  const lowLen = 60
  const lx = cx + Math.sin(rad) * lowLen
  const ly = plateY + Math.cos(rad) * lowLen

  return (
    <div className="flex flex-col items-center gap-2">
      <svg viewBox="0 0 140 170" className="h-36 w-auto" role="img"
           aria-label={`Deformity direction: ${direction}`}>
        {/* เส้นแกนปกติ (เด็กปกติ) — เทาประ */}
        <line x1={cx} y1={20} x2={cx} y2={150} stroke="currentColor"
              className="text-slate-300 dark:text-slate-600" strokeWidth="2"
              strokeDasharray="4 4" />

        {/* กระดูกท่อนบน (femur) */}
        <rect x={cx - 9} y={24} width="18" height="60" rx="9"
              className="fill-slate-200 dark:fill-slate-600" />

        {/* แผ่นการเจริญเติบโต (growth plate) */}
        <rect x={cx - 11} y={plateY - 5} width="22" height="6" rx="3"
              className="fill-teal-400 dark:fill-med-teal" />
        {/* physeal bar (ฝั่งที่ปิด/โตช้า) */}
        <rect
          x={c.barSide === 'medial' ? cx - 11 : cx + 3}
          y={plateY - 5} width="8" height="6" rx="2"
          fill={c.color} />

        {/* กระดูกท่อนล่าง (tibia) — เอียง */}
        <g transform={`rotate(${c.tilt} ${cx} ${plateY})`}>
          <rect x={cx - 9} y={plateY + 2} width="18" height={lowLen} rx="9"
                fill={c.color} opacity="0.85" />
        </g>

        {/* ลูกศรแรงดัน/ทิศเอียง */}
        <g stroke={c.color} fill={c.color} strokeWidth="2.5" strokeLinecap="round">
          <line x1={lx} y1={ly - 6} x2={lx + c.arrowDir * 26} y2={ly - 6} />
          <polygon
            points={
              c.arrowDir === 1
                ? `${lx + 26},${ly - 6} ${lx + 18},${ly - 11} ${lx + 18},${ly - 1}`
                : `${lx - 26},${ly - 6} ${lx - 18},${ly - 11} ${lx - 18},${ly - 1}`
            }
            stroke="none" />
        </g>
      </svg>
      <span className="text-sm font-semibold" style={{ color: c.color }}>
        {direction} · {c.label}
      </span>
    </div>
  )
}
