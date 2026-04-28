from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, not_, select
from sqlalchemy.orm import selectinload, contains_eager
from app.models.hotel import Hotel, Room
from app.models.booking import Booking
from typing import Optional
from datetime import date


class HotelService:
    async def get_multi(
            self,
            db: AsyncSession,
            *,
            location: Optional[str] = None,
            price_from: Optional[int] = None,
            price_to: Optional[int] = None,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            limit: int = 10,
            offset: int = 0
    ):
        query = select(Hotel)

        if location:
            query = query.where(Hotel.location.ilike(f"%{location}%"))

        filters = []
        if price_from:
            filters.append(Room.price_per_night >= price_from)

        if price_to:
            filters.append(Room.price_per_night <= price_to)

        if date_from and date_to:
            booked_rooms = (
                select(Booking.room_id)
                .where(
                    or_(
                        and_(Booking.check_in <= date_from, Booking.check_out >= date_from),
                        and_(Booking.check_in <= date_to, Booking.check_out >= date_to),
                        and_(Booking.check_in >= date_from, Booking.check_out <= date_to),
                    )
                )
                .subquery()
            )
            filters.append(not_(Room.id.in_(booked_rooms)))

        if filters:
            query = query.join(Room).where(and_(*filters)).options(contains_eager(Hotel.rooms))
        else:
            query = query.options(selectinload(Hotel.rooms))


        result = await db.execute(query.offset(offset).limit(limit))
        return result.scalars().unique().all()

    async def get_rooms_by_hotel(self, db: AsyncSession, *, hotel_id: int):
        query = select(Room).where(Room.hotel_id == hotel_id)
        result = await db.execute(query)
        return result.scalars().all()


hotel_service = HotelService()
