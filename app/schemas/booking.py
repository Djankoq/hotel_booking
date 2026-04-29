from pydantic import BaseModel
from datetime import date
from typing import Optional

class BookingCreate(BaseModel):
    title: str
    location: str
    price: float
    date: date
    description: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    title: str
    location: str
    price: float
    date: date
    description: Optional[str]
    is_confirmed: bool
    
    class Config:
        from_attributes = True