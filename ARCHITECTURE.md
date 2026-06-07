# Bridge AI Demo - Architecture & Design Document

## Overview

Bridge AI Demo is a Medical AI prototype for bone X-ray analysis with clinical decision support. Built for Medical AI Awards submission with focus on rapid prototyping and demonstration.

## Design Decisions

### 1. Platform: Web Application (React + FastAPI)

**Decision**: Web application with React frontend and FastAPI backend.

**Why**:
- Professional appearance for awards submission
- Easy to demo via screen recording
- Responsive UI possible with React
- Thai language support built-in

**Alternatives Considered**:
- Jupyter Notebook (too informal for submission)
- Desktop GUI (harder to demo, platform-specific)
- Streamlit (too basic for awards demo)

---

### 2. Architecture Pattern: Monorepo + Docker Compose

**Decision**: Single repository containing both backend and frontend, deployed via Docker Compose.

**Why**:
- Easy local development (single `docker-compose up`)
- Shareable with team members (Namthip, mentors)
- Clear separation of concerns
- Easy to expand later

**Folder Structure**:
```
/backend   - FastAPI application
/frontend  - React application
```

---

### 3. Frontend Stack: React + TypeScript + Tailwind CSS

**Decision**: React with TypeScript and Tailwind CSS for styling.

**Why**:
- Tailwind: Fast styling, responsive by default, great for prototypes
- TypeScript: Type safety reduces bugs
- React: Modern, component-based, easy to maintain

**UI Language**: Thai (ภาษาไทย) for all user-facing text

---

### 4. Backend Stack: FastAPI + Python

**Decision**: FastAPI framework with Python for core logic.

**Why**:
- Fast development (automatic API documentation)
- Python ecosystem (NumPy, PIL for image processing)
- Easy integration with ML/medical imaging libraries
- CORS support built-in

---

### 5. Data & Mock Implementation

**Decision**: Deterministic mock output based on clinical parameters.

**Parameters**:
- Age (อายุ)
- Gender (เพศ)
- Weight (น้ำหนัก)
- Height (ส่วนสูง)
- Bone Location (ตำแหน่งกระดูก): Medial (ด้านใน) / Lateral (ด้านนอก)

**Risk Score Logic**:
```
Primary Drivers: Age + Bone Location
- Age < 8 + Medial location → Risk: 70-90%
- Age < 8 + Lateral location → Risk: 50-70%
- Age 8-14 + Medial location → Risk: 50-70%
- Age 8-14 + Lateral location → Risk: 30-50%
- Age > 14 + Any location → Risk: 20-40%
```

**Output**:
- Risk Score: Percentage (0-100%)
- Heatmap: Intensity-based visualization overlay on X-ray
- Visualization: Base64-encoded PNG overlay on original image

---

### 6. X-ray Image Processing

**Decision**: Image overlay with opacity for heatmap visualization.

**Why**:
- Simple to implement (no complex libraries needed)
- Backend generates heatmap PNG
- Frontend overlays with CSS opacity
- Professional appearance

**Sample Data**: Open-source bone X-ray datasets
- Alternative: Synthetic X-ray images if needed

---

### 7. Database: SQLite

**Decision**: SQLite for data persistence.

**Why**:
- No external database server needed
- Perfect for prototype/local demo
- Easy to backup (single file)
- Sufficient for demo purposes

**Schema** (planned):
```
analysis_results:
  - id (primary key)
  - timestamp
  - age
  - gender
  - weight
  - height
  - bone_location (medial/lateral)
  - xray_image (file reference or base64)
  - heatmap_image (base64)
  - risk_score
  - created_at
```

---

### 8. UI Flow: Step-by-Step Form

**Decision**: Multi-step form with validation at each step.

**Steps**:
1. **Upload X-ray Image**
   - Image preview
   - Format validation (JPG, PNG)
   
2. **Clinical Parameters**
   - Age input (numeric)
   - Gender dropdown
   - Weight input
   - Height input
   - Bone Location dropdown (Medial/Lateral)
   
3. **Analyze & Results**
   - Show risk score percentage
   - Display heatmap overlay on X-ray
   - Risk level indicator (Low/Medium/High)
   - Option to export PDF or save to history

---

### 9. Report Export: PDF

**Decision**: PDF report generation using reportlab (already in system).

**Report Contents** (Detailed):
- Clinical input parameters
- X-ray image with heatmap overlay
- Risk score and interpretation
- Risk factors explanation (why this score?)
- Medical recommendations based on risk level
- Timestamp and analysis metadata

**Why Detailed Report**:
- Professional for awards submission
- Shows AI reasoning (not just a number)
- Supports medical decision-making workflow

---

### 10. History & Results Management

**Decision**: Full history tracking with ability to view and export previous analyses.

**Features**:
- Results list page showing all past analyses
- Search/filter by date or patient parameters
- Re-export any previous result as PDF
- Delete results option

**UI**: Dedicated "History" page with table of results

---

### 11. Language & Localization

**Decision**: Thai UI with English technical terms where appropriate.

**Principle**:
- User-facing buttons, labels, messages: Thai (ไทย)
- Technical terms (API, parameters): English
- Numbers and percentages: Same format across both

---

## Deployment & Running

### Local Development (Native)

```bash
# Backend
cd backend && pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm start
```

### Docker (Recommended for Demo)

```bash
docker-compose up
```

Access:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Implementation Roadmap

### Phase 1: Core Setup (Foundation)
- [ ] Database models and migrations
- [ ] FastAPI route structure and models
- [ ] React component structure and routing
- [ ] API integration (axios client)

### Phase 2: Analysis Pipeline
- [ ] Image upload handling
- [ ] Mock heatmap generation (NumPy)
- [ ] Risk score calculation logic
- [ ] Image overlay rendering

### Phase 3: UI Implementation
- [ ] Step 1: Image upload form
- [ ] Step 2: Clinical parameters form
- [ ] Step 3: Results display with heatmap
- [ ] Tailwind styling across all pages

### Phase 4: Features
- [ ] PDF report generation
- [ ] Results history and display
- [ ] Export functionality
- [ ] Thai language implementation

### Phase 5: Polish & Demo
- [ ] Error handling and validation
- [ ] Loading states and user feedback
- [ ] Performance optimization
- [ ] Screenshot/video recording optimization

---

## Key Technical Considerations

1. **Image Handling**: Store both original X-ray and heatmap for PDF export
2. **Heatmap Generation**: NumPy arrays converted to PIL Images → base64 for frontend
3. **CORS**: FastAPI configured to accept frontend requests
4. **State Management**: React hooks sufficient for this scope
5. **Type Safety**: TypeScript for frontend, Pydantic for backend

---

## Success Criteria for Demo

- [ ] Upload X-ray image successfully
- [ ] Input clinical parameters correctly
- [ ] Receive risk score with heatmap visualization
- [ ] Export PDF report with all information
- [ ] Save/retrieve from history
- [ ] Professional appearance in video recording
- [ ] Thai language UI complete

---

## Future Enhancements (Post-Awards)

- Real ML model integration
- Multi-image analysis
- Batch processing
- User authentication
- PostgreSQL migration for production
- CI/CD pipeline
- Unit and integration tests
