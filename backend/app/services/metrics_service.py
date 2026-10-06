
from backend.app.schemas.metrics import MetricIn, MetricOut


class MetricsService:
    def __init__(self):
        self._metrics: list[MetricOut] = []
        self._next_id = 1
        self._max_records = 1000

    def add_metric(self, metric: MetricIn) -> MetricOut:
        record = MetricOut(
            id=self._next_id,
            **metric.model_dump(),
        )

        self._next_id += 1
        self._metrics.append(record)

        if len(self._metrics) > self._max_records:
            self._metrics.pop(0)

        return record

    def get_recent(self, limit: int = 50) -> list[MetricOut]:
        return list(reversed(self._metrics[-limit:]))


metrics_service = MetricsService()
