"""
schemas.py
==========
Pydantic models for API request/response validation.

Why Pydantic:
    - Catches bad input before it reaches business logic
    - Automatic JSON serialization
    - Type hints become runtime checks
"""

from typing import List, Tuple

from pydantic import BaseModel, Field


Coords = Tuple[float, float]


class FindParkingRequest(BaseModel):
    """POST /find-parking input."""

    start: Coords = Field(..., description="(lat, lon) of driver's start position")
    dest: Coords = Field(..., description="(lat, lon) of destination")


class ParkingResult(BaseModel):
    """One parking spot in the response."""

    id: str
    coords: Coords
    drive_time_sec: float
    walk_time_sec: float


class FindParkingResponse(BaseModel):
    """POST /find-parking output."""

    parkings: List[ParkingResult]
