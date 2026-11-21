
from datetime import datetime, timezone

from backend.app.services.metrics_service import MetricsService
from backend.app.schemas.metrics import MetricIn
from backend.app.services.statistical_service import StatisticalService


def create_metric(cpu: float) -> MetricIn:
    return MetricIn(
        host_id="integration-host",
        timestamp=datetime.now(timezone.utc),
        cpu_percent=cpu,
        memory_percent=30.0,
        disk_percent=40.0,
        latency_ms=100.0,
        error_rate_percent=1.0,
        active_connections=10,
        request_rate=50.0,
        network_rtt_ms=20.0,
    )


def test_statistical_anomaly_is_saved():
    import backend.app.services.metrics_service as metrics_module

    metrics_module.statistical_service = StatisticalService(window_size=20)

    service = MetricsService()
    service._thresholds = {"cpu_percent": 1000.0}

    for _ in range(5):
        service.add_metric(create_metric(50.0))

    service.add_metric(create_metric(100.0))

    anomalies = service.get_anomalies()

    assert len(anomalies) == 1
    assert anomalies[0].metric_name == "cpu_percent"
    assert "statistically unusual" in anomalies[0].explanation


def test_combines_threshold_and_statistical_detection():
    import backend.app.services.metrics_service as metrics_module

    metrics_module.statistical_service = StatisticalService(window_size=20)

    service = MetricsService()
    service._thresholds = {"cpu_percent": 85.0}

    for _ in range(5):
        service.add_metric(create_metric(50.0))

    service.add_metric(create_metric(100.0))

    anomalies = service.get_anomalies()

    assert len(anomalies) == 1
    assert "configured threshold" in anomalies[0].explanation
    assert "statistically unusual" in anomalies[0].explanation
    assert anomalies[0].severity == "critical"


def test_statistical_history_survives_service_restart():
    import backend.app.services.metrics_service as metrics_module

    metrics_module.statistical_service = StatisticalService(window_size=20)

    first_service = MetricsService()

    for _ in range(5):
        first_service.add_metric(create_metric(50.0))

    # Simulate a service restart with fresh statistical memory.
    metrics_module.statistical_service = StatisticalService(window_size=20)

    restarted_service = MetricsService()
    restarted_service._thresholds = {"cpu_percent": 1000.0}

    restarted_service.add_metric(create_metric(100.0))

    anomalies = restarted_service.get_anomalies()

    assert len(anomalies) == 1
    assert anomalies[0].metric_name == "cpu_percent"
    assert "statistically unusual" in anomalies[0].explanation
