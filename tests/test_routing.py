"""
Tests for routing.py
"""

import pytest

from src.routing import drive_time_seconds


def test_drive_time_is_positive():
    """Время между двумя разными точками должно быть > 0."""
    t = drive_time_seconds((51.13, 71.43), (51.12, 71.42))
    assert t > 0


def test_drive_time_zero_for_same_point():
    """Из точки в неё же — 0 секунд."""
    t = drive_time_seconds((51.13, 71.43), (51.13, 71.43))
    assert t == 0


def test_drive_time_grows_with_distance():
    """Дальше точка → дольше ехать."""
    near = drive_time_seconds((51.13, 71.43), (51.131, 71.431))
    far = drive_time_seconds((51.13, 71.43), (51.09, 71.41))
    assert far > near


def test_drive_time_returns_float():
    """Результат должен быть числом."""
    t = drive_time_seconds((51.13, 71.43), (51.12, 71.42))
    assert isinstance(t, (int, float))
