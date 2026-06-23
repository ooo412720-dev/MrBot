from sqlalchemy import (
    Integer,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class Stats(Base):

    __tablename__ = "stats"

    group_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    messages: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    joins: Mapped[int] = mapped_column(
        Integer,
        default=0
    )