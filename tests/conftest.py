import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db, engine
from app.core.config import settings

# Используем SQLite для тестов, чтобы не нужен был Docker
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_booking.sqlite"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Создает и удаляет таблицы для каждого теста"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Возвращает сессию БД для теста"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """HTTP клиент, использующий тестовую БД"""
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def user_token(client: AsyncClient):
    """Регистрирует юзера и возвращает токен"""
    await client.post("/auth/register", json={"username": "tester", "password": "123"})
    resp = await client.post("/auth/login", json={"username": "tester", "password": "123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}