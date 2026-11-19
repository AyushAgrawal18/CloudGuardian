
from collections import deque
from statistics import mean, stdev


class StatisticalService:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._history = {}

    def analyze(
        self,
        host_id: str,
        metric_name: str,
        actual_value: float,
    ) -> dict:
        key = (host_id, metric_name)

        if key not in self._history:
            self._history[key] = deque(maxlen=self.window_size)

        history = self._history[key]

        # Need enough historical observations
        # before calculating statistical anomalies.
        if len(history) < 5:
            history.append(actual_value)
            return {
                "metric_name": metric_name,
                "actual_value": actual_value,
                "rolling_mean": None,
                "rolling_std": None,
                "z_score": None,
                "is_anomaly": False,
            }

        rolling_mean = mean(history)
        rolling_std = stdev(history)

        if rolling_std == 0:
            z_score = None
            is_anomaly = actual_value != rolling_mean
        else:
            z_score = (actual_value - rolling_mean) / rolling_std
            is_anomaly = abs(z_score) >= 3.0

        history.append(actual_value)

        return {
            "metric_name": metric_name,
            "actual_value": actual_value,
            "rolling_mean": rolling_mean,
            "rolling_std": rolling_std,
            "z_score": z_score,
            "is_anomaly": is_anomaly,
        }

    def restore_history(
        self,
        host_id: str,
        metric_name: str,
        values: list[float],
    ) -> None:
        key = (host_id, metric_name)

        self._history[key] = deque(
            values[-self.window_size:],
            maxlen=self.window_size,
        )

statistical_service = StatisticalService()
