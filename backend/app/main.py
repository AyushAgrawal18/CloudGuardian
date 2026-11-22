
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.metrics import router as metrics_router
from backend.app.api.auth import router as auth_router


app = FastAPI(
    title="CloudGuardian API",
    description="AI-powered predictive maintenance and anomaly detection",
    version="0.3.0",
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


frontend_directory = Path(__file__).resolve().parents[2] / "frontend"

app.mount(
    "/dashboard",
    StaticFiles(directory=frontend_directory, html=True),
    name="dashboard",
)
