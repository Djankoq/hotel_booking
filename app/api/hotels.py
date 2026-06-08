from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.hotel import Room, HotelsResponse, LocationSuggestionsResponse
from app.services.hotel_service import hotel_service
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.get("/", response_model=HotelsResponse)
async def get_hotels(
    location: Optional[str] = None,
    price_from: Optional[int] = None,
    price_to: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Получение списка отелей с пагинацией и общим количеством.
    """
    limit = page_size
    offset = (page - 1) * page_size

    hotels, total_count = await hotel_service.get_multi(
        db,
        location=location,
        price_from=price_from,
        price_to=price_to,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return {"total": total_count, "hotels": hotels}


@router.get("/locations/suggest", response_model=LocationSuggestionsResponse)
async def suggest_locations(
    q: str = Query(..., min_length=1, description="Часть названия города"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Подсказки локаций для автодополнения в фильтре поиска отелей.
    """
    suggestions = await hotel_service.search_location_suggestions(db, q=q, limit=limit)
    return {"suggestions": suggestions}


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
