"""
finder.py
=========
Business logic: given a start and a destination, find the N best parkings.

"Best" for the MVP = lowest combined time (drive to parking + walk to dest).
This module does NOT know about Flask or HTTP — only takes coords and
returns a list of dicts. Easy to test in isolation.
"""

from typing import List, Tuple

from geopy.distance import geodesic

from src.parking_data import get_all_parkings
from src.routing import drive_time_seconds

# Average pedestrian walking speed in meters per second (~4.7 km/h)
WALK_SPEED_MPS = 1.3


def _walk_time_seconds(
    from_coords: Tuple[float, float],
    to_coords: Tuple[float, float],
) -> float:
    """
    Straight-line walking time in seconds.

    Geodesic distance (real-world spherical) divided by avg walking speed.
    This is an approximation — real pedestrian routing would use a walk graph.
    """
    distance_m = geodesic(from_coords, to_coords).meters
    return distance_m / WALK_SPEED_MPS


def find_nearest_parkings(
    start: Tuple[float, float],
    dest: Tuple[float, float],
    top_n: int = 3,
) -> List[dict]:
    """
    Return the top_n parkings minimizing (drive_time + walk_time).

    Args:
        start:  driver's current (lat, lon)
        dest:   destination (lat, lon)
        top_n:  how many parkings to return

    Returns:
        List of dicts, sorted by total time ascending:
            {id, coords, drive_time_sec, walk_time_sec}
    """
    results = []

    for parking in get_all_parkings():
        drive_t = drive_time_seconds(start, parking["coords"])
        walk_t = _walk_time_seconds(parking["coords"], dest)

        results.append(
            {
                "id": parking["id"],
                "coords": parking["coords"],
                "drive_time_sec": drive_t,
                "walk_time_sec": walk_t,
            }
        )

    results.sort(key=lambda r: r["drive_time_sec"] + r["walk_time_sec"])
    return results[:top_n]
