"""
parking_data.py
===============
Парковки берутся вживую из 2GIS Places API — в радиусе вокруг точки
назначения. Один поиск пользователя = 1 запрос к API.

Раньше тут был захардкоженный список из 15 точек. Теперь функция
принимает координаты назначения и радиус, и возвращает реальные
парковки 2GIS с богатой информацией (цена, мест, тип, адрес).

Каждая парковка:
    id:       str
    coords:   (lat, lon)
    name:     str
    address:  str
    capacity: int | None     — всего мест
    price:    str | None     — строка цены (например "100 тнг./час")
    tags:     list[str]      — крытая / тёплая / охраняемая и т.п.
"""

import os
from typing import List, Optional, Tuple, TypedDict

import requests
from dotenv import load_dotenv

load_dotenv()

CATALOG_URL = "https://catalog.api.2gis.com/3.0/items"
GIS_CATALOG_KEY = os.getenv("GIS_CATALOG_KEY")

# Сколько парковок просить у 2GIS за один запрос (макс 10 на демо-ключе).
PAGE_SIZE = 10

FIELDS = ",".join(
    [
        "items.point",
        "items.address",
        "items.attribute_groups",
        "items.capacity",
        "items.rubrics",
    ]
)


class Parking(TypedDict):
    id: str
    coords: Tuple[float, float]
    name: str
    address: str
    capacity: Optional[int]
    price: Optional[str]
    tags: List[str]


def _parse_item(item: dict) -> Optional[Parking]:
    """Превратить сырой объект 2GIS в нашу Parking. None если нет координат."""
    point = item.get("point")
    if not point:
        return None

    # Цена и теги — из attribute_groups
    price = None
    tags: List[str] = []
    for group in item.get("attribute_groups", []):
        for attr in group.get("attributes", []):
            tag = attr.get("tag", "")
            name = attr.get("name", "")
            if tag == "parking_cost_parking_hour" and price is None:
                price = name
            elif tag in (
                "parking_indoor_parking",
                "parking_warm_parking",
                "parking_secure_parking",
            ):
                tags.append(name)

    # Вместимость
    capacity = None
    cap = item.get("capacity", {})
    if isinstance(cap, dict) and cap.get("total"):
        try:
            capacity = int(cap["total"])
        except (ValueError, TypeError):
            capacity = None

    return {
        "id": item["id"],
        "coords": (point["lat"], point["lon"]),
        "name": item.get("name", "Парковка"),
        "address": item.get("address_name", ""),
        "capacity": capacity,
        "price": price,
        "tags": tags,
    }


def get_parkings_near(
    dest: Tuple[float, float],
    radius_m: int = 1000,
) -> List[Parking]:
    """
    Найти парковки в радиусе radius_m вокруг точки назначения через 2GIS.

    Один вызов = один запрос к API (PAGE_SIZE парковок).

    Args:
        dest:     (lat, lon) точки назначения
        radius_m: радиус поиска в метрах

    Returns:
        Список Parking (может быть пустым).
    """
    if not GIS_CATALOG_KEY:
        raise RuntimeError("GIS_CATALOG_KEY не задан в .env")

    lat, lon = dest
    resp = requests.get(
        CATALOG_URL,
        params={
            "q": "парковка",
            "point": f"{lon},{lat}",  # 2GIS хочет lon,lat
            "radius": radius_m,
            "sort": "distance",
            "fields": FIELDS,
            "page_size": PAGE_SIZE,
            "key": GIS_CATALOG_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    items = resp.json().get("result", {}).get("items", [])

    parkings: List[Parking] = []
    for item in items:
        parsed = _parse_item(item)
        if parsed:
            parkings.append(parsed)
    return parkings
