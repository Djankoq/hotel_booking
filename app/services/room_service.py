from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.hotel import Room


class RoomService:
    async def get_room(
            self,
            db: AsyncSession,
            room_id: int
    ):
        query = select(Room)
        query = query.where(Room.id == room_id)
        result = await db.execute(query)
        return result.scalars().all()

room_service = RoomService()
