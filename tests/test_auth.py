import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    resp = await client.post("/auth/register", json={"username": "new_user", "password": "secret"})
    assert resp.status_code == 200

    resp = await client.post("/auth/login", json={"username": "new_user", "password": "secret"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient, user_token: dict):
    resp = await client.post("/bookings/", json={
        "title": "Test Hotel", "location": "Moscow", 
        "price": 5000.0, "date": "2026-06-01"
    }, headers=user_token)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test Hotel"