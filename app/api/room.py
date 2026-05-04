from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import date


from app.api import deps
from app.services.room_service import room_service
from app.services.ai_service import ai_service
from app.schemas.hotel import Room
from app.schemas.ai import BookedRoom

router = APIRouter(tags=["room"])

@router.get('/{room_id}/recommendations')
async def get_recommendations(
        room_id: int,
        limit: int,
        db: AsyncSession = Depends(deps.get_db)
):
    """
    Получение списка рекомендованных комнат, по другой комнате
    """
    rooms = await ai_service.get_recommendations(
        db,
        room_id = room_id,
        limit = limit
    )
    return rooms