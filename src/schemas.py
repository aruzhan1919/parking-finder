"""
schemas.py
==========
Pydantic-модели для валидации запроса/ответа API.
"""

from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

Coords = Tuple[float, float]


class FindParkingRequest(BaseModel):
    """Вход POST /find-parking."""

    start: Coords = Field(..., description="(lat, lon) старта водителя")
    dest: Coords = Field(..., description="(lat, lon) назначения")


class ParkingResult(BaseModel):
    """Одна парковка в ответе."""

    id: str
    coords: Coords
    name: str
    address: str
    capacity: Optional[int] = None
    price: Optional[str] = None
    tags: List[str] = []
    drive_time_sec: float
    walk_time_sec: float


class FindParkingResponse(BaseModel):
    """Выход POST /find-parking."""

    parkings: List[ParkingResult]
