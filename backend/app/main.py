from fastapi import FastAPI

app = FastAPI(
    title="CloudGuardian API",
    description="AI-powered predictive maintenance and anomaly detection",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cloudguardian-api",
        "version": "0.1.0",
    }
