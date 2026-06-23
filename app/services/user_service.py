# app/services/user_service.py

from sqlalchemy.orm import Session

from app.database.models import User


def create_user(

        db: Session,

        telegram_id: int,

        username: str,

        first_name: str

):

    exists = db.query(User).filter(

        User.telegram_id == telegram_id

    ).first()

    if exists:
        return

    user = User(

        telegram_id=telegram_id,

        username=username,

        first_name=first_name
    )

    db.add(user)

    db.commit()