# app/database/models/federation_bans.py

from datetime import datetime, timezone
from sqlalchemy import Integer, BigInteger, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class FederationBan(Base):
    __tablename__ = "federation_bans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
