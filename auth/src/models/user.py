import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from ..db.postgres import Base


class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    token_version = Column(Integer, default=1)
    email = Column(String, unique=True)

    def __repr__(self):
        return f"<User {self.login}>"
