import uuid
from datetime import date

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserProfileRead(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    preferred_first_name: str | None = None
    birthdate: date | None = None
    referral_source: str | None = None
    intended_use: str | None = None

    model_config = {"from_attributes": True}
