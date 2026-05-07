import pytest
from httpx import AsyncClient

# AT-001: Регистрация обычного пользователя
@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Регистрация обычного пользователя (is_manager=false)"""
    resp = await client.post("/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "login": "user@test.com",
        "password": "Pass123!",
        "is_manager": False
    })
    print(f"[DEBUG] Register user: {resp.status_code}")
    assert resp.status_code == 201
    data = resp.json()
    assert data["login"] == "user@test.com"
    assert "password" not in data  # Пароль не должен возвращаться

# AT-002: Регистрация менеджера
@pytest.mark.asyncio
async def test_register_manager(client: AsyncClient):
    """Регистрация менеджера (is_manager=true)"""
    resp = await client.post("/auth/register", json={
        "first_name": "Manager",
        "last_name": "Test",
        "login": "manager@test.com",
        "password": "Pass123!",
        "is_manager": True
    })
    print(f"[DEBUG] Register manager: {resp.status_code}")
    assert resp.status_code == 201
    data = resp.json()
    assert data["login"] == "manager@test.com"
    assert data["is_manager"]

# AT-003: Регистрация с дубликатом логина
@pytest.mark.asyncio
async def test_register_duplicate_login(client: AsyncClient):
    """Повторная регистрация с тем же логином должна вернуть ошибку"""
    # Первая регистрация
    await client.post("/auth/register", json={
        "first_name": "First",
        "last_name": "User",
        "login": "duplicate@test.com",
        "password": "Pass123!",
        "is_manager": False
    })
    
    # Вторая регистрация с тем же логином
    resp = await client.post("/auth/register", json={
        "first_name": "Second",
        "last_name": "User",
        "login": "duplicate@test.com",
        "password": "Pass123!",
        "is_manager": False
    })
    print(f"[DEBUG] Duplicate login: {resp.status_code}")
    assert resp.status_code == 409  # Conflict
    assert "already exists" in resp.json()["detail"].lower()

# AT-004: Успешный вход
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Вход с верными учётными данными"""
    # Сначала регистрируем пользователя
    await client.post("/auth/register", json={
        "first_name": "Login",
        "last_name": "Test",
        "login": "login@test.com",
        "password": "Pass123!",
        "is_manager": False
    })
    
    # Входим (OAuth2 использует username)
    resp = await client.post("/auth/login", data={
        "username": "login@test.com",
        "password": "Pass123!"
    })
    print(f"[DEBUG] Login success: {resp.status_code}")
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

# AT-005: Вход с неверным паролем
@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Вход с неверным паролем должен вернуть ошибку"""
    # Регистрируем пользователя
    await client.post("/auth/register", json={
        "first_name": "Wrong",
        "last_name": "Pass",
        "login": "wrongpass@test.com",
        "password": "CorrectPass123!",
        "is_manager": False
    })
    
    # Пробуем войти с неправильным паролем
    resp = await client.post("/auth/login", data={
        "username": "wrongpass@test.com",
        "password": "WrongPass123!"
    })
    print(f"[DEBUG] Wrong password: {resp.status_code}")
    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()