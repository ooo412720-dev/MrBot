from sqlalchemy import (
    Integer,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class Wallet(Base):

    __tablename__ = "wallets"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    balance: Mapped[int] = mapped_column(
        Integer,
        default=0
    )