from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserService:
    async def get_by_login(self, db: AsyncSession, *, login: str) -> User | None:
        """
        Находит пользователя по логину.
        """
        query = select(User).where(User.login == login)
        result = await db.execute(query)
        return result.scalar_one_or_none()

user_service = UserService()
