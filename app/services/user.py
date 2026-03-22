import uuid

from ecom_shop_shared_lib.brokers.events.user_service.events import UserServiceEvents
from ecom_shop_shared_lib.models import EventStatus
from ecom_shop_shared_lib.schemas.outbox import OutboxSchema
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from exceptions import InvalidCredentialsError
from models.outbox import Outbox
from models.user import User
from schemas.user import CreateUserSchema, LoginUserSchema
from ecom_shop_shared_lib.repositories.base import AsyncBaseRepository, ModelFields


class UserService:
    def __init__(
        self,
        db_session: AsyncSession,
        user_repository: AsyncBaseRepository[User],
        outbox_repository: AsyncBaseRepository[Outbox],
    ):
        self.db_session = db_session
        self.user_repository = user_repository
        self.outbox_repository = outbox_repository

    async def create_user(self, user_data: CreateUserSchema) -> User:
        async with self.db_session.begin():
            user = await self.user_repository.create(schema=user_data)
            await self.outbox_repository.create(
                schema=OutboxSchema(
                    event_topic=UserServiceEvents.USER_CREATED.topic,
                    payload=UserServiceEvents.USER_CREATED.schema(
                        id=user.id, created_at=user.created_at
                    ),
                    status=EventStatus.UNPROCESSED,
                )
            )
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        return await self.user_repository.get_one(
            [ModelFields(field=User.id, value=user_id)]
        )

    async def authenticate_user(self, user_data: LoginUserSchema) -> User:
        user = await self.user_repository.get_one(
            [ModelFields(field=User.email, value=user_data.email)]
        )

        if not user or user.is_active is False:
            raise InvalidCredentialsError

        if not user.verify_password(plain_password=user_data.password):
            raise InvalidCredentialsError

        await self.outbox_repository.create(
            schema=OutboxSchema(
                event_topic=UserServiceEvents.USER_LOGGED.topic,
                payload=UserServiceEvents.USER_LOGGED.schema(id=user.id),
                status=EventStatus.UNPROCESSED,
            )
        )

        return user


async def get_user_service(
    db_session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(db_session=db_session)
