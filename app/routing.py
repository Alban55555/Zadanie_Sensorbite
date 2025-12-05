# app/routing.py
import logging
from typing import Tuple, List

import networkx as nx
from shapely.geometry import Point, LineString, mapping

logger = logging.getLogger(__name__)


def _nearest_node(G: nx.MultiDiGraph, lat: float, lon: float) -> Tuple[float, float]:
    """Najbliższy węzeł grafu do podanej współrzędnej."""
    target = Point(lon, lat)
    nearest = None
    best_dist = float("inf")

    for node in G.nodes:
        p = Point(node[0], node[1])
        d = p.distance(target)
        if d < best_dist:
            best_dist = d
            nearest = node

    if nearest is None:
        raise ValueError("No nodes found in graph")

    return nearest


def compute_safe_route(G: nx.MultiDiGraph, start_lat: float, start_lon: float,
                       end_lat: float, end_lon: float):
    """Wyznacza trasę unikając krawędzi z atrybutem flooded=True."""
    logger.info("Computing route from (%s,%s) to (%s,%s)",
                start_lat, start_lon, end_lat, end_lon)

    source = _nearest_node(G, start_lat, start_lon)
    target = _nearest_node(G, end_lat, end_lon)

    def weight(u, v, data):
        # jeśli nie ma length – przyjmij 1.0
        length = data.get("length", 1.0)
        if data.get("flooded"):
            return length * 1000.0
        return length

    path_nodes = nx.dijkstra_path(G, source, target, weight=weight)
    logger.info("Path found with %d nodes", len(path_nodes))

    # budujemy linię routingu i zbieramy metadane
    line_coords: List[Tuple[float, float]] = list(path_nodes)
    line = LineString(line_coords)

    total_length = 0.0
    avoided = 0
    edges = list(zip(path_nodes[:-1], path_nodes[1:]))

    for u, v in edges:
        # networkx MultiDiGraph – bierzemy pierwszą krawędź
        data = list(G.get_edge_data(u, v).values())[0]
        total_length += data["length"]
        if data.get("flooded"):
            avoided += 1

    feature = {
        "type": "Feature",
        "geometry": mapping(line),
        "properties": {
            "length": total_length,
            "nodes": len(path_nodes),
        },
    }

    return feature, {
        "length_m": float(total_length),
        "num_edges": len(edges),
        "avoided_edges": avoided,
    }
