from fastapi.testclient import TestClient

from src.api import create_app


def test_register_login_and_protected_flow() -> None:
    app = create_app()
    client = TestClient(app)

    register_response = client.post(
        "/auth/register",
        data={"email": "test@example.com", "password": "Secret123"},
    )
    assert register_response.status_code == 200
    token = register_response.json()["access_token"]

    protected_response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "Secret123"},
    )
    assert login_response.status_code == 200
    login_token = login_response.json()["access_token"]

    me_response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {login_token}"},
    )
    assert me_response.status_code == 200
