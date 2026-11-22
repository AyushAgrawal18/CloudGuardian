
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.core.jwt import create_access_token
from backend.app.core.security import hash_password
from backend.app.database import get_db
from backend.app.models.user import User, UserRole


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

    with TestClient(main.app) as client:
        yield client, create_user_and_token

    main.app.dependency_overrides.pop(get_db, None)


METRIC_PAYLOAD = {
    "host_id": "rbac-host",
    "cpu_percent": 45,
    "memory_percent": 40,
    "disk_percent": 30,
    "latency_ms": 80,
    "error_rate_percent": 0.5,
    "active_connections": 20,
    "request_rate": 100,
    "network_rtt_ms": 25,
}


def test_metrics_rejects_missing_token(client_with_role):
    client, _ = client_with_role

    response = client.get("/api/v1/metrics")

    assert response.status_code == 401


def test_viewer_can_read_metrics_but_cannot_ingest(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.VIEWER)

    read_response = client.get(
        "/api/v1/metrics",
        headers=headers,
    )

    write_response = client.post(
        "/api/v1/metrics",
        json=METRIC_PAYLOAD,
        headers=headers,
    )

    assert read_response.status_code == 200
    assert write_response.status_code == 403


@pytest.mark.parametrize(
    "role",
    [UserRole.OPERATOR, UserRole.ADMIN],
)
def test_operator_and_admin_can_ingest_metrics(
    client_with_role,
    role,
):
    client, create_token = client_with_role
    headers = create_token(role)

    response = client.post(
        "/api/v1/metrics",
        json=METRIC_PAYLOAD,
        headers=headers,
    )

    assert response.status_code == 201


def test_metrics_rejects_invalid_token(client_with_role):
    client, _ = client_with_role

    response = client.get(
        "/api/v1/metrics",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
