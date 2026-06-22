# กระบวนการพัฒนา Prototype ของ Bridge AI

## บทนำ

เอกสารฉบับนี้อธิบายแนวทางพัฒนาโครงการ Bridge AI จากแนวคิดตั้งต้นไปสู่ต้นแบบที่ใช้งานได้จริง พร้อมโมเดลตั้งต้นที่เหมาะสมในเชิงปฏิบัติ เอกสารถูกเขียนสำหรับทีมพัฒนาหลายบทบาท โดยเน้นทิศทางผลิตภัณฑ์ โครงสร้างระบบ การไหลของข้อมูล กลยุทธ์โมเดล และลำดับการดำเนินงาน มากกว่ารายละเอียดระดับโค้ด

ใน repository ปัจจุบันมีทั้งแอปเดโมที่ใช้งานได้ ชุดภาพ X-ray ตัวอย่าง ข้อมูล synthetic สำหรับ clinical bias และ pipeline แบบ deterministic สำหรับคำนวณคะแนนความเสี่ยง สิ่งเหล่านี้มีประโยชน์มากในฐานะต้นแบบอ้างอิงด้านหน้าจอ รูปแบบ API และลำดับการใช้งานเดโม อย่างไรก็ตาม เดโมปัจจุบันยังเป็นระบบที่ขับเคลื่อนด้วย metadata และยังไม่ใช่ machine learning prototype อย่างแท้จริง ดังนั้นเอกสารนี้จึงมุ่งอธิบายวิธีขยับจาก mock facade ปัจจุบัน ไปสู่ prototype รุ่นแรกที่มี AI จริง โดยไม่ตั้งเป้าทางคลินิกเกินความพร้อมของข้อมูล

## ข้อสมมติ

- โครงการนี้มีเป้าหมายเป็น prototype สำหรับช่วยตัดสินใจเบื้องต้น ไม่ใช่ระบบวินิจฉัยทางการแพทย์ที่พร้อมใช้งานจริง
- ข้อมูลที่มีอยู่ยังมีจำกัด และประกอบด้วยภาพ X-ray เข่าเด็กจาก open หรือ synthetic data, bounding box labels, ข้อมูล synthetic clinical bias และสูตรอ้างอิงจากงานวิจัย
- ยังไม่มี longitudinal dataset ขนาดเพียงพอที่จะใช้ฝึกโมเดล end-to-end สำหรับพยากรณ์ผลการเติบโตระยะยาวอย่างน่าเชื่อถือ
- ทีมต้องการ prototype ที่น่าเชื่อถือ อธิบายได้ สาธิตได้ และสร้างได้จริงภายในเวลาจำกัด

## 1. ภาพรวมโครงการ

Bridge AI มีเป้าหมายเพื่อช่วยประเมินความเสี่ยงเบื้องต้นของการบาดเจ็บที่ growth plate บริเวณข้อเข่าเด็กหลังอุบัติเหตุ ปัญหาหลักคือภาพ X-ray ในวันที่เกิดเหตุสามารถแสดงความเสียหายเชิงโครงสร้าง ณ เวลานั้นได้ แต่ยังไม่สามารถบอกได้โดยตรงว่าอาการบาดเจ็บนั้นจะส่งผลต่อการเติบโตของกระดูก การเอียงผิดรูป หรือความยาวขาที่ไม่เท่ากันมากน้อยเพียงใดในอนาคต ในทางปฏิบัติ ความไม่แน่นอนนี้ทำให้การตัดสินใจรักษาต้องอาศัยการติดตามและการประเมินจากประสบการณ์เป็นหลัก

ผู้ใช้เป้าหมายหลักของ prototype คือแพทย์ด้านกระดูกเด็ก ทีมคลินิกที่เกี่ยวข้องกับการอ่านภาพ หรือผู้ประเมินนวัตกรรมที่ต้องการเห็นว่าระบบนี้สามารถช่วย decision support ได้อย่างไร ผู้ใช้รองคือทีมวิจัยและผู้มีส่วนเกี่ยวข้องด้านผลิตภัณฑ์ที่ต้องการแพลตฟอร์มต้นแบบสำหรับตรวจสอบ flow การใช้งาน คุณภาพข้อมูล และความเป็นไปได้ของโมเดล

prototype ควรสาธิตให้เห็น 3 เรื่องสำคัญอย่างชัดเจน:

