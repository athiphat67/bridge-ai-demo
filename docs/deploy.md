# Deploy Guide

This repo ships as two apps:

- `frontend/` React + Vite
- `backend/` FastAPI

## Local

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

If the frontend needs the backend URL in local dev, leave `VITE_API_URL` unset. The Vite proxy already sends `/api` to `http://localhost:8000`.

## Vercel

Use two Vercel projects.

Frontend project:

1. Import the repo.
2. Set `Root Directory` to `frontend`.
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add `VITE_API_URL` = backend deployment URL.

Backend project:

1. Create a second project from the same repo.
2. Set `Root Directory` to `backend`.
3. Let Vercel detect FastAPI.
4. Deploy.

## After Deploy

Set the frontend env var:

```bash
VITE_API_URL=https://your-backend.vercel.app
```

Then redeploy the frontend so it bakes in the new API base URL.

## Notes

- If the repo does not show up in Vercel import, you can still deploy with the CLI if your Git/Vercel login has access.
- If you are only a contributor, you can deploy your own Vercel project, but you may need the repo owner to grant access to the Git repo or the Vercel team.
