from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError, ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate, UserLogin


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def register(self, data: UserCreate) -> User:
        existing = await self.users.get_by_email(data.email)
        if existing is not None:
            raise ConflictError("An account with this email already exists.")

        hashed = hash_password(data.password)
        return await self.users.create(email=data.email, hashed_password=hashed)

    async def login(self, data: UserLogin) -> Token:
        user = await self.users.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            # Deliberately vague: don't reveal whether the email exists.
            raise UnauthorizedError("Incorrect email or password.")

        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)
