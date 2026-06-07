// ภาพมี box+heatmap+ป้าย "Damage XX%" ฝังมาจาก backend แล้ว
export default function XrayOverlay({ image }) {
  return (
    <div className="overflow-hidden rounded-lg border bg-black">
      <img src={image} alt="ผลวิเคราะห์ X-ray" className="mx-auto block max-h-[460px] w-auto" />
    </div>
  )
}
