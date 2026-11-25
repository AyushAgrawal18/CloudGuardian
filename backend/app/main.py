
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.metrics import router as metrics_router
from backend.app.api.auth import router as auth_router
from backend.app.api.hosts import router as hosts_router
from backend.app.api.logs import router as logs_router

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="CloudGuardian API",
    description="AI-powered predictive maintenance and anomaly detection",
    version="0.3.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cloudguardian-api",
        "version": "0.3.0",
    }


app.include_router(metrics_router)
app.include_router(auth_router)
app.include_router(hosts_router)
app.include_router(logs_router)


frontend_directory = Path(__file__).resolve().parents[2] / "frontend"

app.mount(
    "/dashboard",
    StaticFiles(directory=frontend_directory, html=True),
    name="dashboard",
)
