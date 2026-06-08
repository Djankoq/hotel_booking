from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, not_, select, func, distinct
from sqlalchemy.orm import selectinload
from app.models.hotel import Hotel, Room
from app.models.booking import Booking
from typing import Optional, Tuple, List
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
    ) -> Tuple[List[Hotel], int]:

        # --- 1. Базовый запрос для подсчета и для подзапроса ID ---
        # Исправлено: используется .distinct() как метод, чтобы колонка имела имя
        id_query = select(Hotel.id).distinct()
        count_query = select(func.count(distinct(Hotel.id)))

        # --- 2. Применяем фильтры к обоим запросам ---
        if location:
            id_query = id_query.where(Hotel.location.ilike(f"%{location}%"))
            count_query = count_query.where(Hotel.location.ilike(f"%{location}%"))

        room_filters = []
        if price_from:
            room_filters.append(Room.price_per_night >= price_from)
        if price_to:
            room_filters.append(Room.price_per_night <= price_to)
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
            room_filters.append(not_(Room.id.in_(booked_rooms)))

        if room_filters:
            id_query = id_query.join(Room).where(and_(*room_filters))
            count_query = count_query.join(Room).where(and_(*room_filters))

        # --- 3. Выполняем подсчет общего количества ---
        total_count = await db.scalar(count_query)

        # --- 4. Применяем пагинацию к запросу ID и делаем его подзапросом ---
        paginated_ids_subquery = id_query.order_by(Hotel.id).limit(limit).offset(offset).subquery()

        # --- 5. Основной запрос для получения полных данных отелей по ID из подзапроса ---
        main_query = (
            select(Hotel)
            .where(Hotel.id.in_(select(paginated_ids_subquery.c.id)))
            .options(selectinload(Hotel.rooms))
            .order_by(Hotel.id)
        )

        result = await db.execute(main_query)
        hotels = result.scalars().unique().all()

        return hotels, total_count

    async def get_rooms_by_hotel(self, db: AsyncSession, *, hotel_id: int):
        query = select(Room).where(Room.hotel_id == hotel_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def search_location_suggestions(
        self,
        db: AsyncSession,
        *,
        q: str,
        limit: int = 10,
    ) -> List[str]:
        query = (
            select(Hotel.location)
            .where(Hotel.location.ilike(f"%{q}%"))
            .distinct()
            .order_by(Hotel.location)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


hotel_service = HotelService()
