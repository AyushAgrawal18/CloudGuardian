
import pytest

from backend.app.models.user import UserRole
from backend.app.api.logs import log_service
from backend.app.services.log_parser import LogParser


LOG_PAYLOAD = {
    "host_id": "server-01",
    "severity": "ERROR",
    "message": "Database connection timeout",
}


@pytest.fixture(autouse=True)
def isolated_log_parser(monkeypatch, tmp_path):
    monkeypatch.setattr(
        log_service,
        "parser",
        LogParser(state_dir=str(tmp_path)),
    )


def create_host(client, headers):
    return client.post(
        "/api/v1/hosts",
        json={
            "host_id": "server-01",
            "name": "Production Server",
            "hostname": "prod-server-01",
            "ip_address": "192.168.1.10",
            "environment": "production",
            "operating_system": "Ubuntu 24.04",
        },
        headers=headers,
    )


def test_operator_can_ingest_log(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    operator_headers = create_token(UserRole.OPERATOR)

    create_host(client, admin_headers)

    response = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
        headers=operator_headers,
    )

    assert response.status_code == 201
    assert response.json()["host_id"] == "server-01"
    assert response.json()["severity"] == "ERROR"
    assert response.json()["message"] == LOG_PAYLOAD["message"]


def test_log_template_deduplication(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    operator_headers = create_token(UserRole.OPERATOR)

    create_host(client, admin_headers)

    first = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
        headers=operator_headers,
    )

    second = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
        headers=operator_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["template_id"] == second.json()["template_id"]


def test_log_secrets_are_redacted(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    operator_headers = create_token(UserRole.OPERATOR)

    create_host(client, admin_headers)

    payload = {
        **LOG_PAYLOAD,
        "message": "Authentication failed password=SuperSecret123",
    }

    response = client.post(
        "/api/v1/logs",
        json=payload,
        headers=operator_headers,
    )

    assert response.status_code == 201
    assert "SuperSecret123" not in response.json()["message"]
    assert "[REDACTED]" in response.json()["message"]


def test_log_ingestion_rejects_unknown_host(client_with_role):
    client, create_token = client_with_role
    operator_headers = create_token(UserRole.OPERATOR)

    response = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
        headers=operator_headers,
    )

    assert response.status_code == 404


def test_log_ingestion_rejects_inactive_host(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    operator_headers = create_token(UserRole.OPERATOR)

    create_host(client, admin_headers)

    deactivate_response = client.delete(
        "/api/v1/hosts/server-01",
        headers=admin_headers,
    )

    assert deactivate_response.status_code == 200

    response = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
        headers=operator_headers,
    )

    assert response.status_code == 409


def test_viewer_cannot_ingest_logs(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    viewer_headers = create_token(UserRole.VIEWER)

    create_host(client, admin_headers)

    response = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
        headers=viewer_headers,
    )

    assert response.status_code == 403


def test_log_ingestion_rejects_missing_token(client_with_role):
    client, _ = client_with_role

    response = client.post(
        "/api/v1/logs",
        json=LOG_PAYLOAD,
    )

    assert response.status_code == 401


def test_log_ingestion_validates_severity(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    operator_headers = create_token(UserRole.OPERATOR)

    create_host(client, admin_headers)

    payload = {
        **LOG_PAYLOAD,
        "severity": "INVALID",
    }

    response = client.post(
        "/api/v1/logs",
        json=payload,
        headers=operator_headers,
    )

    assert response.status_code == 422




def test_failed_log_insert_rolls_back_template(
    client_with_role, isolated_database, monkeypatch
):
    from backend.app.api.logs import log_service
    from backend.app.models.logs import LogEvent, LogTemplate

    client, create_token = client_with_role
    admin_headers = create_token(UserRole.ADMIN)

    create_host(client, admin_headers)

    # Use the isolated SQLite test database.
    db = isolated_database()

    original_commit = db.commit

    def failing_commit():
        raise RuntimeError("Simulated database failure")

    monkeypatch.setattr(db, "commit", failing_commit)

    try:
        with pytest.raises(RuntimeError, match="Simulated database failure"):
            log_service.ingest_log(
                db=db,
                host_id="server-01",
                timestamp=__import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ),
                severity="ERROR",
                message="Database connection timeout",
            )

        # Restore commit before querying.
        monkeypatch.setattr(db, "commit", original_commit)

        # The service should have rolled back the flushed template
        # and the pending event.
        assert db.query(LogTemplate).count() == 0
        assert db.query(LogEvent).count() == 0

    finally:
        db.close()


def test_database_failure_discards_drain3_miner(
    client_with_role, isolated_database, monkeypatch
):
    from datetime import datetime, timezone

    from backend.app.api.logs import log_service
    from backend.app.models.logs import LogEvent, LogTemplate

    client, create_token = client_with_role
    admin_headers = create_token(UserRole.ADMIN)

    create_host(client, admin_headers)

    db = isolated_database()
    original_commit = db.commit

    def failing_commit():
        raise RuntimeError("Simulated database failure")

    monkeypatch.setattr(db, "commit", failing_commit)

    try:
        with pytest.raises(RuntimeError, match="Simulated database failure"):
            log_service.ingest_log(
                db=db,
                host_id="server-01",
                timestamp=datetime.now(timezone.utc),
                severity="ERROR",
                message="Database connection timeout",
            )

        # Restore commit before checking database contents.
        monkeypatch.setattr(db, "commit", original_commit)

        # Database changes must have been rolled back.
        assert db.query(LogTemplate).count() == 0
        assert db.query(LogEvent).count() == 0

        # The failed ingestion must discard the in-memory miner.
        assert "server-01" not in log_service.parser.miners

    finally:
        db.close()



def test_drain3_persistence_failure_keeps_database_record(
    client_with_role, isolated_database, monkeypatch
):
    from datetime import datetime, timezone

    from backend.app.api.logs import log_service
    from backend.app.models.logs import LogEvent, LogTemplate

    client, create_token = client_with_role
    admin_headers = create_token(UserRole.ADMIN)

    create_host(client, admin_headers)

    db = isolated_database()

    def failing_save_state(host_id):
        raise OSError("Simulated Drain3 persistence failure")

    monkeypatch.setattr(
        log_service.parser,
        "save_state",
        failing_save_state,
    )

    try:
        event = log_service.ingest_log(
            db=db,
            host_id="server-01",
            timestamp=datetime.now(timezone.utc),
            severity="ERROR",
            message="Database connection timeout",
        )

        # Ingestion succeeds despite Drain3 persistence failure.
        assert event.id is not None

        # PostgreSQL records remain committed.
        assert db.query(LogEvent).count() == 1
        assert db.query(LogTemplate).count() == 1

        # In-memory miner is retained for a future persistence retry.
        assert "server-01" in log_service.parser.miners

    finally:
        db.close()