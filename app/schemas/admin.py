from pydantic import BaseModel, HttpUrl
from typing import Optional
from decimal import Decimal
from datetime import date

from app.models.booking import BookingStatus
from app.schemas.user import UserRead

# --- Booking Schemas ---
class RoomForBookingAdmin(BaseModel):
    id: int
    name: str
    hotel_id: int
    
    class Config:
        from_attributes = True

class BookingAdminRead(BaseModel):
    id: int
    user: UserRead
    room: RoomForBookingAdmin
    check_in: date
    check_out: date
    total_price: Decimal
    status: BookingStatus

    class Config:
        from_attributes = True

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

# --- Hotel & Room Create Schemas ---
class HotelCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class RoomCreate(BaseModel):
    hotel_id: int
    name: str
    description: Optional[str] = None
    price_per_night: Decimal
    capacity: int
    image_url: Optional[HttpUrl] = None
