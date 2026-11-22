
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.database import get_db
from backend.app.models.host import HostStatus
from backend.app.models.user import User, UserRole
from backend.app.schemas.hosts import (
    HostCreate,
    HostUpdate,
    HostResponse,
)
from backend.app.services.host_service import (
    host_service,
    HostAlreadyExistsError,
    HostNotFoundError,
)


router = APIRouter(
    prefix="/api/v1/hosts",
    tags=["Hosts"],
)


@router.post(
    "",
    response_model=HostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_host(
    host_data: HostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    try:
        return host_service.create_host(db, host_data)

    except HostAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get("", response_model=list[HostResponse])
def get_hosts(
    host_status: HostStatus | None = Query(default=None, alias="status"),
    environment: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
):
    return host_service.get_hosts(
        db,
        status=host_status,
        environment=environment,
    )


@router.get("/{host_id}", response_model=HostResponse)
def get_host(
    host_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.VIEWER,
        )
    ),
):
    try:
        return host_service.get_host(db, host_id)

    except HostNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch("/{host_id}", response_model=HostResponse)
def update_host(
    host_id: str,
    host_data: HostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    try:
        return host_service.update_host(
            db,
            host_id,
            host_data,
        )

    except HostNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete("/{host_id}", response_model=HostResponse)
def deactivate_host(
    host_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    try:
        return host_service.deactivate_host(db, host_id)

    except HostNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
