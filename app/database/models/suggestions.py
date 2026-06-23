# app/database/models/suggestions.py

from sqlalchemy import Integer, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
