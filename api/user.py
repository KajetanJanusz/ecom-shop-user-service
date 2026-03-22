from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from schemas.auth import TokenSchema, TokenPairSchema
from schemas.user import CreateUserSchema, LoginUserSchema
from services.auth import AuthService
from services.user import UserService, get_user_service


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post(
    "/register",
    tags=["auth"],
    summary="Register a new user",
    response_model=TokenPairSchema,
)
async def create_user(
    user_data: CreateUserSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> TokenPairSchema:
    user = await user_service.create_user(user_data=user_data)

    access_token = AuthService.create_access_token(user_id=user.id)
    refresh_token = AuthService.create_refresh_token(user_id=user.id)

    return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)


@user_router.post(
    "/token",
    tags=["auth"],
    summary="Login user",
    response_model=TokenPairSchema,
)
async def get_token_pair(
    user_data: LoginUserSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> TokenPairSchema:
    user = await user_service.authenticate_user(user_data=user_data)

    access_token = AuthService.create_access_token(user_id=user.id)
    refresh_token = AuthService.create_refresh_token(user_id=user.id)

    return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)


@user_router.post(
    "/token/refresh",
    tags=["auth"],
    summary="Refresh user tokens",
    response_model=TokenSchema,
)
async def refresh_access_token(
    token: TokenSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> TokenSchema:
    user_id = AuthService.verify_token(token=token.token, expected_token_type="refresh")

    await user_service.get_user_by_id(user_id=user_id)
    access_token = AuthService.create_access_token(user_id=user_id)

    return TokenSchema(token=access_token)
