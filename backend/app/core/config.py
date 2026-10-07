import os

from dotenv import load_dotenv

load_dotenv()


THRESHOLDS = {
    "cpu_percent": float(os.getenv("CPU_THRESHOLD", "85")),
    "memory_percent": float(os.getenv("MEMORY_THRESHOLD", "85")),
    "disk_percent": float(os.getenv("DISK_THRESHOLD", "90")),
    "latency_ms": float(os.getenv("LATENCY_THRESHOLD", "500")),
    "error_rate_percent": float(os.getenv("ERROR_RATE_THRESHOLD", "5")),
    "network_rtt_ms": float(os.getenv("NETWORK_RTT_THRESHOLD", "250")),
}

CRITICAL_MULTIPLIER = float(
    os.getenv("CRITICAL_MULTIPLIER", "1.15")
)