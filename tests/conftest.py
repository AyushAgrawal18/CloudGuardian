
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models import Metric, Anomaly, User
from backend.app.services import metrics_service as metrics_module
from backend.app.services.statistical_service import StatisticalService


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
