
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.user import User, UserRole
from backend.app.core.security import hash_password, verify_password
from backend.app.schemas.auth import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
)


class EmailAlreadyRegisteredError(Exception):
    pass


class AuthService:

    def register_user(
        self,
        db: Session,
        user_data: RegisterRequest,
    ) -> UserResponse:

        existing_user = db.scalar(
            select(User).where(
                User.email == str(user_data.email).lower()
            )
        )

        if existing_user:
            raise EmailAlreadyRegisteredError(
                "An account with this email already exists"
            )

        user = User(
            email=str(user_data.email).lower(),
            full_name=user_data.full_name.strip(),
            hashed_password=hash_password(user_data.password),
            role=UserRole.VIEWER,
            is_active=True,
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

        except IntegrityError:
            db.rollback()
            raise EmailAlreadyRegisteredError(
                "An account with this email already exists"
            )

        return UserResponse.model_validate(user)


    def authenticate_user(
        self,
        db: Session,
        credentials: LoginRequest,
    ) -> User | None:

        user = db.scalar(
            select(User).where(
                User.email == str(credentials.email).lower()
            )
        )

        if not user or not user.is_active:
            return None

        if not verify_password(
            credentials.password,
            user.hashed_password,
        ):
            return None

        return user

auth_service = AuthService()
