# BRIDGE-AI — Pediatric Knee Growth-Plate Risk Prototype

**An AI-assisted prototype that reads a child's knee X-ray, finds the growth plate, flags likely fractures, and turns them into a risk summary a clinician can explain to a family.**

![Selected](https://img.shields.io/badge/BRIDGE--AI_Summit_2026-Selected_exhibitor_(90_of_230%2B)-success)
![Host](https://img.shields.io/badge/Chulalongkorn-Faculty_of_Medicine-B71C1C)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React_+_Vite-61DAFB?logo=react&logoColor=black)
![ONNX](https://img.shields.io/badge/ONNX-OpenCV_DNN-005CED?logo=onnx&logoColor=white)

> **Role:** Tech Lead, Data Scientist & AI Engineer (team of 4) · **When:** Jun – Jul 2026
> ⚠️ Research prototype for a competition. **Not a medical device** and not for clinical decisions.

---

## The problem

When a child injures the growth plate (physis) near the knee, the first X-ray shows the damage. It does **not** show what happens later: the bone may stop growing, bend (varus/valgus), or end up shorter than the other leg. Today the answer comes from months of follow-up and the doctor's judgement. Families meanwhile have little to plan around.

**Goal:** give the doctor an early, explainable risk estimate and a clear visual to share with the family. Clinical follow-up stays in charge.

## How it works

```
X-ray upload + clinical inputs (age, sex, injury location)
  ▼ C1  YOLOv8n growth-plate detector (ONNX)   → bounding box on the physis
  ▼ C2  ResNet-18 fracture classifier (ONNX)    → fracture / no fracture + confidence
  ▼ Rule-based scoring                            → damage %, Low / Medium / High risk,
                                                    1 / 3 / 5-year growth outlook
  ▼ React dashboard                               → overlay + heatmap + risk badge + charts (Thai UI)
```

- **Models run without PyTorch.** Both networks are exported to ONNX and served via OpenCV DNN ([`backend/app/services/vision.py`](backend/app/services/vision.py)), so the API stays small enough for serverless hosting.
- **Scoring is transparent on purpose.** Risk and growth outlook come from explicit formulas ([`scoring.py`](backend/app/services/scoring.py), [`growth.py`](backend/app/services/growth.py)), not a black box. A clinician can see why a case is "High".

## Results

The models were trained in a separate (private) training repo and documented in a model card. Results use 5-fold cross-validation:

| Component | Metric | Result | Baseline |
|---|---|---|---|
| C1 growth-plate detector (YOLOv8n) | mAP@0.5 | **0.928** | — |
| C2 fracture classifier (ResNet-18) | Accuracy | **0.902** | 0.804 |
| C2 fracture classifier | Fracture recall | 0.67 | — |

**Read with care:** the classifier saw only **55 X-rays (18 fractures)**. A recall of 0.67 means about 1 in 3 fractures is missed. That is the main reason this stays a prototype, and more labelled data is the first next step.

## My role

- Led research and system design: framed the clinical problem, chose the two-stage detect → classify design, and defined the scoring outputs.
- Trained the growth-plate detector and the fracture classifier, and wrote the model card with the cross-validation results.

## Run it

**Docker (one command):**

```bash
npm run up          # backend → http://localhost:8000/docs · frontend → http://localhost:5173
npm run up:build    # rebuild images
```

**Native:**

```bash
# backend
cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload

# frontend (new terminal)
cd frontend && npm install && npm run dev
```

### API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/samples` | Sample cases (Normal / Low / Medium / High) |
| `POST` | `/api/analyze` | X-ray + clinical inputs → overlay, damage %, risk level, growth outlook. `mode=sample` + `sample_id`, or `mode=real` + `image` (≤ 4 MB) |

Deployment notes (two Vercel projects, `frontend/` and `backend/`) are in [`docs/deploy.md`](docs/deploy.md). Design notes and the development process are in [`docs/`](docs/) (Thai).

## Repository map

```
backend/            FastAPI API · ONNX models in backend/app/models/
frontend/           React + Vite + Tailwind dashboard
Working Prototype/  Stand-alone prognosis pipeline + demo cases
scripts/            Builds demo data from data/
docs/               Proposal, development process, team notes
```

## Team

Athiphat Sunsit (tech lead) · Purich Ampawa · and teammates. Built for the **BRIDGE-AI Summit 2026**, Faculty of Medicine, Chulalongkorn University.
