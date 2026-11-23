
def test_metric_buffer_add_and_retrieve(tmp_path):
    from agent.storage.metric_buffer import MetricBuffer

    buffer = MetricBuffer(str(tmp_path / "buffer.db"))

    payload = {
        "host_id": "AYUSH_AGRAWAL",
        "cpu_percent": 45.0,
    }

    buffer.add(payload)

    pending = buffer.get_pending()

    assert len(pending) == 1
    assert pending[0]["payload"] == payload
    assert buffer.count() == 1


def test_metric_buffer_remove(tmp_path):
    from agent.storage.metric_buffer import MetricBuffer

    buffer = MetricBuffer(str(tmp_path / "buffer.db"))

    buffer.add({"host_id": "server-01"})
    metric_id = buffer.get_pending()[0]["id"]

    buffer.remove(metric_id)

    assert buffer.count() == 0


def test_metric_buffer_persists_after_restart(tmp_path):
    from agent.storage.metric_buffer import MetricBuffer

    db_path = str(tmp_path / "buffer.db")

    first_buffer = MetricBuffer(db_path)
    first_buffer.add({"host_id": "server-01"})

    second_buffer = MetricBuffer(db_path)

    assert second_buffer.count() == 1
