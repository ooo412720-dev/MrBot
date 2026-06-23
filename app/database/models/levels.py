from sqlalchemy import (
    BigInteger,
    Integer
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class Level(Base):

    __tablename__ = "levels"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        default=0
    )