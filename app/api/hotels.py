from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.hotel import Hotel, Room
from app.services.hotel_service import hotel_service
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.get("/", response_model=List[Hotel])
async def get_hotels(
    location: Optional[str] = None,
    price_from: Optional[int] = None,
    price_to: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Получение списка отлей с возможностью фильтрации по параметрам
    """
    hotels = await hotel_service.get_multi(
        db,
        location=location,
        price_from=price_from,
        price_to=price_to,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return hotels


@router.get("/{hotel_id}/rooms", response_model=List[Room])
async def get_hotel_rooms(
    hotel_id: int,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Получение списка комнат в отеле по его id
    """
    rooms = await hotel_service.get_rooms_by_hotel(db, hotel_id=hotel_id)
    return rooms