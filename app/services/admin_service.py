from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.models import Booking, Hotel, Room
from app.models.booking import BookingStatus
from app.schemas.admin import HotelCreate, RoomCreate


class AdminService:
    async def get_all_bookings(
            self, db: AsyncSession, *, user_id: Optional[int], hotel_id: Optional[int], limit: int, offset: int
    ):
        query = select(Booking).options(selectinload(Booking.user), selectinload(Booking.room).selectinload(Room.hotel))

        if user_id:
            query = query.where(Booking.user_id == user_id)
        if hotel_id:
            query = query.join(Room).where(Room.hotel_id == hotel_id)

        result = await db.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

    async def update_booking_status(self, db: AsyncSession, *, booking_id: int, new_status: BookingStatus):
        query = select(Booking).where(Booking.id == booking_id).options(selectinload(Booking.user),
                                                                        selectinload(Booking.room))
        result = await db.execute(query)
        booking = result.scalar_one_or_none()

        if booking:
            booking.status = new_status
            await db.commit()
            await db.refresh(booking)
        return booking

    async def create_hotel(self, db: AsyncSession, *, payload: HotelCreate, manager_id: int):
        hotel_data = payload.model_dump()
        if hotel_data.get("image_url"):
            hotel_data["image_url"] = str(hotel_data["image_url"])

        hotel = Hotel(**hotel_data, manager_id=manager_id)
        db.add(hotel)
        await db.commit()
        await db.refresh(hotel)

        query = select(Hotel).where(Hotel.id == hotel.id).options(selectinload(Hotel.rooms))
        result = await db.execute(query)
        return result.scalar_one()

    async def create_room(self, db: AsyncSession, *, payload: RoomCreate):
        room_data = payload.model_dump()
        if room_data.get("image_url"):
            room_data["image_url"] = str(room_data["image_url"])

        room = Room(**room_data)
        db.add(room)
        await db.commit()
        await db.refresh(room)

        query = select(Room).where(Room.id == room.id)
        result = await db.execute(query)
        return result.scalar_one()


admin_service = AdminService()
