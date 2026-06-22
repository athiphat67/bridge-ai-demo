# กระบวนการพัฒนา Bridge AI

## สไลด์ 1: เป้าหมายการพัฒนา

**Bridge AI** ควรถูกพัฒนาเป็น **usable decision-support prototype** สำหรับการวิเคราะห์การบาดเจ็บของ growth plate บริเวณข้อเข่าเด็ก

- Input: ภาพ X-ray เข่า + ข้อมูลทางคลินิกแบบมีโครงสร้าง
- หน้าที่หลัก: ระบุตำแหน่ง growth plate หรือบริเวณบาดเจ็บที่เกี่ยวข้อง และผสานกับปัจจัยทางคลินิก
- Output: ภาพ overlay, risk summary ที่อธิบายได้ และ growth-impact projection แบบง่าย

**จุดเน้นของ prototype**

- สร้างต้นแบบที่ใช้งานได้จริงภายในทีม
- สาธิต workflow และผลลัพธ์ที่ตีความได้
- ไม่กล่าวอ้างเกินจริงเรื่องความแม่นยำเชิงวินิจฉัยหรือการพยากรณ์ระยะยาว

## สไลด์ 2: แนวทางพัฒนา Prototype

โครงการควรถูกพัฒนาเป็น **2 ชั้นที่ทำงานร่วมกัน**

**1. Vision Layer**

- ใช้ pre-trained detection model แล้ว fine-tune กับภาพ X-ray เข่าเด็ก
- ทำหน้าที่ detect physis หรือ injury region
- สร้าง bounding box หรือ heatmap สำหรับแสดงบน dashboard

**2. Prognosis Layer**

- แปลงข้อมูลทางคลินิกให้เป็น structured features
- รวมผลจากภาพกับ rule-based growth logic
- ประเมิน damage severity, risk direction และผลกระทบในช่วง 1, 3 และ 5 ปี

**เหตุผลที่เลือกแนวทางนี้**

- เหมาะสมกว่าการฝึก end-to-end prognosis model ตั้งแต่ตอนนี้
- สอดคล้องกับข้อจำกัดของข้อมูลที่มีอยู่
- อธิบาย ตรวจสอบ และสาธิตได้ง่ายกว่า

## สไลด์ 3: ขั้นตอนการพัฒนาในทางปฏิบัติ

**Step 1: เตรียมฐานของระบบ**

- ยืนยันขอบเขตของ prototype และผลลัพธ์ที่ต้องการ
- ทำความสะอาด dataset และตรวจสอบ labels
- ทำมาตรฐานโครงสร้าง clinical inputs

**Step 2: สร้าง product shell**

- ใช้โครง React + FastAPI ที่มีอยู่แล้ว
- เพิ่ม database สำหรับเก็บเคสและผลลัพธ์
- เพิ่ม object storage สำหรับ X-ray และภาพ overlay ที่สร้างขึ้น

**Step 3: เพิ่มโมเดลจริงตัวแรก**

- ฝึก localization model สำหรับ growth-plate region
- เชื่อม inference เข้ากับ backend API
- แทนที่ visual output แบบ metadata-only ด้วยผลจากโมเดลจริง

**Step 4: เชื่อม flow ของ prototype ให้ครบ**

- รวม model output กับ clinical logic และ growth logic
- แสดงผลทั้งหมดใน dashboard เดียว
- ทดสอบทั้งกับ sample cases และ uploaded cases

## สไลด์ 4: สิ่งที่ควรได้เมื่อจบ Prototype

เมื่อจบ prototype phase ทีมควรมี:

- dashboard ที่ deploy ได้
- backend API ที่ deploy ได้
- localization model รุ่นแรกที่ฝึกแล้ว
- hybrid prognosis engine
- ระบบเก็บข้อมูลเคสและไฟล์ภาพ
- sample cases สำหรับเดโมที่เสถียร
- เอกสาร, validation notes และข้อจำกัดของระบบ

**สารหลัก**

milestone ที่ถูกต้องของเฟสแรก ไม่ใช่ระบบ multimodal medical AI ที่สมบูรณ์
แต่คือ **hybrid prototype** ที่มี:

- vision model จริง 1 ตัว
- prognosis workflow ที่อธิบายได้ 1 ชุด
- dashboard ที่ใช้งานได้จริง 1 หน้าจอ
