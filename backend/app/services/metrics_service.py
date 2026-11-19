
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from backend.app.core.config import THRESHOLDS, CRITICAL_MULTIPLIER
from backend.app.services.statistical_service import statistical_service

from backend.app.schemas.metrics import AnomalyOut, HostStatusOut, MetricIn, MetricOut


class MetricsService:
    def __init__(self):
        configured_path = os.getenv("CLOUDGUARDIAN_DB_PATH", "backend/cloudguardian.db")
        self._database_path = Path(configured_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._thresholds =  THRESHOLDS.copy()
        self._initialise_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    disk_percent REAL NOT NULL,
                    latency_ms REAL NOT NULL,
                    error_rate_percent REAL NOT NULL,
                    active_connections INTEGER NOT NULL,
                    request_rate REAL NOT NULL,
                    network_rtt_ms REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    host_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    actual_value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    severity TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    FOREIGN KEY(metric_id) REFERENCES metrics(id)
                );
                """
            )

    def add_metric(self, metric: MetricIn) -> MetricOut:
        values = metric.model_dump()
        values["timestamp"] = values["timestamp"].isoformat()
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)

        with self._connect() as connection:
            cursor = connection.execute(
                f"INSERT INTO metrics ({columns}) VALUES ({placeholders})",
                tuple(values.values()),
            )
            metric_id = cursor.lastrowid
            record = MetricOut(id=metric_id, **metric.model_dump())
            self._create_anomalies(connection, record)

        return record

    def get_recent(
        self,
        limit: int = 50,
        host_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[MetricOut]:
        query = "SELECT * FROM metrics"
        conditions = []
        parameters = []

        if host_id:
            conditions.append("host_id = ?")
            parameters.append(host_id)

        if start_time:
            conditions.append("timestamp >= ?")
            parameters.append(start_time.isoformat())

        if end_time:
            conditions.append("timestamp <= ?")
            parameters.append(end_time.isoformat())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC, id DESC LIMIT ?"
        parameters.append(limit)

        with self._connect() as connection:
            rows = connection.execute(
                query,
                tuple(parameters),
            ).fetchall()
            
        return [MetricOut(**dict(row)) for row in rows]
    
    

    def get_anomalies(self, limit: int = 50) -> list[AnomalyOut]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM anomalies ORDER BY timestamp DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [AnomalyOut(**dict(row)) for row in rows]

    def get_host_statuses(self) -> list[HostStatusOut]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                  SELECT metrics.host_id, MAX(metrics.timestamp) AS latest_metric_timestamp,
                       COUNT(anomalies.id) AS anomaly_count
                FROM metrics
                LEFT JOIN anomalies ON anomalies.metric_id = metrics.id
                GROUP BY metrics.host_id
                ORDER BY metrics.host_id
                """
            ).fetchall()

        return [
            HostStatusOut(
                host_id=row["host_id"],
                status=("critical" if row["anomaly_count"] >= 3 else "warning" if row["anomaly_count"] else "healthy"),
                latest_metric_timestamp=row["latest_metric_timestamp"],
                anomaly_count=row["anomaly_count"],
            )
            for row in rows
        ]

    def _create_anomalies(
        self,
        connection: sqlite3.Connection,
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

            connection.execute(
                """
                INSERT INTO anomalies (
                    metric_id, host_id, timestamp, metric_name, actual_value,
                    threshold, severity, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.host_id,
                    record.timestamp.isoformat(),
                    metric_name,
                    actual_value,
                    threshold,
                    severity,
                    f"{metric_name} reached {actual_value}, above the configured threshold of {threshold}",
                ),
            )

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

            # Check whether threshold detection already created an anomaly.
            existing_anomaly = connection.execute(
                """
                SELECT id, explanation
                FROM anomalies
                WHERE metric_id = ? AND metric_name = ?
                """,
                (record.id, metric_name),
            ).fetchone()

            if existing_anomaly:
                # Combine both detection explanations into one record.
                connection.execute(
                    """
                    UPDATE anomalies
                    SET explanation = ?
                    WHERE id = ?
                    """,
                    (
                        existing_anomaly["explanation"]
                        + "; "
                        + statistical_explanation,
                        existing_anomaly["id"],
                    ),
                )
            else:
                # Insert a separate statistical anomaly.
                connection.execute(
                    """
                    INSERT INTO anomalies (
                        metric_id, host_id, timestamp, metric_name,
                        actual_value, threshold, severity, explanation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        record.host_id,
                        record.timestamp.isoformat(),
                        metric_name,
                        actual_value,
                        statistical_boundary,
                        "warning",
                        statistical_explanation,
                    ),
                )

metrics_service = MetricsService()
