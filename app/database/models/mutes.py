from sqlalchemy import (
    Integer,
    BigInteger,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from datetime import datetime

from app.database.base import Base

class Mute(Base):

    __tablename__ = "mutes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    group_id: Mapped[int] = mapped_column(
        BigInteger
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime
    )