1. ระบบรับภาพ X-ray เข่าพร้อมข้อมูล clinical input แบบมีโครงสร้างได้
2. ระบบสามารถระบุตำแหน่ง growth plate หรือบริเวณบาดเจ็บที่เกี่ยวข้อง พร้อมแสดงผลที่ตีความได้
3. ระบบสามารถผสานผลจากภาพกับปัจจัยทางคลินิก เพื่อสร้างมุมมองเชิงพยากรณ์ความเสี่ยงที่อธิบายได้ แม้ผลการทำนายระยะยาวในเฟสแรกจะยังเป็นการประมาณ

## 2. เป้าหมายของ Prototype

สำหรับโครงการนี้ คำว่า “usable prototype” ไม่ควรหมายถึงระบบ AI ทางการแพทย์ที่ทำงานอัตโนมัติครบวงจร แต่ควรหมายถึงต้นแบบภายในที่เชื่อถือได้ ผู้ใช้สามารถอัปโหลดหรือเลือกเคสตัวอย่าง ตรวจดูตำแหน่งที่ระบบโฟกัส ดูปัจจัยเสี่ยงแบบมีโครงสร้าง และได้รับผลลัพธ์เชิงพยากรณ์ที่ให้เหตุผลได้มากพอสำหรับการสาธิตและอภิปรายต่อ

prototype รุ่นแรกควรมี:

- การรับภาพ X-ray ผ่านการอัปโหลดและ sample cases
- แบบฟอร์ม clinical input เช่น อายุ อายุของกระดูก เพศ น้ำหนัก ส่วนสูง ตำแหน่งบาดเจ็บ และประวัติทางการแพทย์ที่เกี่ยวข้อง
- vision model ตั้งต้นที่ทำหน้าที่ localize growth plate หรือบริเวณบาดเจ็บ และถ้าเป็นไปได้อาจคาดการณ์ class เบื้องต้นหรือ damage proxy
- prognosis engine แบบ rule-based หรือ hybrid ที่ผสาน image features กับปัจจัยทางคลินิก เพื่อสร้างผลลัพธ์ด้าน severity, risk และ projection ช่วง 1, 3 และ 5 ปี
- dashboard ที่แสดง overlay, metric หลัก, คำอธิบายความเสี่ยง และกราฟแนวโน้ม
- ระบบจัดเก็บข้อมูลเคส ไฟล์ภาพ และผลลัพธ์ที่สร้างขึ้น

prototype รุ่นแรกควรตัดสิ่งต่อไปนี้ออกจากขอบเขต:

- การใช้งานเชิงคลินิกจริงหรือระบบแนะนำการรักษาอัตโนมัติ
- การเชื่อมต่อ PACS เต็มรูปแบบ ระบบสิทธิ์ระดับโรงพยาบาล และการควบคุมด้าน audit ระดับองค์กร
- multimodal deep model แบบ end-to-end ที่ฝึกเพื่อพยากรณ์ผลลัพธ์ระยะยาวจากภาพ X-ray ดิบโดยตรง
- การอ้างความแม่นยำเชิงวินิจฉัยเกินกว่าที่ validation set ขนาดเล็กจะรองรับได้

สิ่งเหล่านี้ควรอยู่ในเฟสถัดไป เพราะต้องอาศัยข้อมูลที่มากขึ้น governance ที่เข้มขึ้น และการตรวจสอบผลในโลกจริง

## 3. Tech Stack ที่แนะนำ

แนวทางที่เหมาะสมที่สุดคือยึดกับ stack ที่ใช้งานได้อยู่แล้วใน repository ปัจจุบัน และเปลี่ยนเฉพาะส่วนที่เป็นข้อจำกัดต่อการทำ prototype จริง

### Frontend

แนะนำให้ใช้ React ร่วมกับ Vite และ Tailwind CSS

stack นี้มีอยู่แล้วใน repository และเหมาะกับ dashboard prototype อย่างมาก รองรับการ iterate หน้าจอได้เร็ว น้ำหนักเบา และแยกส่วน input flow, ภาพ overlay และ analytical sections ได้ชัดเจน จึงไม่มีเหตุผลจำเป็นต้องเปลี่ยนในระยะนี้

### Backend

แนะนำให้ใช้ FastAPI กับ Python

backend ปัจจุบันมีโครง API ที่ชัดเจน และเข้ากันได้ดีกับงาน image processing, data transformation และ model inference FastAPI เหมาะมากเพราะภาษาเดียวกันสามารถใช้ทั้งใน API, preprocessing, inference orchestration และ research scripts

### Database

แนะนำให้ใช้ PostgreSQL สำหรับ prototype ที่ deploy และใช้ SQLite สำหรับ local development เท่านั้น

