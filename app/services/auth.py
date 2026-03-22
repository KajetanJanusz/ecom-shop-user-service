import datetime
import uuid
from enum import StrEnum

import jwt
from typing_extensions import Literal

from exceptions import InvalidTokenError
from settings import get_settings

settings = get_settings()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class AuthService:
    @staticmethod
    def create_access_token(user_id: uuid.UUID) -> str:
        now = datetime.datetime.now()
        return jwt.encode(
            payload={
                "user_id": str(user_id),
                "exp": now + datetime.timedelta(hours=1),
                "type": TokenType.ACCESS,
            },
            key=settings.secret_key,
            algorithm=settings.algorithm,
        )

    @staticmethod
    def create_refresh_token(user_id: uuid.UUID) -> str:
        now = datetime.datetime.now()
        return jwt.encode(
            payload={
                "user_id": str(user_id),
                "exp": now + datetime.timedelta(days=30),
                "type": TokenType.REFRESH,
            },
            key=settings.secret_key,
            algorithm=settings.algorithm,
        )

    @staticmethod
    def verify_token(
        token: str, expected_token_type: TokenType
    ) -> uuid.UUID:
        try:
            decoded_data = jwt.decode(
                jwt=token,
                key=settings.secret_key,
                algorithms=[
                    settings.algorithm,
                ],
            )
        except jwt.PyJWTError as e:
            raise InvalidTokenError from e

        user_id = decoded_data.get("user_id")
        token_type = decoded_data.get("type")

        if not all([user_id, token_type]):
            raise InvalidTokenError

        if expected_token_type != token_type:
            raise InvalidTokenError

        return user_id
