from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="Hotel Booking API")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Hotel Booking API!",
        "db_url_configured": bool(settings.DATABASE_URL)
    }
