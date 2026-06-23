from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    BigInteger,
    Text,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class Log(Base):

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    group_id: Mapped[int] = mapped_column(
        BigInteger
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    action: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
