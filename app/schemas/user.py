from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    login: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)
    is_manager: bool = False


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    is_manager: bool
    created_at: datetime

    model_config = {"from_attributes": True}

