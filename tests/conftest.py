import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.database import Base
from app.db.session import get_db

# === Тестовая БД: SQLite ===
TEST_DB_URL = "sqlite+aiosqlite:///./test_hotel.db"
test_engine = create_async_engine(TEST_DB_URL, echo=False, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


# 1️⃣ Авто-создание/удаление таблиц
@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


# 2️⃣ db_session
@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


# 3️⃣ client
@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# 4️⃣ user_token (ИСПРАВЛЕНО: username вместо login)
@pytest_asyncio.fixture(scope="function")
async def user_token(client: AsyncClient):
    # Регистрация (используем login, как в модели)
    reg_resp = await client.post("/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "login": "testuser@example.com",  # ← регистрация принимает login
        "password": "SecurePass123!",
        "is_manager": False
    })
    
    # Вход: используем username + form-data
    login_resp = await client.post("/auth/login", data={
        "username": "testuser@example.com",  # ← ⚠️ login-эндпоинт ждёт username!
        "password": "SecurePass123!"
    })
    
    if login_resp.status_code != 200:
        print(f"\n[DEBUG] Login failed: {login_resp.status_code} — {login_resp.text}")
        raise RuntimeError(f"Login failed: {login_resp.text}")
    
    token_data = login_resp.json()
    token = token_data.get("access_token") or token_data.get("token")
    if not token:
        raise KeyError("access_token not found")
    
    return {"Authorization": f"Bearer {token}"}


# 5️⃣ manager_token (ИСПРАВЛЕНО: username вместо login)
@pytest_asyncio.fixture(scope="function")
async def manager_token(client: AsyncClient):
    await client.post("/auth/register", json={
        "first_name": "Mgr",
        "last_name": "Test",
        "login": "mgr@test.com",
        "password": "Mgr123!",
        "is_manager": True
    })
    
    # Вход: username + form-data
    login_resp = await client.post("/auth/login", data={
        "username": "mgr@test.com",  # ← username, не login!
        "password": "Mgr123!"
    })
    
    if login_resp.status_code != 200:
        print(f"\n[DEBUG] Manager login failed: {login_resp.status_code} — {login_resp.text}")
        raise RuntimeError(f"Manager login failed: {login_resp.text}")
    
    token_data = login_resp.json()
    token = token_data.get("access_token") or token_data.get("token")
    if not token:
        raise KeyError("access_token not found")
    
    return {"Authorization": f"Bearer {token}"}

# === Фикстура: test_room_id (создаёт отель и комнату в тестовой БД) ===
@pytest_asyncio.fixture(scope="function")
async def test_room_id(db_session):
    """Создаёт тестовый отель и комнату, возвращает ID комнаты."""
    from app.models.hotel import Hotel, Room
    from decimal import Decimal
    
    # Создаём тестового "менеджера" (если нет реального юзера с id=1)
    from app.models.user import User
    from app.core.security import hash_password
    
    manager = User(
        first_name="Test",
        last_name="Manager",
        login="testmgr@example.com",
        password_hash=hash_password("Mgr123!"),
        is_manager=True
    )
    db_session.add(manager)
    await db_session.flush()  # Получаем ID без коммита
    
    # Создаём тестовый отель
    hotel = Hotel(
        name="Test Hotel",
        location="Test City",
        description="For testing",
        manager_id=manager.id,
        image_url="https://example.com/test.jpg"
    )
    db_session.add(hotel)
    await db_session.flush()
    
    # Создаём тестовую комнату
    room = Room(
        hotel_id=hotel.id,
        name="Test Room",
        description="Test room for bookings",
        price_per_night=Decimal("1000.00"),
        capacity=2,
        image_url="https://example.com/room.jpg"
    )
    db_session.add(room)
    await db_session.commit()
    await db_session.refresh(room)
    
    return room.id