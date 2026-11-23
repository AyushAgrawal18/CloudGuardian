
import platform
import psutil
import socket


def collect_system_metrics() -> dict:
    """Collect current system resource utilization."""

    cpu_percent = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    network = psutil.net_io_counters()

    return {
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),

        "cpu_percent": cpu_percent,

        "memory_percent": memory.percent,
        "memory_total_bytes": memory.total,
        "memory_available_bytes": memory.available,

        "disk_percent": disk.percent,
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,

        "network_bytes_sent": network.bytes_sent,
        "network_bytes_recv": network.bytes_recv,
    }


def build_metric_payload(metrics: dict) -> dict:
    """Convert collected system metrics into the backend API schema."""

    return {
        "host_id": metrics["hostname"],
        "cpu_percent": metrics["cpu_percent"],
        "memory_percent": metrics["memory_percent"],
        "disk_percent": metrics["disk_percent"],
        "latency_ms": 0.0,
        "error_rate_percent": 0.0,
        "active_connections": 0,
        "request_rate": 0.0,
        "network_rtt_ms": 0.0,
    }
