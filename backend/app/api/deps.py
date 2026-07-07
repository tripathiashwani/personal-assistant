import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# HTTPBearer makes Swagger's "Authorize" dialog show a single field to
# paste a raw token into. We deliberately don't use OAuth2PasswordBearer
# here — it makes Swagger render a full OAuth2 client_id/client_secret
# form, which doesn't match how our /auth/login endpoint actually works
# (plain JSON body -> JWT), and just confuses anyone testing the API.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decodes the bearer token, loads the corresponding user, and raises
    401 if anything is wrong. Every protected router (documents, chats,
    and later integrations) depends on this — none of them re-implement
    token parsing.
    """
    if credentials is None:
        raise UnauthorizedError("Not authenticated.")

    token = credentials.credentials
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
