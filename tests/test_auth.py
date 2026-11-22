
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import get_db


def test_user_registration(isolated_database):
    def override_get_db():
        db = isolated_database()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "password": "CloudGuardian@123",
                },
            )

            assert response.status_code == 201
            assert response.json()["email"] == "test@example.com"
            assert response.json()["role"] == "viewer"
            assert "hashed_password" not in response.json()
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_duplicate_email_registration(isolated_database):
    def override_get_db():
        db = isolated_database()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            payload = {
                "email": "duplicate@example.com",
                "full_name": "Test User",
                "password": "CloudGuardian@123",
            }

            first = client.post("/api/v1/auth/register", json=payload)
            second = client.post("/api/v1/auth/register", json=payload)

            assert first.status_code == 201
            assert second.status_code == 409
    finally:
        app.dependency_overrides.pop(get_db, None)
