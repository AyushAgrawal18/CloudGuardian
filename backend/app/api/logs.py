
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.logs import LogIn, LogOut
from backend.app.services.log_service import LogService


router = APIRouter(
    prefix="/api/v1/logs",
    tags=["Logs"],
)

log_service = LogService()


@router.post(
    "",
    response_model=LogOut,
    status_code=status.HTTP_201_CREATED,
)
def ingest_log(
    log: LogIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.OPERATOR)
    ),
):
    try:
        return log_service.ingest_log(
            db=db,
            host_id=log.host_id,
            timestamp=log.timestamp,
            severity=log.severity,
            message=log.message,
        )

    except ValueError as error:
        if str(error) == "Host not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            ) from error

        if str(error) == "Host is not active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(error),
            ) from error

        raise
