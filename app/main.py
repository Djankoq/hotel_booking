from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.booking import Booking
from app.schemas.user import UserCreate, UserLogin, Token
from app.schemas.booking import BookingCreate, BookingResponse
from app.core.config import settings

app = FastAPI(title="Booking Project")

# --- Security Utils ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def get_password_hash(password): return pwd_context.hash(password)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username: raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user: raise HTTPException(401, "User not found")
    return user

# --- Routes ---

@app.post("/auth/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    return {"msg": "User created"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(401, "Wrong credentials")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/bookings/", response_model=List[BookingResponse])
async def get_bookings(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Booking).offset(skip).limit(limit))
    return result.scalars().all()

@app.post("/bookings/", response_model=BookingResponse, status_code=201)
async def create_booking(booking: BookingCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_booking = Booking(**booking.model_dump(), user_id=current_user.id)
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking