
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MetricIn(BaseModel):
    host_id: str = Field(min_length=1, max_length=100)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)

    latency_ms: float = Field(ge=0)
    error_rate_percent: float = Field(ge=0, le=100)

    active_connections: int = Field(ge=0)
    request_rate: float = Field(ge=0)
    network_rtt_ms: float = Field(ge=0)


class MetricOut(MetricIn):
    id: int


class AnomalyOut(BaseModel):
    id: int
    metric_id: int
    host_id: str
    timestamp: datetime
    metric_name: str
    actual_value: float
    threshold: float
    severity: str
    explanation: str


class HostStatusOut(BaseModel):
    host_id: str
    status: str
    latest_metric_timestamp: datetime | None = None
    anomaly_count: int
