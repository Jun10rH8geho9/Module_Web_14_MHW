import unittest
from unittest.mock import MagicMock, Mock, patch

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    update_avatar,
    confirmed_email
)


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        user = UserModel(id=1,
                        username="username",
                        email='user@example.com',
                        password="password")

        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        self.session.query().filter().first.return_value = user

        result = await get_user_by_email(user.email, self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(username="username",
                         email='user@example.com',
                         password="password")

        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_update_token(self):
        refresh_token = None
        with patch.object(self.session, 'commit') as mock_db_commit:
            result = await update_token(self.user, refresh_token, self.session)
            mock_db_commit.assert_called_once()
            self.assertEqual(result, refresh_token)

    async def test_confirmed_email(self):
        user = User(username="username",
                    email='user@example.com',
                    password="password",
                    confirmed=False)

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            mock_session_commit = MagicMock()
            self.session.commit = mock_session_commit

            result = await confirmed_email(user.email, self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)
            mock_session_commit.assert_called_once()
            self.assertIsNone(result)

    async def test_update_avatar(self):
        user = User(username="username",
                    email='user@example.com',
                    password="password",
                    avatar="avatar_url")

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            mock_session_commit = MagicMock()
            self.session.commit = mock_session_commit

            result = await update_avatar(user.email, "another_avatar", self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)
            mock_session_commit.assert_called_once()
            self.assertEqual(result.avatar, "another_avatar")

if __name__ == '__main__':
    unittest.main()