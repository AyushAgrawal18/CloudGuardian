
import logging
import time

from agent.collectors.system_collector import (
    collect_system_metrics,
    build_metric_payload,
)
from agent.core.api_client import CloudGuardianClient
from agent.config import AGENT_INTERVAL_SECONDS
from agent.storage.metric_buffer import MetricBuffer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("cloudguardian-agent")


def flush_pending_metrics(client, buffer):
    """Send queued metrics to CloudGuardian in FIFO order."""
    while True:
        pending_metrics = buffer.get_pending(limit=1)

        if not pending_metrics:
            break

        metric = pending_metrics[0]

        try:
            response = client.send_metrics(metric["payload"])

            buffer.remove(metric["id"])

            logger.info(
                "Metric delivered | Host: %s | Metric ID: %s",
                response["host_id"],
                response["id"],
            )

        except Exception:
            logger.exception(
                "Could not deliver queued metric %s. Keeping it for retry.",
                metric["id"],
            )
            break


def main():
    client = CloudGuardianClient()
    buffer = MetricBuffer()

    logger.info("CloudGuardian Monitoring Agent started")
    logger.info("Collection interval: %s seconds", AGENT_INTERVAL_SECONDS)

    try:
        while True:
            try:
                logger.info("Collecting system metrics...")

                metrics = collect_system_metrics()
                payload = build_metric_payload(metrics)

                # Persist before attempting network delivery.
                buffer.add(payload)

                logger.info(
                    "Metric saved locally | Pending: %s",
                    buffer.count(),
                )

                flush_pending_metrics(client, buffer)

            except Exception:
                logger.exception("Metric collection or processing failed")

            time.sleep(AGENT_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Shutdown signal received")

    finally:
        client.close()
        logger.info("CloudGuardian Monitoring Agent stopped")


if __name__ == "__main__":
    main()
