
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.host import Host, HostStatus
from backend.app.schemas.hosts import (
    HostCreate,
    HostUpdate,
    HostResponse,
)


class HostAlreadyExistsError(Exception):
    pass


class HostNotFoundError(Exception):
    pass


class HostService:

    def create_host(
        self,
        db: Session,
        host_data: HostCreate,
    ) -> HostResponse:

        existing_host = db.scalar(
            select(Host).where(
                Host.host_id == host_data.host_id
            )
        )

        if existing_host:
            raise HostAlreadyExistsError(
                "A host with this ID already exists"
            )

        host = Host(
            host_id=host_data.host_id,
            name=host_data.name,
            hostname=host_data.hostname,
            ip_address=str(host_data.ip_address),
            environment=host_data.environment,
            operating_system=host_data.operating_system,
            status=HostStatus.ACTIVE,
        )

        try:
            db.add(host)
            db.commit()
            db.refresh(host)

        except IntegrityError:
            db.rollback()
            raise HostAlreadyExistsError(
                "A host with this ID already exists"
            )

        return HostResponse.model_validate(host)

    def get_host(
        self,
        db: Session,
        host_id: str,
    ) -> HostResponse:

        host = db.scalar(
            select(Host).where(Host.host_id == host_id)
        )

        if not host:
            raise HostNotFoundError("Host not found")

        return HostResponse.model_validate(host)

    def get_hosts(
        self,
        db: Session,
        status: HostStatus | None = None,
        environment: str | None = None,
    ) -> list[HostResponse]:

        query = select(Host).order_by(Host.created_at.desc())

        if status is not None:
            query = query.where(Host.status == status)

        if environment is not None:
            query = query.where(
                Host.environment == environment
            )

        hosts = db.scalars(query).all()

        return [
            HostResponse.model_validate(host)
            for host in hosts
        ]

    def update_host(
        self,
        db: Session,
        host_id: str,
        host_data: HostUpdate,
    ) -> HostResponse:

        host = db.scalar(
            select(Host).where(Host.host_id == host_id)
        )

        if not host:
            raise HostNotFoundError("Host not found")

        update_data = host_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "ip_address" in update_data:
            update_data["ip_address"] = str(
                update_data["ip_address"]
            )

        for field, value in update_data.items():
            setattr(host, field, value)

        db.commit()
        db.refresh(host)

        return HostResponse.model_validate(host)

    def deactivate_host(
        self,
        db: Session,
        host_id: str,
    ) -> HostResponse:

        host = db.scalar(
            select(Host).where(Host.host_id == host_id)
        )

        if not host:
            raise HostNotFoundError("Host not found")

        host.status = HostStatus.INACTIVE

        db.commit()
        db.refresh(host)

        return HostResponse.model_validate(host)


host_service = HostService()
