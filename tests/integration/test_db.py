from sqlalchemy import text

from app.database.session import engine


def test_connection():

    with engine.connect() as conn:

        result = conn.execute(

            text("SELECT 1")
        )

        assert result.scalar() == 1