เดโมปัจจุบันยังไม่มี persistence สำหรับ analysis history หากต้องการให้ prototype ใช้งานได้จริง ระบบควรเก็บข้อมูลเคส อินพุต ผลลัพธ์ และ model-run metadata ได้ PostgreSQL เป็นตัวเลือกที่เหมาะสมเพราะรองรับ structured clinical data และรองรับการขยายต่อเรื่อง traceability กับ auditability โดยไม่ซับซ้อนเกินจำเป็น

### Object Storage

แนะนำให้ใช้ S3-compatible storage เช่น Supabase Storage, Cloudflare R2 หรือ AWS S3

ไฟล์ X-ray ที่อัปโหลด ภาพ overlay และ artifact ที่สร้างขึ้นไม่ควรถูกเก็บไว้ใน container หรือในฐานข้อมูลโดยตรง object storage เป็นวิธีที่ง่ายและเหมาะกับการเตรียมระบบให้พร้อมต่อยอดเรื่อง dataset versioning ในอนาคต

### AI และ Data Tooling

แนะนำให้ใช้ PyTorch, Ultralytics YOLO สำหรับ vision model รุ่นแรก, scikit-learn สำหรับ baseline ฝั่ง tabular และใช้ NumPy, Pandas, Pillow, OpenCV สำหรับ preprocessing

ทางเลือกนี้ตั้งใจให้ pragmatic มากกว่าจะล้ำเกินความจำเป็น โครงการต้องการผลลัพธ์แบบ localization ที่มองเห็นได้เร็ว และ YOLO-style detection ฝึกและสาธิตได้ง่ายกว่าการเริ่มด้วย segmentation pipeline ที่ซับซ้อน scikit-learn ก็เพียงพอสำหรับ baseline หรือการ calibrate probability ฝั่ง structured features ในระยะแรก

หากในอนาคตทีมต้องทำงานกับ medical imaging ที่เข้มขึ้นหรือรองรับ DICOM อย่างจริงจัง จึงค่อยเพิ่ม MONAI ในเฟสถัดไป

### Cloud และ Deployment

แนะนำให้ใช้ Vercel สำหรับ frontend และ Render, Railway หรือ Fly.io สำหรับ FastAPI backend ที่ต้องเก็บ model files

repository ปัจจุบันอธิบายวิธี deploy ด้วย Vercel ไว้แล้ว ซึ่งเพียงพอสำหรับ pure demo แต่เมื่อมี model inference จริง backend ควรอยู่บน host ที่จัดการ runtime ฝั่ง Python ได้เสถียรกว่า มี filesystem และ memory headroom ที่เหมาะกับ model serving มากกว่า ดังนั้นการ deploy แยก frontend และ backend จึงเป็นทางเลือกที่ปลอดภัยกว่า

### External Services และ APIs

prototype รุ่นแรกยังไม่จำเป็นต้องใช้ external medical API

บริการเสริมที่อาจเพิ่มในภายหลัง ได้แก่:

- `pydicom` สำหรับรองรับ DICOM ingestion
- Orthanc หรือระบบเชื่อม PACS หากต้องเชื่อม workflow โรงพยาบาลในอนาคต
- เครื่องมือ monitoring หรือ product analytics เช่น Sentry และ PostHog

## 4. สถาปัตยกรรมระบบ

สถาปัตยกรรมที่เหมาะสมควรเป็น hybrid application ที่แบ่งออกเป็น 5 ชั้นหลักซึ่งเข้าใจง่ายและใช้งานได้จริง

### Presentation Layer

frontend ทำหน้าที่เป็น dashboard แบบ workflow-centric ผู้ใช้อัปโหลดภาพหรือเลือก sample case กรอก clinical values ส่งวิเคราะห์ และรับผลลัพธ์กลับมาในหน้าจอเดียวที่มีทั้งภาพ overlay, risk metrics, factors และกราฟ projection

### API Layer

FastAPI backend เปิด endpoints สำหรับดึง sample cases, ส่งเคสเข้าวิเคราะห์, เรียกผลการวิเคราะห์ และดูข้อมูลเคส ใน prototype รุ่นแรก inference อาจยังทำแบบ synchronous ได้ หาก runtime ยังสั้นพอ และหากในอนาคตรันโมเดลใช้เวลานานขึ้น จึงค่อยขยับเป็น asynchronous job flow

### Data Layer

ชั้นข้อมูลควรเก็บ:

- ข้อมูล case metadata และ clinical input ใน PostgreSQL
- ไฟล์ X-ray และภาพ overlay ใน object storage
- model artifacts และ version metadata ในตำแหน่งที่จัดการได้ชัดเจน

### Model Layer

