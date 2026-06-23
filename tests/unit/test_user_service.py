from unittest.mock import MagicMock, patch
from app.services.user_service import create_user


@patch("app.services.user_service.Session")
def test_create_user(mock_session_cls):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    create_user(
        db=db,
        telegram_id=123456,
        username="testuser",
        first_name="Test"
    )

    db.add.assert_called_once()
    db.commit.assert_called_once()
