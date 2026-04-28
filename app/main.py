from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="Hotel Booking API")

from app.api.auth import router as auth_router
from app.api.hotels import router as hotels_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(hotels_router, prefix="/hotels", tags=["hotels"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Hotel Booking API!",
        "db_url_configured": bool(settings.DATABASE_URL)
    }
