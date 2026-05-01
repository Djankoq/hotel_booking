from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.models.booking import Booking
from app.models.room import Room


class BookingService:

    async def create_booking(self, db: AsyncSession, user_id: int, room: Room, check_in, check_out):

        # 1. Валидация дат
        if check_in >= check_out:
            raise ValueError("check_in must be earlier than check_out")

        # 2. Проверка double booking
        query = await db.execute(
            select(Booking).where(
                Booking.room_id == room.id,
                Booking.status != "cancelled",
                ~(
                    (Booking.check_out <= check_in) |
                    (Booking.check_in >= check_out)
                )
            )
        )

        if query.scalars().first():
            raise ValueError("Room already booked")

        # 3. Расчёт стоимости
        nights = (check_out - check_in).days
        total_price = nights * room.price_per_night

        # 4. Создание брони
        booking = Booking(
            user_id=user_id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status="pending"
        )

        db.add(booking)
        await db.commit()
        await db.refresh(booking)

        return booking


booking_service = BookingService()