model layer ควรถูกแยก ไม่ควรทำแบบ end-to-end ตั้งแต่แรก:

- vision component สำหรับ localize physis region และถ้าเป็นไปได้ให้ดึง fracture หรือ damage features เบื้องต้น
- prognosis component สำหรับนำผลลัพธ์นั้นมารวมกับ clinical input และ logic จากงานวิจัย เพื่อสร้าง risk-oriented projections

การแยกแบบนี้ช่วยให้ระบบอธิบายได้ง่ายกว่า และสอดคล้องกับข้อจำกัดของข้อมูลในปัจจุบัน

### User Interaction Flow

high-level flow ที่แนะนำคือ:

1. ผู้ใช้ส่งภาพและ clinical input
2. backend ตรวจสอบและ preprocess ข้อมูล
3. vision model สร้าง region และ feature outputs
4. prognosis engine แปลงผลจากโมเดลและข้อมูลคลินิกเป็นผลลัพธ์เชิงความเสี่ยง
5. ระบบบันทึกผลลัพธ์และส่งกลับไปยัง frontend
6. frontend แสดง overlay, scores, factors และแนวโน้มการเติบโต

## 5. Data Flow

ข้อมูลควรเข้าสู่ระบบผ่าน submission flow ที่ควบคุมได้ ไม่ใช่ส่งตรงเข้าโมเดลทันที เพราะ prototype ที่อธิบายได้และทดสอบได้ ต้องมี data pipeline ที่ชัดเจนไม่แพ้ตัวโมเดล

flow ที่แนะนำมีดังนี้:

1. **Input capture**  
   ผู้ใช้ส่งภาพ X-ray เข่าพร้อม structured fields เช่น อายุ อายุของกระดูก เพศ น้ำหนัก ส่วนสูง ตำแหน่งบาดเจ็บ และตัวเลือกด้าน medical history

2. **Validation**  
   backend ตรวจสอบชนิดไฟล์ ขนาดไฟล์ ความสามารถในการอ่านภาพ ฟิลด์ที่จำเป็น ช่วงค่าที่รับได้ และ enum consistency หากข้อมูลไม่ถูกต้องควร reject ก่อนถึงขั้น model execution

3. **Preprocessing**  
   ภาพถูกแปลงให้อยู่ในรูปแบบมาตรฐานสำหรับ inference ใน prototype รุ่นแรก PNG หรือ JPEG เพียงพอ หากเพิ่ม DICOM ภายหลัง การทำ windowing และ metadata extraction ควรอยู่ในขั้นนี้ และควรเก็บต้นฉบับที่ trace ได้ไว้ด้วย

4. **Feature extraction**  
   vision model สร้างผลลัพธ์เชิงพื้นที่อย่างน้อยหนึ่งอย่าง เช่น bounding box รอบ physis region หากโมเดลรองรับมากกว่า localization ก็อาจสร้าง class probabilities ของ Salter-Harris หรือ damage proxy เบื้องต้นได้

5. **Clinical transformation**  
   clinical inputs ถูกแปลงให้พร้อมใช้ทั้งใน logic และโมเดล เช่น การคำนวณ BMI, age normalization, lookup ค่า clinical bias และ encoding ข้อมูลยาหรือโรคประจำตัว repository ปัจจุบันมีทั้ง synthetic clinical bias generator และ WHO reference tables ที่ใช้เป็นจุดเริ่มต้นได้

6. **Fusion และ prognosis**  
   ระบบรวม image-derived features กับ clinical features และ rule-based growth logic เพื่อคำนวณผลลัพธ์ของ prototype ขั้นตอนนี้เหมาะที่สุดสำหรับการใช้สูตรเกี่ยวกับ remaining growth, mechanical bias และ deformity direction

7. **Persistence**  
   ควรเก็บ raw input metadata, transformed features, result payload, model version และ timestamps ส่วน raw image และ overlay asset ควรถูกเก็บใน object storage พร้อม reference ในฐานข้อมูล

8. **Display**  
   frontend แสดงภาพที่ประมวลผลแล้ว metric ที่สำคัญ คำอธิบายความเสี่ยง และ projection ในรูปแบบที่อ่านเข้าใจง่ายสำหรับผู้ใช้สายคลินิก

## 6. แนวทาง AI/ML Model

โครงการนี้จำเป็นต้องใช้ machine learning แต่ไม่ควรเริ่มจาก multimodal prognosis model แบบ end-to-end ใน prototype รุ่นแรก

### โมเดลควรทำอะไร

