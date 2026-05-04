from pydantic import BaseModel
from datetime import date

from app.models.booking import BookingStatus
from app.schemas.hotel import Room



class BookedRoom(BaseModel):
    id: int
    user: int
    room: int
    check_in: date
    check_out: date
    created_at: date
    status: BookingStatus

    class Config:
        from_attributes = True

