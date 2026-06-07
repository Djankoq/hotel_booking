from pydantic import BaseModel, HttpUrl, ConfigDict, Field
from typing import List, Optional
from decimal import Decimal
from datetime import date

class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_per_night: Decimal = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    image_url: Optional[HttpUrl] = None

class Room(RoomBase):
    id: int
    hotel_id: int
    model_config = ConfigDict(from_attributes=True)

class RoomDetail(Room):
    hotel_name: str
    hotel_description: Optional[str] = None
    hotel_image_url: Optional[HttpUrl] = None

class HotelBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class Hotel(HotelBase):
    id: int
    rooms: List[Room] = []
    model_config = ConfigDict(from_attributes=True)

class HotelsResponse(BaseModel):
    total: int
    hotels: List[Hotel]

class BookingInfo(BaseModel):
    id: int
    room_id: int
    hotel_id: int
    check_in: date
    check_out: date
    total_price: Decimal
    status: str

    class Config:
        from_attributes = True

class MyBookingsResponse(BaseModel):
    user_first_name: str
    user_last_name: str
    user_login: str
    bookings: List[BookingInfo]
