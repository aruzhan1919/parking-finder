"""
finder.py
=========
Бизнес-логика: по точкам start и dest найти N лучших парковок.

"Лучшая" = минимальное суммарное время (доезд до парковки + пешком до dest).
Парковки берутся из 2GIS в радиусе вокруг dest (см. parking_data).

Этот модуль НЕ знает про Flask и HTTP — принимает координаты,
возвращает список словарей. Легко тестируется.
"""

from typing import List, Tuple

from geopy.distance import geodesic

from src.parking_data import get_parkings_near
from src.routing import drive_time_seconds

# Средняя скорость пешехода, м/с (~4.7 км/ч)
WALK_SPEED_MPS = 1.3


def _walk_time_seconds(
    from_coords: Tuple[float, float],
    to_coords: Tuple[float, float],
) -> float:
    """Время пешком по прямой (геодезическое расстояние / скорость)."""
    distance_m = geodesic(from_coords, to_coords).meters
    return distance_m / WALK_SPEED_MPS


def find_nearest_parkings(
    start: Tuple[float, float],
    dest: Tuple[float, float],
    top_n: int = 5,
    radius_m: int = 1000,
) -> List[dict]:
    """
    Вернуть top_n парковок с минимальным (drive_time + walk_time).

    Парковки ищутся в радиусе radius_m вокруг dest через 2GIS.

    Args:
        start:    (lat, lon) старта водителя
        dest:     (lat, lon) назначения
        top_n:    сколько парковок вернуть
        radius_m: радиус поиска вокруг dest

    Returns:
        Список словарей, отсортированный по суммарному времени:
            {id, coords, name, address, capacity, price, tags,
             drive_time_sec, walk_time_sec}
    """
    parkings = get_parkings_near(dest, radius_m=radius_m)

    results = []
    for parking in parkings:
        drive_t = drive_time_seconds(start, parking["coords"])
        walk_t = _walk_time_seconds(parking["coords"], dest)
        results.append(
            {
                "id": parking["id"],
                "coords": parking["coords"],
                "name": parking["name"],
                "address": parking["address"],
                "capacity": parking["capacity"],
                "price": parking["price"],
                "tags": parking["tags"],
                "drive_time_sec": drive_t,
                "walk_time_sec": walk_t,
            }
        )

    results.sort(key=lambda r: r["drive_time_sec"] + r["walk_time_sec"])
    return results[:top_n]
