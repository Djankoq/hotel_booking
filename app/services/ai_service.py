from datetime import date, datetime
from textdistance import jaccard
from math import sqrt, pow

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


from app.models.booking import Booking
from app.models.hotel import Hotel
from app.models.room import Room

class AIService:
    async def get_last_booked_room(
            self,
            db: AsyncSession,
            user_id: int,
    ):
        #Получение даты последнего забронированного отеля
        latest_date = select(func.max(Booking.created_at)).where((Booking.user_id == user_id) and (Booking.status == "confirmed")).scalar_subquery()

        #Проверка существование даты
        if latest_date is not None:
            query = select(Booking)
            query = query.filter(
                Booking.status == "confirmed",
                Booking.user_id == user_id,
                Booking.created_at == latest_date
            )
            result = await db.execute(query)
            return result.scalars().all()

        else:
            raise ValueError("No booked hotels by the user")

    async def get_recommendations(
            self,
            db: AsyncSession,
            room_id: int,
            limit: 5
    ):
        # Получение запрашиваемой комнаты
        base_room = select(Room).filter(Room.id == room_id)
        base_room = await db.execute(base_room)
        base_room = base_room.scalar_one_or_none()

        # Получение запрашиваемого отеля
        base_hotel = select(Hotel).filter(Hotel.id == base_room.hotel_id)
        base_hotel = await db.execute(base_hotel)
        base_hotel = base_hotel.scalar_one_or_none()

        # Нахождение экстремум для нормализации
        min_price = await db.scalar(select(func.min(Room.price_per_night)))
        max_price = await db.scalar(select(func.max(Room.price_per_night)))
        min_cap = await db.scalar(select(func.min(Room.capacity)))
        max_cap = await db.scalar(select(func.max(Room.capacity)))

        price_range = max_price - min_price
        cap_range = max_cap - min_cap

        # Создания списка всех других комнат для оценки
        other_rooms = select(Room).filter(Room.is_available == True, Room.id != room_id)
        other_rooms = await db.execute(other_rooms)
        other_rooms = other_rooms.scalars().all()

        # Создания списка всех других отелей для оценки
        other_hotels = select(Hotel).where(Hotel.id.in_([room.hotel_id for room in other_rooms]))
        other_hotels = await db.execute(other_hotels)
        other_hotels = {hotel.id: hotel for hotel in other_hotels.scalars().all()}

        results = []

        for current_room in other_rooms:
            current_hotel = other_hotels.get(current_room.hotel_id)

            price_diff_norm = (base_room.price_per_night - current_room.price_per_night) / price_range
            cap_diff_norm = (base_room.capacity - current_room.capacity) / cap_range
            desc_diff_norm = 1 - jaccard.normalized_similarity(set(str(current_room.description).lower().split()), set(str(base_room.description).lower().split()))

            if current_hotel.location == base_hotel.location:
                loc_diff_norm = 0
            else:
                loc_diff_norm = 1

            euclidian_distance = sqrt(pow(price_diff_norm,2) + pow(cap_diff_norm,2) + pow(loc_diff_norm,2) * 0.5 + pow(desc_diff_norm,2)* 0.8)

            results.append((current_room.id, euclidian_distance))

        results.sort(key=lambda x: x[1])
        query = select(Room)
        query = query.where(Room.id.in_([room_id for room_id, _ in results[:limit]]))
        result = await db.execute(query)
        return result.scalars().all()

ai_service = AIService()