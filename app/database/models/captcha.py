from sqlalchemy import (
    Integer,
    BigInteger,
    String
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base

class Captcha(Base):

    __tablename__ = "captchas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    answer: Mapped[str] = mapped_column(
        String(50)
    )