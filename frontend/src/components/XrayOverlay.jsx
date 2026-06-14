// ภาพมี box+heatmap+ป้าย "Damage XX%" ฝังมาจาก backend แล้ว
export default function XrayOverlay({ image }) {
  return (
    <div className="xray-frame group relative overflow-hidden rounded-xl bg-black">
      <img src={image} alt="ผลวิเคราะห์ X-ray"
           className="mx-auto block max-h-[460px] w-auto animate-fade-in transition-transform duration-500 ease-out group-hover:scale-[1.03]" />
      
      {/* Scanner Animation Overlay */}
      <div className="pointer-events-none absolute inset-0 z-10 overflow-hidden rounded-xl">
        <div className="animate-scanner absolute left-0 top-0 h-1 w-full bg-cyan-400/60 shadow-[0_0_20px_5px_rgba(34,211,238,0.5)] mix-blend-screen" />
      </div>
    </div>
  )
}
