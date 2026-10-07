from fastapi.testclient import TestClient

from backend.app import main
from backend.app.api import metrics as metrics_api
from backend.app.services.metrics_service import MetricsService


def test_metric_service_persists_and_detects_anomaly(tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDGUARDIAN_DB_PATH", str(tmp_path / "cloudguardian.db"))
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


def test_api_accepts_metrics_and_serves_dashboard(tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDGUARDIAN_DB_PATH", str(tmp_path / "cloudguardian.db"))
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

    with TestClient(main.app) as client:
        response = client.post("/api/v1/metrics", json=payload)

        assert response.status_code == 201
        assert len(client.get("/api/v1/metrics").json()) == 1
        assert len(client.get("/api/v1/metrics/anomalies").json()) == 1
        assert client.get("/api/v1/metrics/hosts").json()[0]["status"] == "warning"
        assert client.get("/dashboard/").status_code == 200