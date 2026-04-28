from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from decimal import Decimal

class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_per_night: Decimal
    capacity: int
    image_url: Optional[HttpUrl] = None

class Room(RoomBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True

class HotelBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class Hotel(HotelBase):
    id: int
    rooms: List[Room] = []

    class Config:
        from_attributes = True