from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserModel, UserResponse, TokenModel, RequestEmail
from src.services.email import send_email


router = APIRouter(prefix='/auth', tags=["Authorization"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):


    """
    Register a new user.

    :param body: UserModel: User data for registration.
    :param background_tasks: BackgroundTasks: Background tasks for sending email confirmation.
    :param request: Request: Incoming HTTP request.
    :param db: Session: Database session object.
    :return: UserResponse: User data and confirmation message.
    :raises: HTTPException: If account with provided email already exists.
    """

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel, status_code=status.HTTP_200_OK)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    """
    Log in an existing user and issue access and refresh tokens.

    :param body: OAuth2PasswordRequestForm: Username and password for login.
    :param db: Session: Database session object.
    :return: TokenModel: Access and refresh tokens.
    :raises: HTTPException: If provided credentials are invalid or email is not confirmed.
    """

    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):

    """
    Refresh access token using refresh token.

    :param credentials: HTTPAuthorizationCredentials: HTTP Bearer token credentials.
    :param db: Session: Database session object.
    :return: TokenModel: New access and refresh tokens.
    :raises: HTTPException: If refresh token is invalid.
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):

    """
    Confirm user's email using confirmation token.

    :param token: str: Email confirmation token.
    :param db: Session: Database session object.
    :return: dict: Confirmation message.
    :raises: HTTPException: If verification fails.
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    
    """
    Request email confirmation.

    :param body: RequestEmail: Email address for confirmation.
    :param background_tasks: BackgroundTasks: Background tasks for sending email confirmation.
    :param request: Request: Incoming HTTP request.
    :param db: Session: Database session object.
    :return: dict: Confirmation message.
    """

    user = await repository_users.get_user_by_email(body.email, db)

    if user is not None and user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
