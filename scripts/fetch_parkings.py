"""
scripts/fetch_parkings.py

Один раз вытягивает все парковки Астаны из 2GIS Places API
и сохраняет их в data/parkings.json.

Запуск (из корня проекта):
    python -m scripts.fetch_parkings
"""

# import json
# import os
# import time
# from pathlib import Path

# import requests
# from dotenv import load_dotenv

# # Загружаем .env (там лежит GIS_CATALOG_KEY)
# load_dotenv()

# KEY = os.getenv("GIS_CATALOG_KEY")
# if not KEY or KEY.startswith("ВСТАВЬ"):
#     raise SystemExit("❌ Не задан GIS_CATALOG_KEY в .env")

# CATALOG_URL = "https://catalog.api.2gis.com/3.0/items"

# # Покрываем Астану несколькими большими кругами по 5 км.
# # Координаты в (lat, lon) — для удобства чтения, ниже переворачиваются.
# SEARCH_CIRCLES = [
#     ("center", 51.128, 71.430),  # центр
#     ("left_bank", 51.124, 71.405),  # левый берег
#     ("right_bank", 51.165, 71.460),  # правый берег
#     ("north", 51.180, 71.430),  # север
#     ("south", 51.090, 71.430),  # юг
#     ("east", 51.128, 71.510),  # восток
#     ("west", 51.128, 71.350),  # запад
#     ("ne", 51.170, 71.490),  # северо-восток
#     ("nw", 51.170, 71.370),  # северо-запад
#     ("se", 51.090, 71.490),  # юго-восток
#     ("sw", 51.090, 71.370),  # юго-запад
# ]
# RADIUS_M = 5000
# PAGE_SIZE = 50  # максимум для большинства тарифов 2GIS

# # Запрашиваем максимально широкий набор полей.
# # Некоторые могут не прийти на демо-ключе — это нормально.
# FIELDS = ",".join(
#     [
#         "items.point",
#         "items.address",
#         "items.attribute_groups",
#         "items.contact_groups",
#         "items.schedule",
#         "items.rubrics",
#         "items.name_ex",
#         "items.adm_div",
#         "items.capacity",
#     ]
# )


# def fetch_one_page(lat: float, lon: float, page: int) -> dict:
#     """Один запрос — одна страница."""
#     params = {
#         "q": "парковка",,
#         "point": f"{lon},{lat}",  # 2GIS хочет lon,lat!
#         "radius": RADIUS_M,
#         "fields": FIELDS,
#         "page_size": PAGE_SIZE,
#         "page": page,
#         "key": KEY,
#     }
#     resp = requests.get(CATALOG_URL, params=params, timeout=15)
#     resp.raise_for_status()
#     return resp.json()


# def fetch_circle(name: str, lat: float, lon: float) -> list:
#     """Все страницы для одного круга поиска."""
#     items = []
#     page = 1
#     while True:
#         print(f"  → круг '{name}', страница {page}...", end=" ")
#         data = fetch_one_page(lat, lon, page)
#         result = data.get("result", {})
#         page_items = result.get("items", [])
#         total = result.get("total", 0)
#         print(f"получено {len(page_items)} (всего в круге: {total})")
#         items.extend(page_items)

#         if len(page_items) < PAGE_SIZE or len(items) >= total:
#             break
#         page += 1
#         time.sleep(0.3)  # вежливая пауза между запросами
#     return items


# def main():
#     print(f"🔍 Тяну парковки из 2GIS по {len(SEARCH_CIRCLES)} кругам...\n")
#     all_items = []
#     for name, lat, lon in SEARCH_CIRCLES:
#         items = fetch_circle(name, lat, lon)
#         all_items.extend(items)

#     # Дедупликация по id (круги перекрываются)
#     unique = {}
#     for it in all_items:
#         if "id" in it:
#             unique[it["id"]] = it
#     print(f"\n✓ Всего получено: {len(all_items)}, уникальных: {len(unique)}")

