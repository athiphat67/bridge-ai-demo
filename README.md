# Bridge AI Demo

A Medical AI demo application for bone X-ray analysis with risk scoring, developed for the Medical AI Awards submission.

## Features

- Upload and analyze bone X-ray images
- Clinical parameter input (age, gender, weight, height, bone location)
- AI-powered risk score calculation with heatmap visualization
- PDF report generation
- Analysis history management
- Thai language UI

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: SQLite
- **Deployment**: Docker Compose

## Project Structure

```
bridge-ai-demo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── services/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── data/
│       └── sample_images/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start (Docker)

```bash
docker-compose up
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

## Development (Native)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze` - Analyze X-ray image
- `GET /api/results` - Get analysis results history
- `GET /api/results/{id}` - Get specific result
- `POST /api/results/{id}/export` - Export result as PDF

## Architecture Decisions

See `ARCHITECTURE.md` for detailed design decisions and rationale.
