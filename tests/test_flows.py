import os

from fastapi.testclient import TestClient

from src.api import create_app


def test_register_login_and_protected_flow(tmp_path) -> None:
    db_path = tmp_path / "test-auth.db"
    previous_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(db_path)
    try:
        app = create_app()
        with TestClient(app) as client:
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
    finally:
        if previous_db_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_db_url
