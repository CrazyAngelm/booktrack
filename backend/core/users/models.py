import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    surname = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    salt = Column(String(255))
    refresh_tokens = relationship(
        "RefreshToken", backref="user", cascade="all,delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refresh_tokens = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

