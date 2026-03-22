from typing import Self

from pydantic import BaseModel, model_validator

from models.user import User


class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @model_validator(mode="after")
    def hash_password(self) -> Self:
        self.password = User.hash_password(self.password)
        return self


class LoginUserSchema(BaseModel):
    email: str
    password: str
