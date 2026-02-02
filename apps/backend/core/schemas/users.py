import uuid

from fastapi_users.db import SQLAlchemyBaseOAuthAccountTableUUID, SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from core.schemas.base import UserManagementDBModel


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, UserManagementDBModel):
    """OAuth account linking external providers (Google, etc.) to users."""

    pass


class User(SQLAlchemyBaseUserTableUUID, UserManagementDBModel):
    """User model with OAuth account relationships."""

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship("OAuthAccount", lazy="joined")
    profile = relationship("UserProfile", uselist=False, back_populates="user", lazy="joined")


class UserProfile(UserManagementDBModel):
    """Extended user profile information."""

    __tablename__ = "user_profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    preferred_first_name = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    referral_source = Column(String, nullable=True)
    intended_use = Column(String, nullable=True)
    user = relationship("User", back_populates="profile")
