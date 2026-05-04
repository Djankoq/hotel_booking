import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.database import Base
from app.db.session import get_db

# === Тестовая БД: SQLite (полная изоляция, 0 правок в docker-compose) ===
TEST_DB_URL = "sqlite+aiosqlite:///./test_hotel.db"
test_engine = create_async_engine(TEST_DB_URL, echo=False, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


# 1️ Авто-создание таблиц перед тестом и удаление после
@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


# 2️⃣ db_session: сессия с автоматическим rollback после теста
@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


# 3️⃣ client: AsyncClient из httpx, стучится в app напрямую
@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session
    
    # Подменяем реальную БД на тестовую сессию
    app.dependency_overrides[get_db] = override_get_db
    
    # ASGITransport работает без запуска сервера (максимально быстро)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Очищаем подмены после теста
    app.dependency_overrides.clear()


# 4️⃣ user_token: регистрирует юзера и возвращает JWT-заголовки
@pytest_asyncio.fixture(scope="function")
async def user_token(client: AsyncClient):
    # Регистрация (поля под вашу модель User)
    await client.post("/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "login": "testuser@example.com",
        "password": "SecurePass123!",
        "is_manager": False
    })
    
    # Вход
    login_resp = await client.post("/auth/login", json={
        "login": "testuser@example.com",
        "password": "SecurePass123!"
    })
    
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}