โมเดลรุ่นแรกควรรับผิดชอบงานเดียวให้ดี คือระบุหรือล้อมตำแหน่งบริเวณ growth plate หรือรอยบาดเจ็บที่เกี่ยวข้องบนภาพ X-ray เข่าเด็ก และถ้า dataset รองรับ อาจคาดการณ์ class เบื้องต้นหรือ damage severity proxy เพิ่มเติม

นี่คือจุดที่ machine learning เพิ่มคุณค่าได้ชัดที่สุด เพราะ:

- ให้ผลลัพธ์ที่มองเห็นได้และตีความได้บนหน้าจอ
- ลดการพึ่ง label ที่เตรียมไว้ล่วงหน้าสำหรับแต่ละเคสเดโม
- สร้าง structured features สำหรับป้อนเข้าสู่ prognosis engine

### ต้องใช้ input data อะไร

starting model ต้องใช้:

- ภาพ X-ray เข่าเด็กในมุมที่สม่ำเสมอพอสมควร พร้อม train/validation split ที่ชัดเจน
- bounding box annotations สำหรับ physis หรือ injury region
- optional labels เช่น Salter-Harris type, laterality, bar location หรือ damage severity proxy

ส่วนในระดับ prototype pipeline เต็มรูปแบบ ควรมี structured input เพิ่ม:

- อายุและ bone age
- เพศ
- น้ำหนักและส่วนสูง
- clinical history หรือ pathology modifiers ที่มีผลต่อการเติบโตของกระดูก

### โมเดลควรให้ output อะไร

โมเดลรุ่นแรกควรให้:

- bounding box หรือ localization map ของบริเวณที่เกี่ยวข้อง
- confidence score
- optional coarse class เช่น normal เทียบกับ injury หรือกลุ่ม Salter-Harris หากข้อมูลเพียงพอ

ผลลัพธ์ระดับระบบควรรวม:

- damage estimate หรือ injury severity proxy
- แนวโน้ม varus, valgus หรือ growth arrest ผ่าน prognosis engine
- projected growth-impact metrics แบบง่ายในช่วง 1, 3 และ 5 ปี

### ควรใช้ approach แบบไหน

approach ที่แนะนำสำหรับเฟสแรกคือ hybrid stack:

- pre-trained object detection model ที่นำมา fine-tune กับชุด X-ray ที่มีอยู่
- prognosis layer แบบ rule-based ที่อิง clinical formulas และ structured bias tables
- optional lightweight tabular model ในภายหลัง เมื่อมี structured records มากพอ

แนวทางนี้เหมาะกว่าการฝึก multimodal deep prognosis model แบบ custom ตั้งแต่ต้น เพราะ repository ปัจจุบันยังไม่แสดงหลักฐานว่ามี real longitudinal ground-truth dataset เพียงพอ การฝึก end-to-end prognosis model บนข้อมูล synthetic หรือ weak outcome labels จะทำให้ระบบดูน่าเชื่อถือเกินจริง

### กระบวนการฝึกและประเมินเบื้องต้น

ลำดับที่แนะนำคือ:

1. เตรียมและทำความสะอาด labeled image dataset
2. ฝึก detector เพื่อ localize physis region หรือ injury region
3. ประเมิน localization quality ด้วย metric มาตรฐานและการดูภาพจริง
4. ตรึงโมเดลนี้เป็น image feature generator สำหรับ prototype
5. ใช้ prognosis logic แบบ rule-based สำหรับ integrated release รุ่นแรก
6. เก็บ structured usage data และ expert feedback
7. เพิ่ม tabular baseline ภายหลัง เฉพาะเมื่อมี outcome-linked records มากพอ

### เส้นทางการปรับปรุงโมเดล

การพัฒนาโมเดลควรค่อย ๆ เดินตามลำดับนี้:

1. ปรับคุณภาพ detection และ annotation
2. ปรับคุณภาพของ structured outcome definitions
3. เพิ่ม small tabular model หรือ calibration layer บน image-derived features
4. ทำ multimodal prognosis model จริง เมื่อพิสูจน์ได้แล้วว่าข้อมูลพร้อม

## 7. Main Feature Flows

prototype ควรมี feature flows จำนวนน้อยแต่แข็งแรง ไม่ควรมีหลาย flow ที่ทำได้เพียงผิวเผิน

### Analysis Submission Flow

ผู้ใช้เปิด dashboard อัปโหลด X-ray หรือเลือก sample case กรอก clinical inputs และส่งเคส ระบบตรวจสอบข้อมูล รัน inference และคืนผลลัพธ์เป็นชุดเดียวที่ครบสำหรับการอ่านผล

### Clinical Review Flow

