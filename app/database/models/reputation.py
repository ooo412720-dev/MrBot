from sqlalchemy import (
    Integer,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class Reputation(Base):

    __tablename__ = "reputation"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    score: Mapped[int] = mapped_column(
        Integer,
        default=100
    )


def add_reputation(
    current: int,
    amount: int
) -> int:

    return current + amount