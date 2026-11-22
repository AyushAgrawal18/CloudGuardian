
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.config import THRESHOLDS, CRITICAL_MULTIPLIER
from backend.app.database import SessionLocal
from backend.app.models import Metric, Anomaly, Host, HostStatus
from backend.app.schemas.metrics import (
    AnomalyOut,
    HostStatusOut,
    MetricIn,
    MetricOut,
)
from backend.app.services.statistical_service import statistical_service

class HostNotRegisteredError(Exception):
    pass


class HostNotActiveError(Exception):
    pass


class MetricsService:
    def __init__(self):
        self._thresholds = THRESHOLDS.copy()
        self._statistical_window_size = statistical_service.window_size

        self._restore_statistical_history()

    def _restore_statistical_history(self) -> None:
        metric_names = list(self._thresholds.keys())

        with SessionLocal() as db:
            rows = db.scalars(
                select(Metric).order_by(
                    Metric.timestamp.desc(),
                    Metric.id.desc(),
                )
            ).all()

        host_rows = {}

        for row in rows:
            host_rows.setdefault(row.host_id, []).append(row)

        for host_id, records in host_rows.items():
            latest_records = records[:self._statistical_window_size]

            for metric_name in metric_names:
                values = [
                    float(getattr(row, metric_name))
                    for row in reversed(latest_records)
                ]

                statistical_service.restore_history(
                    host_id=host_id,
                    metric_name=metric_name,
                    values=values,
                )

    def _metric_out(self, record: Metric) -> MetricOut:
        return MetricOut(
            id=record.id,
            host_id=record.host_id,
            timestamp=record.timestamp,
            cpu_percent=record.cpu_percent,
            memory_percent=record.memory_percent,
            disk_percent=record.disk_percent,
            latency_ms=record.latency_ms,
            error_rate_percent=record.error_rate_percent,
            active_connections=record.active_connections,
            request_rate=record.request_rate,
            network_rtt_ms=record.network_rtt_ms,
        )

    def add_metric(self, metric: MetricIn) -> MetricOut:
        with SessionLocal.begin() as db:

            # Validate host registration
            host = db.scalar(
                select(Host).where(
                    Host.host_id == metric.host_id
                )
            )

            if host is None:
                raise HostNotRegisteredError(
                    f"Host '{metric.host_id}' is not registered"
                )

            # Only active hosts can submit metrics
            if host.status != HostStatus.ACTIVE:
                raise HostNotActiveError(
                    f"Host '{metric.host_id}' is not active"
                )

            # Store metric
            record = Metric(**metric.model_dump())

            db.add(record)
            db.flush()

            metric_out = self._metric_out(record)

            # Existing anomaly detection
            self._create_anomalies(db, metric_out)

        return metric_out

    def get_recent(
        self,
        limit: int = 50,
        host_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[MetricOut]:

        with SessionLocal() as db:
            query = select(Metric)

            if host_id:
                query = query.where(Metric.host_id == host_id)

            if start_time:
                query = query.where(Metric.timestamp >= start_time)

            if end_time:
                query = query.where(Metric.timestamp <= end_time)

            query = query.order_by(
                Metric.timestamp.desc(),
                Metric.id.desc(),
            ).limit(limit)

            records = db.scalars(query).all()

            return [
                self._metric_out(record)
                for record in records
            ]

    def get_anomalies(self, limit: int = 50) -> list[AnomalyOut]:
        with SessionLocal() as db:
            records = db.scalars(
                select(Anomaly)
                .order_by(
                    Anomaly.timestamp.desc(),
                    Anomaly.id.desc(),
                )
                .limit(limit)
            ).all()

            return [
                AnomalyOut(
                    id=record.id,
                    metric_id=record.metric_id,
                    host_id=record.host_id,
                    timestamp=record.timestamp,
                    metric_name=record.metric_name,
                    actual_value=record.actual_value,
                    threshold=record.threshold,
                    severity=record.severity,
                    explanation=record.explanation,
                )
                for record in records
            ]

    def get_host_statuses(self) -> list[HostStatusOut]:
        with SessionLocal() as db:
            query = (
                select(
                    Metric.host_id,
                    func.max(Metric.timestamp).label(
                        "latest_metric_timestamp"
                    ),
                    func.count(Anomaly.id).label("anomaly_count"),
                )
                .outerjoin(
                    Anomaly,
                    Anomaly.metric_id == Metric.id,
                )
                .group_by(Metric.host_id)
                .order_by(Metric.host_id)
            )

            rows = db.execute(query).all()

            return [
                HostStatusOut(
                    host_id=row.host_id,
                    status=(
                        "critical"
                        if row.anomaly_count >= 3
                        else "warning"
                        if row.anomaly_count
                        else "healthy"
                    ),
                    latest_metric_timestamp=row.latest_metric_timestamp,
                    anomaly_count=row.anomaly_count,
                )
                for row in rows
            ]

    def _create_anomalies(
        self,
        db: Session,
        record: MetricOut,
    ) -> None:

        # 1. Threshold-based anomaly detection
        for metric_name, threshold in self._thresholds.items():
            actual_value = getattr(record, metric_name)

            if actual_value < threshold:
                continue

            severity = (
                "critical"
                if actual_value >= threshold * CRITICAL_MULTIPLIER
                else "warning"
            )

            db.add(
                Anomaly(
                    metric_id=record.id,
                    host_id=record.host_id,
                    timestamp=record.timestamp,
                    metric_name=metric_name,
                    actual_value=actual_value,
                    threshold=threshold,
                    severity=severity,
                    explanation=(
                        f"{metric_name} reached {actual_value}, "
                        f"above the configured threshold of {threshold}"
                    ),
                )
            )

        # Flush threshold anomalies so they can be queried below.
        db.flush()

        # 2. Statistical anomaly detection
        for metric_name in self._thresholds:
            actual_value = getattr(record, metric_name)

            result = statistical_service.analyze(
                host_id=record.host_id,
                metric_name=metric_name,
                actual_value=actual_value,
            )

            if not result["is_anomaly"]:
                continue

            rolling_mean = result["rolling_mean"]
            rolling_std = result["rolling_std"]

            statistical_boundary = (
                rolling_mean
                if rolling_std is None or rolling_std == 0
                else rolling_mean
                + (1 if actual_value > rolling_mean else -1)
                * 3 * rolling_std
            )

            statistical_explanation = (
                f"{metric_name} is statistically unusual: "
                f"value {actual_value}, rolling mean {rolling_mean}, "
                f"z-score {result['z_score']}"
            )

            existing_anomaly = db.scalars(
                select(Anomaly).where(
                    Anomaly.metric_id == record.id,
                    Anomaly.metric_name == metric_name,
                )
            ).first()

            if existing_anomaly:
                existing_anomaly.explanation += (
                    "; " + statistical_explanation
                )
            else:
                db.add(
                    Anomaly(
                        metric_id=record.id,
                        host_id=record.host_id,
                        timestamp=record.timestamp,
                        metric_name=metric_name,
                        actual_value=actual_value,
                        threshold=statistical_boundary,
                        severity="warning",
                        explanation=statistical_explanation,
                    )
                )


metrics_service = MetricsService()