ผู้ใช้ดูภาพ overlay เพื่อยืนยันว่าระบบโฟกัสถูกบริเวณ ตรวจดู damage หรือ injury metrics แล้วอ่าน factor list ที่อธิบายว่าทำไมระบบจึงให้ risk profile แบบนี้ flow นี้สำคัญมาก เพราะความน่าเชื่อถือไม่ได้มาจากตัวเลขเพียงอย่างเดียว แต่ต้องมาจากการมองเห็นเหตุผลด้วย

### Growth Projection Flow

ผู้ใช้ดูส่วนกราฟ projection ซึ่งแปลงผลจากภาพและข้อมูลคลินิกให้กลายเป็นมุมมองอนาคตแบบง่าย ใน prototype รุ่นแรก ควรระบุชัดเจนว่านี่คือ model-assisted estimate ไม่ใช่คำทำนายทางคลินิกที่เด็ดขาด

### Sample Demonstration Flow

ระบบควรมี curated sample cases ที่ให้ผลลัพธ์ได้เสถียรและเชื่อถือได้ สิ่งนี้จำเป็นทั้งสำหรับการเดโม การรีวิวกับ stakeholder และการทำ regression testing แม้หลังจากเริ่มใช้ model inference จริงแล้ว

### Data Capture and Iteration Flow

ทุกครั้งที่วิเคราะห์ควรสร้าง record ที่ trace ย้อนกลับได้ เพื่อให้ทีมมี feedback loop สำหรับการปรับโมเดล วิเคราะห์ error และขยาย dataset ในระยะถัดไป

## 8. กระบวนการพัฒนา

แนวทางพัฒนาจากศูนย์ไปสู่ usable prototype ควรเดินเป็นชั้น ๆ อย่างมีวินัย

### Project setup

เริ่มจากยืนยัน product scope, clinical inputs ที่ยอมรับ, user flow ที่ต้องการ และขอบเขตของคำกล่าวอ้างของ prototype repository ปัจจุบันมี baseline ที่ดีอยู่แล้ว ดังนั้นงานตั้งต้นที่สำคัญคือเก็บโครง frontend/backend ไว้ และแยกส่วน demo-only logic ออกจาก future real inference logic

### Tech stack setup

ตั้ง local environment ของ React frontend และ FastAPI backend จากนั้นเพิ่มการเชื่อม PostgreSQL และ object storage ตั้งแต่ต้น แม้ช่วงแรกจะยังรันด้วย local files อยู่ก็ตาม เพื่อไม่ให้ prototype ติดกับโครงสร้างแบบ static demo

### Data structure design

ออกแบบ entities ที่ชัดเจน เช่น case, uploaded image, clinical input set, model run, result summary และ overlay artifact metadata-driven format ที่มีใน repo ตอนนี้เป็นจุดเริ่มต้นที่ดี แต่ควรถูกยกระดับเป็น database-backed case schema

### Core feature implementation

คงรูปแบบ dashboard ปัจจุบันไว้: sample selection, manual upload, structured form, submission และผลลัพธ์ในหน้าเดียว จากนั้นเพิ่ม persistence, result history สำหรับ internal review และสถานะการทำงานพื้นฐานรอบ model execution

### Model or logic implementation

นำ vision model รุ่นแรกเข้ามาใช้แทน overlay generation ที่อิง label ล้วน และคง prognosis logic ให้เป็น hybrid และ explicit สูตร growth/scoring ที่มีอยู่แล้วใน repository ใช้เป็น starting engine สำหรับชั้นนี้ได้

### API integration

ออกแบบ endpoints สำหรับ sample retrieval, analysis submission และ case retrieval ให้สัญญา request/response คงที่ที่สุด เพื่อให้ frontend พัฒนาต่อได้โดยไม่ต้องไล่แก้ API บ่อย

### UI development

รักษาจุดแข็งของเดโมปัจจุบันไว้ โดยเฉพาะ single-screen dashboard และส่วนแสดงภาพ overlay ที่ชัดเจน จากนั้นปรับถ้อยคำและลำดับการแสดงผลให้แยกชัดระหว่าง image findings, estimated risk และ projected outlook

### Testing

การทดสอบควรครอบคลุม:

- input validation tests
- API contract tests
- inference smoke tests
- visual regression checks สำหรับ sample cases
- human review ของความถูกต้องของ overlay และความสมเหตุสมผลของผลลัพธ์

ยังไม่จำเป็นต้องมี testing framework ขนาดใหญ่ในช่วงเริ่มต้น ชุดทดสอบเล็ก ๆ ที่เชื่อถือได้รอบ main flow ก็เพียงพอ

