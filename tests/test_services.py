import asyncio
import datetime
import uuid
from unittest.mock import MagicMock

import jwt
import pytest

from exceptions import InvalidCredentialsError, InvalidTokenError
from services.auth import AuthService, TokenType
from settings import get_settings
from tests.models import UserFactory


class TestUserService:
    def test_create_user_success(self, user_service, mock_user_repo, mock_outbox_repo):
        # Arrange
        user = UserFactory.build()
        mock_user_repo.create.return_value = user
        user_data = MagicMock(email="john@example.com", password="hashed_pw")

        # Act
        result = asyncio.run(user_service.create_user(user_data))

        # Assert
        assert result == user
        mock_user_repo.create.assert_called_once_with(schema=user_data)
        mock_outbox_repo.create.assert_called_once()

    def test_get_user_by_id_success(self, user_service, mock_user_repo):
        # Arrange
        user = UserFactory.build()
        mock_user_repo.get_one.return_value = user
        user_id = user.id

        # Act
        result = asyncio.run(user_service.get_user_by_id(user_id))

        # Assert
        assert result == user

    def test_authenticate_user_success(self, user_service, mock_user_repo, mock_outbox_repo):
        # Arrange
        user = UserFactory.build()
        mock_user_repo.get_one.return_value = user
        user_data = MagicMock(email=user.email, password="password")

        # Act
        result = asyncio.run(user_service.authenticate_user(user_data))

        # Assert
        assert result == user
        mock_outbox_repo.create.assert_called_once()

    @pytest.mark.parametrize(
        ("repo_return", "is_active", "password"),
        [
            (None, True, "password"),  # user not found
            ("user", False, "password"),  # user inactive
            ("user", True, "wrong_pass"),  # wrong password
        ],
    )
    def test_authenticate_user_raises_invalid_credentials(
        self, user_service, mock_user_repo, repo_return, is_active, password
    ):
        # Arrange
        user = UserFactory.build() if repo_return == "user" else None
        if user:
            user.is_active = is_active
        mock_user_repo.get_one.return_value = user
        user_data = MagicMock(email="test@example.com", password=password)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            asyncio.run(user_service.authenticate_user(user_data))


class TestAuthService:
    def test_create_access_token_returns_decodable_token(self, mock_auth_settings):
        # Arrange
        user_id = uuid.uuid4()

        # Act
        token = AuthService.create_access_token(user_id=user_id)

        # Assert
        settings = get_settings()
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["user_id"] == str(user_id)
        assert payload["type"] == "access"

    def test_create_refresh_token_returns_decodable_token(self, mock_auth_settings):
        # Arrange
        user_id = uuid.uuid4()

        # Act
        token = AuthService.create_refresh_token(user_id=user_id)

        # Assert
        settings = get_settings()
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["user_id"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_verify_token_success(self, mock_auth_settings):
        # Arrange
        user_id = uuid.uuid4()
        token = AuthService.create_access_token(user_id=user_id)

        # Act
        result = AuthService.verify_token(token=token, expected_token_type=TokenType.ACCESS)

        # Assert
        assert result == str(user_id)

    def test_expired_token_raises_invalid_token(self, mock_auth_settings):
        # Arrange
        user_id = uuid.uuid4()
        payload = {
            "user_id": str(user_id),
            "exp": datetime.datetime.now() - datetime.timedelta(hours=1),
            "type": TokenType.ACCESS,
        }
        settings = get_settings()
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        # Act & Assert
        with pytest.raises(InvalidTokenError):
            AuthService.verify_token(token=token, expected_token_type=TokenType.ACCESS)

    def test_verify_wrong_type_token_raises_invalid_token(self, mock_auth_settings):
        # Arrange
        user_id = uuid.uuid4()
        token = AuthService.create_refresh_token(user_id=user_id)

        # Act & Assert
        with pytest.raises(InvalidTokenError):
            AuthService.verify_token(token=token, expected_token_type=TokenType.ACCESS)

    def test_verify_invalid_token_raises_invalid_token(self, mock_auth_settings):
        # Arrange
        token = "invalid.token"

        # Act & Assert
        with pytest.raises(InvalidTokenError):
            AuthService.verify_token(token=token, expected_token_type=TokenType.ACCESS)
