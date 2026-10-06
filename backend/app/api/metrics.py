
from fastapi import APIRouter, Query

from backend.app.schemas.metrics import MetricIn, MetricOut
from backend.app.services.metrics_service import metrics_service

router = APIRouter(
    prefix="/api/v1/metrics",
    tags=["Metrics"],
)


@router.post("", response_model=MetricOut, status_code=201)
def ingest_metric(metric: MetricIn):
    return metrics_service.add_metric(metric)


@router.get("", response_model=list[MetricOut])
def get_metrics(
    limit: int = Query(default=50, ge=1, le=1000),
):
    return metrics_service.get_recent(limit)
