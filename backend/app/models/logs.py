
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)

from backend.app.database import Base


class LogTemplate(Base):
    __tablename__ = "log_templates"

    id = Column(Integer, primary_key=True, index=True)

    host_id = Column(
        String(100),
        ForeignKey("hosts.host_id"),
        nullable=False,
        index=True,
    )

    cluster_id = Column(Integer, nullable=False)
    template = Column(Text, nullable=False)
    cluster_size = Column(Integer, default=1, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "host_id",
            "cluster_id",
            name="uq_log_template_host_cluster",
        ),
    )


class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(Integer, primary_key=True, index=True)

    host_id = Column(
        String(100),
        ForeignKey("hosts.host_id"),
        nullable=False,
        index=True,
    )

    template_id = Column(
        Integer,
        ForeignKey("log_templates.id"),
        nullable=False,
        index=True,
    )

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    severity = Column(String(20), nullable=False, default="INFO")
    message = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
