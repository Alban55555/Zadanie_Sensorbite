# app/routing.py
import logging
from typing import Tuple, List

import networkx as nx
from shapely.geometry import Point, LineString, mapping

logger = logging.getLogger("app.routing")


def _nearest_node(G: nx.Graph, lat: float, lon: float) -> int:
    """
    Find ID of the node in G that is closest to given (lat, lon).

    Nodes in G are integers with attributes:
        - lon
        - lat
    """
    target = Point(lon, lat)
    nearest_id = None
    best_dist = float("inf")

    for node_id, attrs in G.nodes(data=True):
        p = Point(attrs["lon"], attrs["lat"])
        d = p.distance(target)
        if d < best_dist:
            best_dist = d
            nearest_id = node_id

    if nearest_id is None:
        raise ValueError("No nodes found in graph")

    return nearest_id


def compute_safe_route(
    G: nx.Graph,
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
):
    """
    Compute an evacuation route that penalizes edges marked as flooded.

    Edges in G are expected to have attributes:
        - length  (float)
        - flooded (bool)
    """

    logger.info(
        "Computing route from (%s, %s) to (%s, %s)",
        start_lat,
        start_lon,
        end_lat,
        end_lon,
    )

    source = _nearest_node(G, start_lat, start_lon)
    target = _nearest_node(G, end_lat, end_lon)

    def weight(u, v, data):
        # dijkstra will call this for each edge
        length = data.get("length", 1.0)
        if data.get("flooded"):
            # big penalty for flooded segments
            return length * 1000.0
        return length

    # shortest path in terms of our custom weight
    path_nodes: List[int] = nx.dijkstra_path(G, source, target, weight=weight)
    logger.info("Path found with %d nodes", len(path_nodes))

    # Build list of coordinates for the LineString
    line_coords: List[Tuple[float, float]] = []
    for node_id in path_nodes:
        attrs = G.nodes[node_id]
        line_coords.append((attrs["lon"], attrs["lat"]))

    line = LineString(line_coords)

    total_length = 0.0
    flooded_edges = 0
    edges = list(zip(path_nodes[:-1], path_nodes[1:]))

    for u, v in edges:
        data = G.get_edge_data(u, v) or {}
        length = float(data.get("length", 0.0))
        total_length += length
        if data.get("flooded"):
            flooded_edges += 1

    feature = {
        "type": "Feature",
        "geometry": mapping(line),
        "properties": {
            "length": total_length,
            "nodes": len(path_nodes),
        },
    }

    meta = {
        "length_m": float(total_length),
        "num_edges": len(edges),
        "avoided_edges": flooded_edges,
    }

    return feature, meta
