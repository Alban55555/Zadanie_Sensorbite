# app/geo_loader.py
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, Tuple

import networkx as nx
from shapely.geometry import shape, LineString, Point, Polygon, MultiPolygon

logger = logging.getLogger("app.geo_loader")


# Default data locations (used e.g. from state.py)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_ROADS = DATA_DIR / "roads.geojson"
DEFAULT_FLOOD_ZONES = DATA_DIR / "flood_zones.geojson"


Coord = Tuple[float, float]  # (lon, lat)


def _load_geojson(path: Path) -> Dict:
    """
    Load a GeoJSON file and return the parsed dict.

    Raises FileNotFoundError or json.JSONDecodeError on failure.
    """
    logger.info("Loading GeoJSON from %s", path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _ensure_graph_node(
    G: nx.Graph, coord_to_id: Dict[Coord, int], coord: Coord
) -> int:
    """
    Map a coordinate (lon, lat) to a node id in the graph.

    Reuses an existing node if that coordinate was already seen, otherwise
    creates a new node with attributes lon/lat.
    """
    if coord in coord_to_id:
        return coord_to_id[coord]

    node_id = len(coord_to_id)
    lon, lat = coord
    G.add_node(node_id, lon=lon, lat=lat)
    coord_to_id[coord] = node_id
    return node_id


def build_road_graph(roads_path: str | Path = DEFAULT_ROADS) -> nx.Graph:
    """
    Build an undirected road graph from a GeoJSON file.

    The roads GeoJSON is expected to be a FeatureCollection of
    LineString or MultiLineString geometries in lon/lat (EPSG:4326).
    Each edge gets at least the attributes:
      - length  (float, in coordinate units)
      - flooded (bool, default False)
    """
    path = Path(roads_path)
    data = _load_geojson(path)

    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{path} is not a FeatureCollection GeoJSON")

    G = nx.Graph()
    coord_to_id: Dict[Coord, int] = {}

    features: Iterable[Dict] = data.get("features", [])
    edge_count = 0

    for feat in features:
        geom = shape(feat.get("geometry", {}))
        if geom.is_empty:
            continue

        # Normalize: treat MultiLineString as multiple LineStrings
        lines: Iterable[LineString]
        if isinstance(geom, LineString):
            lines = [geom]
        else:
            try:
                # MultiLineString or similar iterable of LineStrings
                lines = list(geom.geoms)  # type: ignore[attr-defined]
            except Exception:
                logger.debug(
                    "Skipping unsupported geometry type %s", geom.geom_type
                )
                continue

        for line in lines:
            coords = list(line.coords)
            if len(coords) < 2:
                continue

            # Edges between consecutive vertices
            for a, b in zip(coords[:-1], coords[1:]):
                coord_a: Coord = (float(a[0]), float(a[1]))
                coord_b: Coord = (float(b[0]), float(b[1]))

                u = _ensure_graph_node(G, coord_to_id, coord_a)
                v = _ensure_graph_node(G, coord_to_id, coord_b)

                seg = LineString([coord_a, coord_b])
                length = float(seg.length)

                # If there are parallel edges, keep the shortest one
                if G.has_edge(u, v):
                    existing_len = G[u][v].get("length", length)
                    if length >= existing_len:
                        continue

                G.add_edge(u, v, length=length, flooded=False)
                edge_count += 1

    logger.info(
        "Graph built from %s: %d nodes, %d edges",
        path,
        G.number_of_nodes(),
        edge_count,
    )
    return G


def _load_flood_polygons(flood_path: Path) -> list[Polygon | MultiPolygon]:
    """
    Load flood polygons from a GeoJSON file.
    Returns a list of Shapely Polygon / MultiPolygon geometries.
    """
    data = _load_geojson(flood_path)

    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{flood_path} is not a FeatureCollection GeoJSON")

    polys: list[Polygon | MultiPolygon] = []
    for feat in data.get("features", []):
        geom = shape(feat.get("geometry", {}))
        if isinstance(geom, (Polygon, MultiPolygon)) and not geom.is_empty:
            polys.append(geom)

    logger.info("Loaded %d flood zone polygons from %s", len(polys), flood_path)
    return polys


def build_hazard_index(
    G: nx.Graph, flood_path: str | Path = DEFAULT_FLOOD_ZONES
) -> dict:
    """
    Mark edges that intersect any flood polygon as 'flooded = True'.

    Returns a small statistics dict, e.g.:
        {
            "num_edges": <int>,
            "num_flooded_edges": <int>
        }

    This function has a side effect on G: it updates the 'flooded'
    attribute on each edge.
    """
    path = Path(flood_path)
    if not path.exists():
        logger.warning(
            "Flood zones file %s does not exist; leaving all edges as not flooded.",
            path,
        )
        return {"num_edges": G.number_of_edges(), "num_flooded_edges": 0}

    polys = _load_flood_polygons(path)
    if not polys:
        logger.warning(
            "No valid flood polygons found in %s; leaving edges unchanged.", path
        )
        return {"num_edges": G.number_of_edges(), "num_flooded_edges": 0}

    num_flooded = 0

    for u, v, data in G.edges(data=True):
        # Build segment between node coordinates
        lon_u, lat_u = G.nodes[u]["lon"], G.nodes[u]["lat"]
        lon_v, lat_v = G.nodes[v]["lon"], G.nodes[v]["lat"]
        seg = LineString([(lon_u, lat_u), (lon_v, lat_v)])

        flooded = False
        for poly in polys:
            # simple intersection test; good enough for prototype
            if seg.intersects(poly):
                flooded = True
                break

        data["flooded"] = flooded
        if flooded:
            num_flooded += 1

    logger.info(
        "Hazard index built from %s: %d / %d edges marked as flooded",
        path,
        num_flooded,
        G.number_of_edges(),
    )

    return {"num_edges": G.number_of_edges(), "num_flooded_edges": num_flooded}
