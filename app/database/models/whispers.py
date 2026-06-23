from sqlalchemy import (
    BigInteger,
    Boolean,
    Text
)

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base

class Whisper(Base):

    __tablename__ = "whispers"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    sender_id: Mapped[int] = mapped_column(
        BigInteger
    )

    target_id: Mapped[int] = mapped_column(
        BigInteger
    )

    message: Mapped[str] = mapped_column(
        Text
    )

    archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )