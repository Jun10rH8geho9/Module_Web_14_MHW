from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_email(email: str, db: Session) -> User:

    """
    Retrieve a user by email.

    :param email: str: Email of the user to retrieve.
    :param db: Session: Database session object.
    :return: User: Retrieved user object.
    """

    return db.query(User).filter(User.email == email).first()


# Створюємо нового 
async def create_user(body: UserModel, db: Session) -> User:


    """
    Create a new user.

    :param body: UserModel: User data to create.
    :param db: Session: Database session object.
    :return: User: Created user object.
    """

    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def confirmed_email(email: str, db: Session) -> None:

    """
    Confirm user's email.

    :param email: str: Email address of the user.
    :param db: Session: Database session object.
    :return: None
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_token(user: User, token: str | None, db: Session) -> None:

    """
    Update user's authentication token.

    :param user: User: User object to update.
    :param token: str | None: Authentication token to set.
    :param db: Session: Database session object.
    :return: None
    """

    user.refresh_token = token
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update user's avatar URL.

    :param email: str: Email address of the user.
    :param url: str: New avatar URL to set.
    :param db: Session: Database session object.
    :return: User: Updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user