import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas.schemas import PasswordResetRequest, PasswordReset
from src.schemas.users import UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/users', tags=["users"])

cloudinary.config(cloud_name=settings.CLOUDINARY_NAME,
                  api_key=settings.CLOUDINARY_API_KEY,
                  api_secret=settings.CLOUDINARY_API_SECRET,
                  secure=True)


@router.get('/me', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_my_user(my_user: User = Depends(auth_service.get_current_user)):

    """
    Get the details of the currently authenticated user.

    :param my_user: User: Current authenticated user.
    :return: UserResponse: Details of the authenticated user.
    """

    return my_user


@router.patch('/avatar', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def upload_avatar(file: UploadFile = File(),
                        user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """
    Upload a new avatar for the authenticated user.

    :param file: UploadFile: Avatar image file to upload.
    :param user: User: Current authenticated user.
    :param db: AsyncSession: Async database session object.
    :return: UserResponse: Details of the user after updating the avatar.
    """

    public_id = f"Application/{user.email}"
    image = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    print(image)
    image_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop=True,
                                                                version=image.get('version'))
    user = await repository_users.update_avatar_url(user.email, image_url, db)
    return user

