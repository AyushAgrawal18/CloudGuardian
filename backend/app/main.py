
from fastapi import FastAPI

from backend.app.api.metrics import router as metrics_router

app = FastAPI(
    title="CloudGuardian API",
    description="AI-powered predictive maintenance and anomaly detection",
    version="0.2.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cloudguardian-api",
        "version": "0.2.0",
    }


app.include_router(metrics_router)
