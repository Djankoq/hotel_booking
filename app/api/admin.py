from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api import deps
from app.models import User
from app.schemas.admin import BookingAdminRead, BookingStatusUpdate, HotelCreate, RoomCreate
from app.schemas.hotel import Hotel as HotelRead, Room as RoomRead
from app.services.admin_service import admin_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(deps.get_current_manager)])

@router.get("/bookings", response_model=List[BookingAdminRead])
async def get_all_bookings(
    user_id: Optional[int] = None,
    hotel_id: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(deps.get_db),
):
    """
   Получить всех бронирований в системе
    """
    bookings = await admin_service.get_all_bookings(db, user_id=user_id, hotel_id=hotel_id, limit=limit, offset=offset)
    return bookings

@router.patch("/bookings/{booking_id}/status", response_model=BookingAdminRead)
async def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Изменить статус бронирования.
    """
    booking = await admin_service.update_booking_status(db, booking_id=booking_id, new_status=payload.status)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.post("/hotels", response_model=HotelRead)
async def create_hotel(
    payload: HotelCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager),
):
    """
    Создать новый отель
    """
    hotel = await admin_service.create_hotel(db, payload=payload, manager_id=current_user.id)
    return hotel

@router.post("/rooms", response_model=RoomRead)
async def create_room(
    payload: RoomCreate,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Создать новую комнату в отеле
    """
    room = await admin_service.create_room(db, payload=payload)
    return room
