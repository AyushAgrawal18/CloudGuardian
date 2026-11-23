
from pprint import pprint

from agent.collectors.system_collector import (
    collect_system_metrics,
    build_metric_payload,
)


if __name__ == "__main__":
    metrics = collect_system_metrics()

    payload = build_metric_payload(metrics)

    print("\nCollected System Metrics:")
    pprint(metrics)

    print("\nCloudGuardian API Payload:")
    pprint(payload)
