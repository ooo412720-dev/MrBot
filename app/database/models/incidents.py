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


class Incident(Base):

    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    reason: Mapped[str] = mapped_column(
        Text
    )

    status: Mapped[str] = mapped_column(
        Text,
        default="open"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
