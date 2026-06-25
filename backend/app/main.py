from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import analyze, samples

app = FastAPI(title="Bridge AI Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(samples.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Bridge AI Demo API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
