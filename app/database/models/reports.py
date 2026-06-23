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


class Report(Base):

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    reporter_id: Mapped[int] = mapped_column(
        BigInteger
    )

    target_id: Mapped[int] = mapped_column(
        BigInteger
    )

    reason: Mapped[str] = mapped_column(
        Text
    )