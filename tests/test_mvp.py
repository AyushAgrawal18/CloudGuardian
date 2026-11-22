
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.api import metrics as metrics_api
from backend.app.core.jwt import create_access_token
from backend.app.core.security import hash_password
from backend.app.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.services.metrics_service import MetricsService
from backend.app.models.host import Host, HostStatus



def test_metric_service_persists_and_detects_anomaly(isolated_database):
    # Register host in the isolated test database first.
    with isolated_database() as db:
        host = Host(
            host_id="host-1",
            name="Test Server",
            hostname="test-server",
            ip_address="192.168.1.10",
            environment="testing",
            operating_system="Ubuntu 24.04",
            status=HostStatus.ACTIVE,
        )

        db.add(host)
        db.commit()

    service = MetricsService()

    service.add_metric(
        metrics_api.MetricIn(
            host_id="host-1",
            cpu_percent=95,
            memory_percent=40,
            disk_percent=45,
            latency_ms=80,
            error_rate_percent=0.5,
            active_connections=20,
            request_rate=100,
            network_rtt_ms=25,
        )
    )

    assert len(service.get_recent()) == 1
    assert len(service.get_anomalies()) == 1
    assert service.get_host_statuses()[0].status == "warning"


def test_api_accepts_metrics_and_serves_dashboard(isolated_database):
    metrics_api.metrics_service = MetricsService()

    payload = {
        "host_id": "host-1",
        "cpu_percent": 95,
        "memory_percent": 40,
        "disk_percent": 45,
        "latency_ms": 80,
        "error_rate_percent": 0.5,
        "active_connections": 20,
        "request_rate": 100,
        "network_rtt_ms": 25,
    }

    # Create an OPERATOR in the isolated test database.
    with isolated_database() as db:
        operator = User(
            email="operator@test.com",
            full_name="Test Operator",
            hashed_password=hash_password("TestPassword@123"),
            role=UserRole.OPERATOR,
            is_active=True,
        )

        db.add(operator)

        host = Host(
            host_id="host-1",
            name="Test Server",
            hostname="test-server",
            ip_address="192.168.1.10",
            environment="testing",
            operating_system="Ubuntu 24.04",
            status=HostStatus.ACTIVE,
        )

        db.add(host)
        db.commit()
        db.refresh(operator)

        token = create_access_token(subject=str(operator.id))

    # Override the database dependency for this test.
    def override_get_db():
        db = isolated_database()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        with TestClient(main.app) as client:
            response = client.post(
                "/api/v1/metrics",
                json=payload,
                headers=headers,
            )

            assert response.status_code == 201

            metrics_response = client.get(
                "/api/v1/metrics",
                headers=headers,
            )

            assert metrics_response.status_code == 200
            assert len(metrics_response.json()) == 1

            anomalies_response = client.get(
                "/api/v1/metrics/anomalies",
                headers=headers,
            )

            assert len(anomalies_response.json()) == 1

            hosts_response = client.get(
                "/api/v1/metrics/hosts",
                headers=headers,
            )

            assert hosts_response.json()[0]["status"] == "warning"

            assert client.get("/dashboard/").status_code == 200

    finally:
        main.app.dependency_overrides.pop(get_db, None)
