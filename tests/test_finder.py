"""
Тесты для finder.py — бизнес-логика.

Запрос к 2GIS замокан, чтобы тесты не тратили лимит API и работали
офлайн. Тесты, которые считают время доезда, помечены @pytest.mark.slow,
так как используют реальный граф Астаны (первый прогон качает ~30МБ).
"""

from unittest.mock import patch

import pytest

from src.finder import _walk_time_seconds, find_nearest_parkings

# Фейковые парковки, которые «вернёт» 2GIS
FAKE_PARKINGS = [
    {
        "id": "a",
        "coords": (51.126, 71.429),
        "name": "Парковка A",
        "address": "ул. Тест 1",
        "capacity": 100,
        "price": "100 тнг./час",
        "tags": ["Крытая"],
    },
    {
        "id": "b",
        "coords": (51.124, 71.427),
        "name": "Парковка B",
        "address": "ул. Тест 2",
        "capacity": 50,
        "price": None,
        "tags": [],
    },
    {
        "id": "c",
        "coords": (51.130, 71.435),
        "name": "Парковка C",
        "address": "",
        "capacity": None,
        "price": "200 тнг./час",
        "tags": ["Тёплая", "Охраняемая"],
    },
]


def test_walk_time_is_positive():
    t = _walk_time_seconds((51.13, 71.43), (51.12, 71.42))
    assert t > 0


def test_walk_time_zero_for_same_point():
    t = _walk_time_seconds((51.13, 71.43), (51.13, 71.43))
    assert t == 0


def test_walk_time_grows_with_distance():
    near = _walk_time_seconds((51.13, 71.43), (51.131, 71.431))
    far = _walk_time_seconds((51.13, 71.43), (51.15, 71.45))
    assert far > near


@pytest.mark.slow
@patch("src.finder.get_parkings_near")
def test_find_nearest_returns_top_n(mock_get):
    """Должно вернуть ровно top_n парковок."""
    mock_get.return_value = FAKE_PARKINGS
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=2,
    )
    assert len(results) == 2


@pytest.mark.slow
@patch("src.finder.get_parkings_near")
def test_results_are_sorted_by_total_time(mock_get):
    """Парковки отсортированы по возрастанию (доезд + пешком)."""
    mock_get.return_value = FAKE_PARKINGS
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=3,
    )
    totals = [r["drive_time_sec"] + r["walk_time_sec"] for r in results]
    assert totals == sorted(totals)


@pytest.mark.slow
@patch("src.finder.get_parkings_near")
def test_result_shape(mock_get):
    """У каждого результата нужные ключи."""
    mock_get.return_value = FAKE_PARKINGS
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=1,
    )
    r = results[0]
    expected = {
        "id",
        "coords",
        "name",
        "address",
        "capacity",
        "price",
        "tags",
        "drive_time_sec",
        "walk_time_sec",
    }
    assert set(r.keys()) == expected


@patch("src.finder.get_parkings_near")
def test_empty_when_no_parkings(mock_get):
    """Если 2GIS ничего не вернул — пустой список, без ошибки."""
    mock_get.return_value = []
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=5,
    )
    assert results == []