### Deployment

deploy frontend และ backend แยกกัน เก็บไฟล์ภาพใน object storage และให้ backend ชี้ไปยังตำแหน่ง model artifact ที่ชัดเจน ควรมี sample cases ฝังไว้ใน production environment ด้วย เพื่อให้การเดโมเสถียรแม้ user-uploaded inference จะยังมีข้อผิดพลาดบ้าง

### Prototype validation

การ validate prototype ไม่ควรดูแค่ technical metrics แต่ควรมี:

- end-to-end runs ที่สำเร็จจริง
- localization ที่ถูกต้องบน held-out validation set
- clinical face-validity review ของผลลัพธ์ด้านความเสี่ยง
- ข้อตกลงภายในทีมว่าระบบสาธิตแนวคิดได้ชัด โดยไม่กล่าวอ้างเกินจริง

## 9. Development Phases

### Phase 1: Scope and Data Audit

เป้าหมาย: กำหนดให้ชัดว่า prototype รุ่นแรกสามารถ “อ้างอะไรได้จริง”

งานหลัก:

- ตรวจทาน assets, labels และ formulas ที่มีใน repo
- ทำมาตรฐาน schema ของ clinical inputs
- audit คุณภาพ image labels และ dataset splits
- ตัดสินใจให้ชัดว่า starting model จะทำหน้าที่อะไรแน่นอน

ผลลัพธ์ที่คาดหวัง:

- prototype scope ที่ finalized
- dataset inventory ที่สะอาดและชัดเจน
- case schema และ result schema ที่นิ่ง

### Phase 2: Product Skeleton and Persistence

เป้าหมาย: เปลี่ยนเดโมปัจจุบันให้เป็น prototype shell ที่เก็บข้อมูลได้จริง

งานหลัก:

- รักษาโครง React และ FastAPI เดิม
- เพิ่ม PostgreSQL-backed case storage
- เพิ่ม object storage สำหรับ uploads และ overlays
- refactor static metadata flows ให้รองรับ database-backed records ตามความเหมาะสม

ผลลัพธ์ที่คาดหวัง:

- application shell ที่ deploy ได้และจัดการเคสแบบ persistent ได้

### Phase 3: Starting Vision Model

เป้าหมาย: แทนที่ visual output ที่พึ่ง metadata-only ด้วย model inference จริง

งานหลัก:

- เตรียม training data และ annotation format
- fine-tune pre-trained detector
- เพิ่ม model inference service เข้าสู่ backend
- validate localization quality ทั้งแบบ visual และเชิง metric

ผลลัพธ์ที่คาดหวัง:

- trained model รุ่นแรกที่ให้ box หรือ localization output ได้จริง

### Phase 4: Prognosis Engine Integration

เป้าหมาย: ผสาน image features และ clinical logic ให้กลายเป็น prototype output ที่มีความหมาย

งานหลัก:

- map ผลจาก detector เป็น structured features
- ผสาน growth formulas และ clinical bias logic
- นิยาม output metrics และ explanatory factors
- ทำให้ระบบ reproducible และ deterministic เท่าที่ทำได้

ผลลัพธ์ที่คาดหวัง:

- end-to-end hybrid analysis pipeline

### Phase 5: UI and User Flow Refinement

เป้าหมาย: ทำให้ระบบใช้งานได้ดีสำหรับ review, demo และ feedback

งานหลัก:

- ปรับความชัดเจนของผลลัพธ์และลำดับ section
- เพิ่ม status และ error handling ที่ดีขึ้น
- ทำให้ sample cases ใช้งานได้ตลอด
- ทบทวนถ้อยคำใน UI ให้ตีความได้ง่ายและระมัดระวัง

ผลลัพธ์ที่คาดหวัง:

- analyst-facing prototype dashboard ที่ใช้งานได้จริง

### Phase 6: Validation and Hosted Prototype

เป้าหมาย: สร้าง hosted prototype ที่เสถียรสำหรับทีมและผู้เกี่ยวข้อง

งานหลัก:

- deploy frontend และ backend
- seed sample cases
- รัน smoke tests และ clinical plausibility checks
- เขียนข้อจำกัดและ known gaps ให้ชัด

ผลลัพธ์ที่คาดหวัง:

- prototype environment ที่แชร์ได้ พร้อม validation notes

## 10. ความเสี่ยงและข้อพิจารณา

### ความเสี่ยงด้านเทคนิค

