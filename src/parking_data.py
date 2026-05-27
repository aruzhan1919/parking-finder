"""
parking_data.py
===============
Hardcoded parking spots for the MVP.

In a real version this would come from a database or OSM tags
(amenity=parking). For now: 15 manually picked points around
central Astana, enough to test the finder logic.

Each spot has:
    id:     unique string
    coords: (lat, lon)
"""

from typing import List, Tuple, TypedDict


class Parking(TypedDict):
    id: str
    coords: Tuple[float, float]


PARKINGS: List[Parking] = [
    {"id": "p01", "coords": (51.1281, 71.4304)},
    {"id": "p02", "coords": (51.1265, 71.4287)},
    {"id": "p03", "coords": (51.1248, 71.4319)},
    {"id": "p04", "coords": (51.1295, 71.4341)},
    {"id": "p05", "coords": (51.1232, 71.4276)},
    {"id": "p06", "coords": (51.1218, 71.4298)},
    {"id": "p07", "coords": (51.1276, 71.4252)},
    {"id": "p08", "coords": (51.1303, 71.4289)},
    {"id": "p09", "coords": (51.1241, 71.4365)},
    {"id": "p10", "coords": (51.1259, 71.4378)},
    {"id": "p11", "coords": (51.1287, 71.4231)},
    {"id": "p12", "coords": (51.1224, 71.4348)},
    {"id": "p13", "coords": (51.1312, 71.4267)},
    {"id": "p14", "coords": (51.1196, 71.4321)},
    {"id": "p15", "coords": (51.1271, 71.4395)},
]


def get_all_parkings() -> List[Parking]:
    """Return all known parking spots."""
    return PARKINGS
