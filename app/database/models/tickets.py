from sqlalchemy import (
    Integer,
    BigInteger,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class Ticket(Base):

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    message: Mapped[str] = mapped_column(
        Text
    )