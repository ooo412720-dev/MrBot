from sqlalchemy import (
    Integer,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base

class Points(Base):

    __tablename__ = "points"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    points: Mapped[int] = mapped_column(
        Integer,
        default=0
    )