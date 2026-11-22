
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    func,
)

from backend.app.database import Base


class HostStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)

    host_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(String(150), nullable=False)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)

    environment = Column(String(50), nullable=False)
    operating_system = Column(String(100), nullable=False)

    status = Column(
        Enum(HostStatus, name="host_status"),
        default=HostStatus.ACTIVE,
        nullable=False,
    )

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
