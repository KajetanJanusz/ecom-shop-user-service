
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from server import app
from services.user import UserService, get_user_service
from settings import get_settings
from tests.models import UserFactory


@pytest.fixture(autouse=True)
def mock_auth_settings():
    """Patch the module-level settings object in auth.py with the real settings."""
    settings = get_settings()
    with patch("services.auth.settings", settings):
        yield settings


@pytest.fixture
def mock_broker():
    broker = AsyncMock()
    with patch("services.user.get_broker_client", return_value=broker):
        yield broker


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def user_service(mock_user_repo, mock_broker):
    service = object.__new__(UserService)
    service.user_repository = mock_user_repo
    service.broker_client = mock_broker
    return service


@pytest.fixture
def mock_user_service():
    user = UserFactory.build()
    service = AsyncMock()
    service.create_user.return_value = user
    service.authenticate_user.return_value = user
    service.get_user_by_id.return_value = user
    return service


@pytest.fixture
def client(mock_user_service):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    with patch("server.get_broker_client", return_value=AsyncMock()):
        yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
