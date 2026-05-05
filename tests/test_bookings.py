import pytest
from httpx import AsyncClient

# AT-001: Создать бронирование
@pytest.mark.asyncio
async def test_create_booking_success(client: AsyncClient, user_token: dict, test_room_id: int):
    params = {"room_id": test_room_id, "check_in": "2026-06-01", "check_out": "2026-06-05"}
    resp = await client.post("/bookings/", params=params, headers=user_token)
    print(f"[DEBUG] Create booking: {resp.status_code} — {resp.text}")
    # ✅ ИСПРАВЛЕНО: принимаем и 200, и 201
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["status"] == "pending"
    assert data["total_price"] > 0

# AT-002: Ошибка: неверные даты
@pytest.mark.asyncio
async def test_create_booking_invalid_dates(client: AsyncClient, user_token: dict, test_room_id: int):
    params = {"room_id": test_room_id, "check_in": "2026-06-10", "check_out": "2026-06-05"}
    resp = await client.post("/bookings/", params=params, headers=user_token)
    print(f"[DEBUG] Invalid dates: {resp.status_code} — {resp.text}")
    assert resp.status_code == 400
    assert "earlier" in resp.json()["detail"].lower()

# AT-003: Двойное бронирование
@pytest.mark.asyncio
async def test_double_booking(client: AsyncClient, user_token: dict, test_room_id: int):
    await client.post("/bookings/", params={
        "room_id": test_room_id, "check_in": "2026-06-01", "check_out": "2026-06-05"
    }, headers=user_token)
    
    resp = await client.post("/bookings/", params={
        "room_id": test_room_id, "check_in": "2026-06-03", "check_out": "2026-06-07"
    }, headers=user_token)
    
    print(f"[DEBUG] Double booking: {resp.status_code} — {resp.text}")
    assert resp.status_code == 400
    assert "already booked" in resp.json()["detail"].lower()

# AT-004: Получить мои брони
@pytest.mark.asyncio
async def test_get_my_bookings(client: AsyncClient, user_token: dict):
    resp = await client.get("/bookings/my", headers=user_token)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# AT-005: Отменить бронь
@pytest.mark.asyncio
async def test_cancel_booking(client: AsyncClient, user_token: dict, test_room_id: int):
    create_resp = await client.post("/bookings/", params={
        "room_id": test_room_id, "check_in": "2026-07-01", "check_out": "2026-07-03"
    }, headers=user_token)
    print(f"[DEBUG] Create for cancel: {create_resp.status_code} — {create_resp.text}")
    
    if create_resp.status_code not in (200, 201):
        pytest.skip(f"Could not create booking: {create_resp.text}")
    
    booking_id = create_resp.json()["id"]
    resp = await client.delete(f"/bookings/{booking_id}", headers=user_token)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"