#     # Сохраняем
#     project_root = Path(__file__).resolve().parent.parent
#     out_path = project_root / "data" / "parkings.json"
#     out_path.parent.mkdir(exist_ok=True)
#     with out_path.open("w", encoding="utf-8") as f:
#         json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)

#     print(f"💾 Сохранено в {out_path}")
#     print(f"\nПодсказка: открой файл и посмотри, какие поля реально пришли.")


# if __name__ == "__main__":
#     main()

"""
scripts/fetch_parkings.py

Один раз вытягивает все парковки Астаны из 2GIS Places API
и сохраняет их в data/parkings.json.

Запуск (из корня проекта):
    python -m scripts.fetch_parkings
"""
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("GIS_CATALOG_KEY")
if not KEY or KEY.startswith("ВСТАВЬ"):
    raise SystemExit("❌ Не задан GIS_CATALOG_KEY в .env")

CATALOG_URL = "https://catalog.api.2gis.com/3.0/items"

SEARCH_CIRCLES = [
    ("center", 51.128, 71.430),
    ("left_bank", 51.124, 71.405),
    ("right_bank", 51.165, 71.460),
    ("north", 51.180, 71.430),
    ("south", 51.090, 71.430),
    ("east", 51.128, 71.510),
    ("west", 51.128, 71.350),
    ("ne", 51.170, 71.490),
    ("nw", 51.170, 71.370),
    ("se", 51.090, 71.490),
    ("sw", 51.090, 71.370),
]
RADIUS_M = 5000
PAGE_SIZE = 10
MAX_PAGES_PER_CIRCLE = 3  # 50*10 = 500 объектов с круга, защита лимита

FIELDS = ",".join(
    [
        "items.point",
        "items.address",
        "items.attribute_groups",
        "items.capacity",
        "items.schedule",
        "items.rubrics",
    ]
)


def fetch_one_page(lat: float, lon: float, page: int) -> dict:
    params = {
        "q": "парковка",
        "point": f"{lon},{lat}",
        "radius": RADIUS_M,
        "fields": FIELDS,
        "page_size": PAGE_SIZE,
        "page": page,
        "key": KEY,
    }
    resp = requests.get(CATALOG_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_circle(name: str, lat: float, lon: float) -> list:
    items = []
    for page in range(1, MAX_PAGES_PER_CIRCLE + 1):
        print(f"  → круг '{name}', страница {page}...", end=" ", flush=True)
        data = fetch_one_page(lat, lon, page)
        result = data.get("result", {})
        page_items = result.get("items", [])
        total = result.get("total", 0)
        print(f"получено {len(page_items)} (total: {total})")
        items.extend(page_items)
        if len(page_items) < PAGE_SIZE:
            break
        time.sleep(0.3)
    return items


def main():
    print(
        f"🔍 Тяну парковки по {len(SEARCH_CIRCLES)} кругам "
        f"(до {MAX_PAGES_PER_CIRCLE} страниц на круг)...\n"
    )

    all_items = []
    for name, lat, lon in SEARCH_CIRCLES:
        items = fetch_circle(name, lat, lon)
        all_items.extend(items)

    unique = {}
    for it in all_items:
        if "id" in it:
            unique[it["id"]] = it

    real = [
        it
        for it in unique.values()
        if any(r.get("alias") == "parkingi" for r in it.get("rubrics", []))
        and "point" in it
    ]

    print(f"\n✓ Всего получено: {len(all_items)}")
    print(f"✓ Уникальных: {len(unique)}")
    print(f"✓ Настоящих паркингов с координатами: {len(real)}")

    project_root = Path(__file__).resolve().parent.parent
    out_path = project_root / "data" / "parkings.json"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(real, f, ensure_ascii=False, indent=2)

    print(f"💾 Сохранено в {out_path}")


if __name__ == "__main__":
    main()