สถาปัตยกรรมปัจจุบันยังเรียบง่าย แต่เมื่อเพิ่ม model inference จะมีเรื่อง runtime, storage และ artifact management เข้ามา หากทีมพยายามยกหลายระบบพร้อมกันเกินไป prototype อาจเสถียรยากกว่าตัวโมเดลเอง

### ความเสี่ยงด้านข้อมูล

ความเสี่ยงที่สำคัญที่สุดคือคุณภาพ dataset ไม่ว่าจะเป็น synthetic fractures, จำนวนภาพเด็กที่จำกัด, มุมภาพไม่สม่ำเสมอ, annotation ที่ไม่คม หรือการไม่มี longitudinal labels ปัญหาเหล่านี้ทำให้ระบบดูน่าเชื่อถือบนเดโม แต่ยังอ่อนในเชิงคลินิกได้ง่าย ดังนั้น prototype รุ่นแรกจึงควรใช้ model scope แคบและ prognosis logic แบบ explicit

### ข้อจำกัดของโมเดล

detector ที่ localize รอยโรคได้ ไม่ได้แปลว่าระบบเข้าใจพฤติกรรมการเติบโตของกระดูกระยะยาวจริง ระบบต้องไม่สื่อว่าตัวเองเรียนรู้ long-term biological growth behavior จากข้อมูลจำกัด หากยังไม่พิสูจน์ได้จริง

### ความเสี่ยงด้านประสบการณ์ผู้ใช้

หากหน้าจอแสดง probability โดยไม่มีเหตุผลประกอบ ผู้ใช้อาจ overtrust หรือ dismiss ผลลัพธ์ไปเลย prototype จึงต้องแสดงให้ชัดว่าระบบเห็นอะไร ใช้อินพุตอะไร และให้ผลแบบนี้เพราะอะไร

### ข้อพิจารณาด้านคลินิกและ governance

หากในอนาคตใช้ patient data จริง จะต้องมี consent, governance และการจัดเก็บที่เหมาะสม แม้ตอนนี้จะยังใช้ open หรือ synthetic data แต่สถาปัตยกรรมไม่ควรออกแบบแบบที่ไม่ปลอดภัยไว้ถาวร

### ความกังวลด้าน scalability

prototype รุ่นแรกยังไม่จำเป็นต้องมี distributed inference หรือ orchestration ที่ซับซ้อน แต่ data model และ storage decisions ควรถูกออกแบบให้ไม่ล็อกทีมอยู่กับ static-demo architecture ที่ไม่สามารถขยายไปสู่ case history, model versioning หรือ validation workflows ได้

## 11. สิ่งที่ควรส่งมอบเมื่อจบเฟส Prototype

เมื่อสิ้นสุด prototype phase ทีมควรมี:

- frontend dashboard ที่ deploy ได้
- FastAPI backend ที่ deploy ได้
- persistent case and result store
- object storage สำหรับไฟล์ภาพต้นฉบับและไฟล์ที่สร้างขึ้น
- trained vision model รุ่นแรกสำหรับ physis-region localization
- hybrid prognosis engine ที่ผสานผลจากโมเดลกับ clinical logic
- analysis API contract ที่นิ่ง
- sample demo cases สำหรับ deterministic walkthrough
- technical documentation พื้นฐานสำหรับ setup, deployment และ limitations
- validation summary ที่อธิบายชัดว่าระบบพิสูจน์อะไรแล้ว และยังพิสูจน์อะไรไม่ได้

## สรุป

เส้นทางที่เหมาะสมที่สุดสำหรับ Bridge AI ไม่ใช่การกระโดดจาก mock demo ไปเป็น multimodal medical prognosis model เต็มรูปแบบทันที repository ปัจจุบันชี้ทางที่ดีกว่าอยู่แล้ว นั่นคือเก็บ dashboard และ API structure ที่มีอยู่ไว้ เพิ่ม vision model จริงเข้ามาก่อนหนึ่งส่วน และใช้ prognosis engine แบบ explicit ที่อาศัยทั้ง image-derived features และ structured clinical logic

แนวทางนี้ทำให้ prototype ใช้งานได้ อธิบายได้ และซื่อสัตย์ทางเทคนิค เมื่อทีมมีข้อมูลที่แข็งแรงขึ้น โดยเฉพาะ real longitudinal outcome data ค่อยพัฒนา Bridge AI ไปสู่ multimodal learning system ที่ลึกขึ้น ในช่วงนี้ สิ่งที่ถูกต้องที่สุดคือสร้าง hybrid prototype คุณภาพดีที่สาธิตคุณค่าทางคลินิกได้จริง โดยไม่พยายามแก้ปัญหาที่ยากที่สุดเร็วเกินไป
