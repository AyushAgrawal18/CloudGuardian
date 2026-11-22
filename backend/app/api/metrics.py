
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from backend.app.models.user import User, UserRole
from backend.app.api.dependencies import require_roles
from backend.app.schemas.metrics import (
    AnomalyOut,
    HostStatusOut,
    MetricIn,
    MetricOut,
)
from fastapi import HTTPException, status

from backend.app.services.metrics_service import (
    metrics_service,
    HostNotRegisteredError,
    HostNotActiveError,
)

router = APIRouter(
    prefix="/api/v1/metrics",
    tags=["Metrics"],
)


@router.post(
    "",
    response_model=MetricOut,
    status_code=201,
)
def ingest_metric(
    metric: MetricIn,
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.OPERATOR)
    ),
):
    try:
        return metrics_service.add_metric(metric)

    except HostNotRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except HostNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

@router.get("", response_model=list[MetricOut])
def get_metrics(
    limit: int = Query(default=50, ge=1, le=1000),
    host_id: str | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
):
    return metrics_service.get_recent(
        limit=limit,
        host_id=host_id,
        start_time=start_time,
        end_time=end_time,
    )


@router.get("/anomalies", response_model=list[AnomalyOut])
def get_anomalies(
    limit: int = Query(default=50, ge=1, le=1000),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
):
    return metrics_service.get_anomalies(limit)


@router.get("/hosts", response_model=list[HostStatusOut])
def get_host_statuses(
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
):
    return metrics_service.get_host_statuses()
