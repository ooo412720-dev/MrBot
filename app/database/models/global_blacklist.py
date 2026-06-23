from sqlalchemy import (
    Integer,
    BigInteger,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class GlobalBlacklist(Base):

    __tablename__ = "global_blacklist"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )