
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models import Metric, Anomaly, User, Host
from backend.app.services import metrics_service as metrics_module
from backend.app.services.statistical_service import StatisticalService

from fastapi.testclient import TestClient

from backend.app import main
from backend.app.core.jwt import create_access_token
from backend.app.core.security import hash_password
from backend.app.database import get_db
from backend.app.models.user import UserRole


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(
        metrics_module,
        "SessionLocal",
        TestingSessionLocal,
    )

    monkeypatch.setattr(
        metrics_module,
        "statistical_service",
        StatisticalService(window_size=20),
    )

    yield TestingSessionLocal

    engine.dispose()
    
    
    
    
@pytest.fixture
def client_with_role(isolated_database):

    def override_get_db():
        db = isolated_database()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db

    def create_user_and_token(role: UserRole):
        with isolated_database() as db:
            user = User(
                email=f"{role.value}@test.com",
                full_name=f"Test {role.value}",
                hashed_password=hash_password("TestPassword@123"),
                role=role,
                is_active=True,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            token = create_access_token(subject=str(user.id))

        return {"Authorization": f"Bearer {token}"}

    try:
        with TestClient(main.app) as client:
            yield client, create_user_and_token
    finally:
        main.app.dependency_overrides.pop(get_db, None)
