
import pytest

from backend.app.models.user import UserRole


HOST_PAYLOAD = {
    "host_id": "server-01",
    "name": "Production Server",
    "hostname": "prod-server-01",
    "ip_address": "192.168.1.10",
    "environment": "production",
    "operating_system": "Ubuntu 24.04",
}


def create_host(client, headers, payload=None):
    return client.post(
        "/api/v1/hosts",
        json=payload or HOST_PAYLOAD,
        headers=headers,
    )


def test_admin_can_create_host(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    response = create_host(client, headers)

    assert response.status_code == 201
    assert response.json()["host_id"] == "server-01"
    assert response.json()["status"] == "active"


def test_viewer_can_list_and_get_hosts(client_with_role):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    viewer_headers = create_token(UserRole.VIEWER)

    create_host(client, admin_headers)

    list_response = client.get(
        "/api/v1/hosts",
        headers=viewer_headers,
    )

    detail_response = client.get(
        "/api/v1/hosts/server-01",
        headers=viewer_headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["host_id"] == "server-01"


@pytest.mark.parametrize(
    "role",
    [UserRole.OPERATOR, UserRole.VIEWER],
)
def test_non_admin_cannot_create_host(client_with_role, role):
    client, create_token = client_with_role

    response = create_host(
        client,
        create_token(role),
    )

    assert response.status_code == 403


def test_admin_can_update_host(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    create_host(client, headers)

    response = client.patch(
        "/api/v1/hosts/server-01",
        json={"name": "Updated Production Server"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Production Server"


def test_admin_can_deactivate_host(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    create_host(client, headers)

    response = client.delete(
        "/api/v1/hosts/server-01",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


@pytest.mark.parametrize(
    "role",
    [UserRole.OPERATOR, UserRole.VIEWER],
)
def test_non_admin_cannot_update_or_deactivate_host(
    client_with_role,
    role,
):
    client, create_token = client_with_role

    admin_headers = create_token(UserRole.ADMIN)
    user_headers = create_token(role)

    create_host(client, admin_headers)

    update_response = client.patch(
        "/api/v1/hosts/server-01",
        json={"name": "Unauthorized Update"},
        headers=user_headers,
    )

    delete_response = client.delete(
        "/api/v1/hosts/server-01",
        headers=user_headers,
    )

    assert update_response.status_code == 403
    assert delete_response.status_code == 403


def test_duplicate_host_id_returns_conflict(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    first_response = create_host(client, headers)
    second_response = create_host(client, headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_filter_hosts_by_environment(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    create_host(client, headers)

    staging_host = {
        **HOST_PAYLOAD,
        "host_id": "server-02",
        "environment": "staging",
    }

    create_host(client, headers, staging_host)

    response = client.get(
        "/api/v1/hosts?environment=production",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["host_id"] == "server-01"


def test_filter_hosts_by_status(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    create_host(client, headers)

    client.delete(
        "/api/v1/hosts/server-01",
        headers=headers,
    )

    response = client.get(
        "/api/v1/hosts?status=inactive",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "inactive"


def test_unknown_host_returns_404(client_with_role):
    client, create_token = client_with_role
    headers = create_token(UserRole.ADMIN)

    response = client.get(
        "/api/v1/hosts/unknown-server",
        headers=headers,
    )

    assert response.status_code == 404


def test_hosts_reject_missing_token(client_with_role):
    client, _ = client_with_role

    response = client.get("/api/v1/hosts")

    assert response.status_code == 401
