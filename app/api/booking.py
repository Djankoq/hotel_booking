from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import date

from app.api import deps
from app.services.booking_service import booking_service
from app.models.room import Room
from app.models.booking import Booking

router = APIRouter(tags=["bookings"])

@router.post("/")
async def create_booking(
    room_id: int,
    check_in: date,
    check_out: date,
    db: AsyncSession = Depends(deps.get_db),
):
    # 1. найти комнату
    room = await db.get(Room, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # 2. user временно (потом заменим на auth)
    user_id = 1

    # 3. создать бронь через сервис
    try:
        booking = await booking_service.create_booking(
            db, user_id, room, check_in, check_out
        )
        return booking

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my")
async def get_my_bookings(
    db: AsyncSession = Depends(deps.get_db),
):
    user_id = 1  # временно

    result = await db.execute(
        select(Booking).where(Booking.user_id == user_id)
    )

    return result.scalars().all()

@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(deps.get_db),
):
    booking = await db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(404, "Booking not found")

    user_id = 1

    if booking.user_id != user_id:
        raise HTTPException(403, "Not allowed")

    booking.status = "cancelled"
    await db.commit()

    return {"status": "cancelled"}

@router.patch("/{booking_id}")
async def update_booking(
    booking_id: int,
    check_in: date,
    check_out: date,
    db: AsyncSession = Depends(deps.get_db),
):
    booking = await db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(404)

    user_id = 1

    if booking.user_id != user_id:
        raise HTTPException(403)

    if check_in >= check_out:
        raise HTTPException(400, "Invalid dates")

    # проверка доступности (исключая текущую бронь)
    query = await db.execute(
        select(Booking).where(
            Booking.room_id == booking.room_id,
            Booking.id != booking_id,
            Booking.status != "cancelled",
            ~(
                (Booking.check_out <= check_in) |
                (Booking.check_in >= check_out)
            )
        )
    )

    if query.scalars().first():
        raise HTTPException(400, "Room not available")

    # пересчёт цены
    nights = (check_out - check_in).days
    booking.check_in = check_in
    booking.check_out = check_out
    booking.total_price = nights * booking.room.price_per_night

    await db.commit()

    return booking

@router.post("/{booking_id}/confirm")
async def confirm_booking(
    booking_id: int,
    db: AsyncSession = Depends(deps.get_db),
):
    booking = await db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(404)

    booking.status = "confirmed"

    await db.commit()

    return booking