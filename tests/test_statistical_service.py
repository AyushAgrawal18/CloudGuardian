from backend.app.services.statistical_service import StatisticalService


def test_statistical_service_detects_spike():
    service = StatisticalService(window_size=20)

    # Build a stable baseline.
    for _ in range(10):
        result = service.analyze("host-1", "cpu_percent", 50.0)

    # A sudden spike should be detected.
    result = service.analyze("host-1", "cpu_percent", 100.0)

    assert result["is_anomaly"] is True
    assert result["z_score"] is None


def test_statistical_service_keeps_hosts_separate():
    service = StatisticalService(window_size=20)

    for _ in range(5):
        service.analyze("host-1", "cpu_percent", 50.0)

    result = service.analyze("host-2", "cpu_percent", 100.0)

    # Host 2 has no historical baseline yet.
    assert result["is_anomaly"] is False


def test_statistical_service_waits_for_warmup():
    service = StatisticalService(window_size=20)

    # First 5 readings should only build the baseline.
    for _ in range(5):
        result = service.analyze("host-1", "cpu_percent", 50.0)

        assert result["is_anomaly"] is False
        assert result["rolling_mean"] is None

    # The 6th reading should be evaluated.
    result = service.analyze("host-1", "cpu_percent", 100.0)

    assert result["is_anomaly"] is True