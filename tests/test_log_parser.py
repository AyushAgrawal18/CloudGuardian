
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.app.services.log_parser import (
    LogParser,
    redact_secrets,
)


def test_password_is_redacted():
    message = "Login failed password=supersecret"

    result = redact_secrets(message)

    assert "supersecret" not in result
    assert "[REDACTED]" in result


def test_bearer_token_is_redacted():
    message = "Authorization: Bearer abc123.secret456"

    result = redact_secrets(message)

    assert "abc123.secret456" not in result
    assert "[REDACTED]" in result


def test_parser_returns_structured_result(tmp_path):
    parser = LogParser(state_dir=str(tmp_path))

    result = parser.parse(
        "Database connection timeout"
    )

    assert result["message"] == "Database connection timeout"
    assert result["cluster_id"] > 0
    assert result["template"]
    assert result["cluster_size"] == 1


def test_repeated_logs_update_existing_cluster(tmp_path):
    parser = LogParser(state_dir=str(tmp_path))

    first = parser.parse("Database connection timeout")
    second = parser.parse("Database connection timeout")

    assert first["cluster_id"] == second["cluster_id"]
    assert second["cluster_size"] == 2


def test_empty_log_message_is_rejected(tmp_path):
    parser = LogParser(state_dir=str(tmp_path))

    with pytest.raises(ValueError):
        parser.parse("   ")



def test_parser_restores_state_after_restart(tmp_path):
    state_dir = str(tmp_path)

    parser1 = LogParser(state_dir=state_dir)
    first = parser1.parse(
        "Database connection timeout",
        host_id="server-1",
    )

    parser2 = LogParser(state_dir=state_dir)
    second = parser2.parse(
        "Database connection timeout",
        host_id="server-1",
    )

    assert first["cluster_id"] == second["cluster_id"]
    assert second["cluster_size"] == 2


def test_same_host_uses_same_lock_concurrently(tmp_path):
    from backend.app.services.log_parser import LogParser

    parser = LogParser(state_dir=str(tmp_path))

    lock_a = parser.get_host_lock("server-01")
    lock_b = parser.get_host_lock("server-01")

    # Both requests must receive the same lock object.
    assert lock_a is lock_b

    active_requests = 0
    maximum_active_requests = 0
    counter_lock = threading.Lock()

    def simulate_request():
        nonlocal active_requests, maximum_active_requests

        with parser.get_host_lock("server-01"):
            with counter_lock:
                active_requests += 1
                maximum_active_requests = max(
                    maximum_active_requests,
                    active_requests,
                )

            # Simulate work while holding the host lock.
            threading.Event().wait(0.05)

            with counter_lock:
                active_requests -= 1

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(simulate_request)
            for _ in range(10)
        ]

        for future in futures:
            future.result()

    assert maximum_active_requests == 1
