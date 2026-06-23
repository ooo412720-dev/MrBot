from sqlalchemy import (
    Integer,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base

class Warning(Base):

    __tablename__ = "warnings"

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

    count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )