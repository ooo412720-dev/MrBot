from sqlalchemy import (
    BigInteger,
    Boolean,
    Integer
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class GroupSettings(Base):

    __tablename__ = "group_settings"

    group_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    links_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    media_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    captcha_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    sticker_limit: Mapped[int] = mapped_column(
        Integer,
        default=5
    )

    mute_hours: Mapped[int] = mapped_column(
        Integer,
        default=1
    )