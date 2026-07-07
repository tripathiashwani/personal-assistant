import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# tokenUrl is only used to populate Swagger's "Authorize" button;
# the actual login endpoint accepts JSON, not this form.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decodes the bearer token, loads the corresponding user, and raises
    401 if anything is wrong. Every protected router (documents, chats,
    and later integrations) depends on this — none of them re-implement
    token parsing.
    """
    if token is None:
        raise UnauthorizedError("Not authenticated.")

    user_id_str = decode_access_token(token)
    if user_id_str is None:
        raise UnauthorizedError("Invalid or expired token.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid token payload.")

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User no longer exists.")

    return user
