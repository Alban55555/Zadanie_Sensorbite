# app/state.py
from __future__ import annotations

import logging
from typing import Dict

import networkx as nx

from app.geo_loader import (
    build_road_graph,
    build_hazard_index,
    DEFAULT_ROADS,
    DEFAULT_FLOOD_ZONES,
)

logger = logging.getLogger("app.state")


# ---------------------------------------------------------------------------
# Global application state
# ---------------------------------------------------------------------------

try:
    # Build the road graph from GeoJSON
    GRAPH: nx.Graph = build_road_graph(DEFAULT_ROADS)

    # Mark flooded edges and get some statistics
    HAZARD_STATS: Dict = build_hazard_index(GRAPH, DEFAULT_FLOOD_ZONES)

    logger.info(
        "Application state initialized: %d nodes, %d edges "
        "(%d flooded edges)",
        GRAPH.number_of_nodes(),
        GRAPH.number_of_edges(),
        HAZARD_STATS.get("num_flooded_edges", 0),
    )

except Exception as exc:  # fail-safe: never crash on import
    logger.exception("Failed to initialize application state: %s", exc)
    GRAPH = nx.Graph()
    HAZARD_STATS = {"num_edges": 0, "num_flooded_edges": 0}


# ---------------------------------------------------------------------------
# Public helper functions
# ---------------------------------------------------------------------------

def get_graph() -> nx.Graph:
    """
    Return the global road graph.

    Use this in routing code instead of rebuilding the graph every request.
    """
    return GRAPH


def get_hazard_stats() -> Dict:
    """
    Return statistics about the current hazard index:
        - num_edges
        - num_flooded_edges
    """
    return HAZARD_STATS
