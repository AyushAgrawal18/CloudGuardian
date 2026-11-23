
import httpx
import pytest

from unittest.mock import Mock, patch

from agent.core.api_client import CloudGuardianClient


@pytest.fixture
def client():
    with patch("agent.core.api_client.AGENT_EMAIL", "test@example.com"), \
         patch("agent.core.api_client.AGENT_PASSWORD", "test-password"):
        api_client = CloudGuardianClient()
        yield api_client
        api_client.close()


def test_successful_login(client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "access_token": "test-token"
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client.client, "post", return_value=mock_response):
        client.login()

    assert client.access_token == "test-token"
    assert client.client.headers["Authorization"] == "Bearer test-token"


def test_successful_metric_ingestion(client):
    client.access_token = "test-token"

    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1}

    with patch.object(client.client, "post", return_value=mock_response):
        result = client.send_metrics({"host_id": "test-host"})

    assert result["id"] == 1


def test_metric_ingestion_retries_network_failure(client):
    client.access_token = "test-token"

    success_response = Mock()
    success_response.status_code = 201
    success_response.json.return_value = {"id": 2}

    with patch.object(
        client.client,
        "post",
        side_effect=[
            httpx.ConnectError("Connection failed"),
            success_response,
        ],
    ), patch("agent.core.api_client.time.sleep") as mock_sleep:

        result = client.send_metrics({"host_id": "test-host"})

    assert result["id"] == 2
    mock_sleep.assert_called_once_with(2)


def test_invalid_metric_is_not_retried(client):
    client.access_token = "test-token"

    request = httpx.Request(
        "POST",
        "http://test/api/v1/metrics",
    )

    response = httpx.Response(
        422,
        request=request,
        json={"detail": "Invalid metric"},
    )

    with patch.object(
        client.client,
        "post",
        return_value=response,
    ) as mock_post:

        with pytest.raises(httpx.HTTPStatusError):
            client.send_metrics({"host_id": "test-host"})

    assert mock_post.call_count == 1


def test_expired_token_triggers_login_and_retries_metric(client):
    client.access_token = "expired-token"

    unauthorized_response = Mock()
    unauthorized_response.status_code = 401

    login_response = Mock()
    login_response.json.return_value = {
        "access_token": "new-token"
    }
    login_response.raise_for_status.return_value = None

    success_response = Mock()
    success_response.status_code = 201
    success_response.json.return_value = {"id": 3}

    with patch.object(
        client.client,
        "post",
        side_effect=[
            unauthorized_response,
            login_response,
            success_response,
        ],
    ) as mock_post:

        result = client.send_metrics({"host_id": "test-host"})

    assert result["id"] == 3
    assert client.access_token == "new-token"
    assert client.client.headers["Authorization"] == "Bearer new-token"
    assert mock_post.call_count == 3
