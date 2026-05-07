from pydantic import BaseModel, HttpUrl, ConfigDict, Field
from typing import List, Optional
from decimal import Decimal

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

class HotelBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class Hotel(HotelBase):
    id: int
    rooms: List[Room] = []
    model_config = ConfigDict(from_attributes=True)