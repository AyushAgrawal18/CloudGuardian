
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

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from environment variables")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
