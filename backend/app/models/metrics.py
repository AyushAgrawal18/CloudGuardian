from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from backend.app.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    disk_percent = Column(Float, nullable=False)

    latency_ms = Column(Float, nullable=False)
    error_rate_percent = Column(Float, nullable=False)

    active_connections = Column(Integer, nullable=False)
    request_rate = Column(Float, nullable=False)
    network_rtt_ms = Column(Float, nullable=False)


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)

    metric_id = Column(
        Integer,
        ForeignKey("metrics.id"),
        nullable=False,
        index=True,
    )

    host_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    metric_name = Column(String(100), nullable=False)
    actual_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)

    severity = Column(String(20), nullable=False)
    explanation = Column(String, nullable=False)