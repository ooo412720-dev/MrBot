from sqlalchemy import (
    BigInteger,
    String,
    Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base

class Group(Base):

    __tablename__ = "groups"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    anti_raid_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    captcha_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    whisper_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )