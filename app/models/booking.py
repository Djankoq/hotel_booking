from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text
from app.db.base import Base

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
    is_confirmed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)