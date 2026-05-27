"""
Tests for finder.py — business logic.

Note: these tests hit the real Astana graph, so the first run is slow
(downloads ~30MB from OSM). Subsequent runs use the cached graphml.
"""

import pytest

from src.finder import _walk_time_seconds, find_nearest_parkings


def test_walk_time_is_positive():
    """Walk time between two distinct points must be > 0."""
    t = _walk_time_seconds((51.13, 71.43), (51.12, 71.42))
    assert t > 0


def test_walk_time_zero_for_same_point():
    """Walk time from a point to itself is 0."""
    t = _walk_time_seconds((51.13, 71.43), (51.13, 71.43))
    assert t == 0


def test_walk_time_grows_with_distance():
    """Farther destination → longer walk."""
    near = _walk_time_seconds((51.13, 71.43), (51.131, 71.431))
    far = _walk_time_seconds((51.13, 71.43), (51.15, 71.45))
    assert far > near


@pytest.mark.slow
def test_find_nearest_returns_3_parkings():
    """API contract: must return exactly top_n parkings."""
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=3,
    )
    assert len(results) == 3


@pytest.mark.slow
def test_results_are_sorted_by_total_time():
    """Parkings must be returned in ascending order of (drive + walk)."""
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=3,
    )
    totals = [r["drive_time_sec"] + r["walk_time_sec"] for r in results]
    assert totals == sorted(totals)


@pytest.mark.slow
def test_result_shape():
    """Every result must have the 4 expected keys."""
    results = find_nearest_parkings(
        start=(51.13, 71.43),
        dest=(51.125, 71.428),
        top_n=1,
    )
    r = results[0]
    assert set(r.keys()) == {"id", "coords", "drive_time_sec", "walk_time_sec"}
