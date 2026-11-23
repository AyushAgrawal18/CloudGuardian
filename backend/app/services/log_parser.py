
import hashlib
import re
from pathlib import Path

from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence


SECRET_PATTERNS = [
    (
        re.compile(
            r"(?i)\b(password|passwd|token|api[_-]?key|secret)"
            r"(\s*[=:]\s*)([^\s,;]+)"
        ),
        r"\1\2[REDACTED]",
    ),
    (
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
        "Bearer [REDACTED]",
    ),
]


def redact_secrets(message: str) -> str:
    """Remove common credentials from a log message."""
    for pattern, replacement in SECRET_PATTERNS:
        message = pattern.sub(replacement, message)

    return message


class LogParser:
    """Parse logs using persistent, host-specific Drain3 miners."""

    def __init__(self, state_dir="backend/data/drain3"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.miners = {}

    def _get_miner(self, host_id: str) -> TemplateMiner:
        if not host_id or not host_id.strip():
            raise ValueError("Host ID cannot be empty")

        if host_id not in self.miners:
            host_key = hashlib.sha256(
                host_id.encode("utf-8")
            ).hexdigest()

            state_file = self.state_dir / f"{host_key}.bin"
            persistence = FilePersistence(str(state_file))

            self.miners[host_id] = TemplateMiner(persistence)

        return self.miners[host_id]

    def parse(self, message: str, host_id: str = "default") -> dict:
        """Parse a message and update in-memory state only."""
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Log message cannot be empty")

        sanitized_message = redact_secrets(message)

        miner = self._get_miner(host_id)
        result = miner.add_log_message(sanitized_message)

        return {
            "message": sanitized_message,
            "cluster_id": result["cluster_id"],
            "template": result["template_mined"],
            "cluster_size": result["cluster_size"],
        }

    def save_state(self, host_id: str) -> None:
        """Persist a host's current Drain3 state."""
        miner = self.miners.get(host_id)

        if miner is not None:
            miner.save_state("periodic")

    def discard_miner(self, host_id: str) -> None:
        """Discard in-memory state and reload the last persisted state later."""
        self.miners.pop(host_id, None)
