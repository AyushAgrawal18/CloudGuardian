
from fastapi import APIRouter, Query

from backend.app.schemas.metrics import AnomalyOut, HostStatusOut, MetricIn, MetricOut
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


@router.get("/anomalies", response_model=list[AnomalyOut])
def get_anomalies(
    limit: int = Query(default=50, ge=1, le=1000),
):
    return metrics_service.get_anomalies(limit)


@router.get("/hosts", response_model=list[HostStatusOut])
def get_host_statuses():
    return metrics_service.get_host_statuses()
