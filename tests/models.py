import datetime
import uuid

import factory
from factory import Faker, LazyFunction
from factory.alchemy import SQLAlchemyModelFactory

from models.user import User


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = LazyFunction(uuid.uuid4)

    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    phone_number = Faker("phone_number")
    hashed_password = LazyFunction(lambda: User.hash_password("password"))
    is_active = True

    created_at = LazyFunction(datetime.datetime.now)
    updated_at = LazyFunction(datetime.datetime.now)

    class Params:
        inactive = factory.Trait(is_active=False)
