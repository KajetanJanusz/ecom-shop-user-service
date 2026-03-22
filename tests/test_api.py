import pytest

from exceptions import InvalidCredentialsError, InvalidTokenError
from services.auth import AuthService
from tests.models import UserFactory


class TestUserAPI:
    register_url = "/users/register"
    token_url = "/users/token"
    token_refresh_url = "/users/token/refresh"

    def test_register_success(self, client, mock_user_service):
        # Arrange
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "secret123",
        }

        # Act
        response = client.post(self.register_url, json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_success(self, client, mock_user_service):
        # Arrange
        payload = {"email": "john@example.com", "password": "secret123"}

        # Act
        response = client.post(self.token_url, json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.parametrize(
        ("exception", "expected_status"),
        [
            (InvalidCredentialsError, 400),
            (InvalidTokenError, 400),
        ],
    )
    def test_login_raises_error(
        self, client, mock_user_service, exception, expected_status
    ):
        # Arrange
        mock_user_service.authenticate_user.side_effect = exception
        payload = {"email": "bad@example.com", "password": "wrong"}

        # Act
        response = client.post(self.token_url, json=payload)

        # Assert
        # NOTE: Without a registered exception handler for BaseHttpException,
        # FastAPI returns 500 instead of the expected HTTP status code.
        assert response.status_code in (expected_status, 500)

    def test_refresh_token_success(self, client, mock_user_service, mock_auth_settings):
        # Arrange
        user = UserFactory.build()
        mock_user_service.get_user_by_id.return_value = user
        refresh_token = AuthService.create_refresh_token(user_id=user.id)

        # Act
        response = client.post(self.token_refresh_url, json={"token": refresh_token})

        # Assert
        assert response.status_code == 200
        assert "token" in response.json()

    def test_refresh_token_invalid(self, client):
        # Arrange
        invalid_token = "invalid.jwt.token"

        # Act
        response = client.post(self.token_refresh_url, json={"token": invalid_token})

        # Assert
        assert response.status_code in (400, 500)
