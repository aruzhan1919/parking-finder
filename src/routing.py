"""
routing.py
==========
Road graph loading and shortest-path calculation.

Responsibilities (and ONLY these):
    1. Load the Astana driving graph from OSM (cached to disk)
    2. Given two (lat, lon) points, return driving time in seconds

This module does NOT know about parkings, Flask, or business logic.
"""

import os
from typing import Tuple

import networkx as nx
import osmnx as ox

PLACE_NAME = "Astana, Kazakhstan"
GRAPH_FILE = "data/astana_drive.graphml"

# Module-level cache. Loaded once per process.
_graph: nx.MultiDiGraph | None = None


def get_graph() -> nx.MultiDiGraph:
    """
    Return the Astana driving graph, loading it the first time.

    On first call:
        - if data/astana_drive.graphml exists → load from disk (fast)
        - otherwise → download from OSM and save to disk (~30 sec)

    Subsequent calls return the cached graph instantly.
    """
    global _graph
    if _graph is not None:
        return _graph

    if os.path.exists(GRAPH_FILE):
        _graph = ox.load_graphml(GRAPH_FILE)
    else:
        os.makedirs(os.path.dirname(GRAPH_FILE), exist_ok=True)
        g = ox.graph_from_place(PLACE_NAME, network_type="drive")
        g = ox.add_edge_speeds(g)
        g = ox.add_edge_travel_times(g)
        ox.save_graphml(g, GRAPH_FILE)
        _graph = g

    return _graph


def drive_time_seconds(
    start: Tuple[float, float],
    end: Tuple[float, float],
) -> float:
    """
    Driving time in seconds between two (lat, lon) points.

    Uses Dijkstra on edge `travel_time` (set by ox.add_edge_travel_times).
    Snaps each point to the nearest graph node.

    Raises:
        nx.NetworkXNoPath: if no driving route exists between the points.
    """
    g = get_graph()

    # osmnx.nearest_nodes takes (lon, lat), not (lat, lon)
    start_node = ox.nearest_nodes(g, start[1], start[0])
    end_node = ox.nearest_nodes(g, end[1], end[0])

    return nx.shortest_path_length(g, start_node, end_node, weight="travel_time")
