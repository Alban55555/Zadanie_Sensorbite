# app/geo_loader.py
import json
import logging
from pathlib import Path
from typing import Iterable

import networkx as nx
from shapely.geometry import shape, LineString, Polygon
from shapely.strtree import STRtree

logger = logging.getLogger(__name__)


def load_geojson(path: Path) -> dict:
    logger.info("Loading GeoJSON from %s", path)
    with path.open() as f:
        return json.load(f)


def build_hazard_index(flood_fc: dict) -> tuple[STRtree, list[Polygon]]:
    polys = [shape(f["geometry"]) for f in flood_fc["features"]]
    index = STRtree(polys)
    return index, polys


def build_road_graph(roads_fc: dict, hazard_index: STRtree | None = None) -> nx.MultiDiGraph:
    """Buduje graf dróg z opcjonalnym oznaczeniem krawędzi jako zagrożone."""
    G = nx.MultiDiGraph()

    for feat in roads_fc["features"]:
        geom = shape(feat["geometry"])
        if not isinstance(geom, LineString):
            continue

        coords = list(geom.coords)
        # prosty wariant – jeden edge między początkiem a końcem
        start = coords[0]
        end = coords[-1]

        flooded = False
        if hazard_index is not None:
            # szybkie sprawdzenie – czy linia przecina jakikolwiek poligon
            for poly in hazard_index.query(geom):
                if geom.intersects(poly):
                    flooded = True
                    break

        length = geom.length  # w jednostkach układu współrzędnych; do prototypu wystarczy

        G.add_edge(
            start,
            end,
            geometry=geom,
            length=length,
            flooded=flooded,
            raw_properties=feat.get("properties", {}),
        )
        # zakładamy ruch dwukierunkowy:
        G.add_edge(
            end,
            start,
            geometry=geom,
            length=length,
            flooded=flooded,
            raw_properties=feat.get("properties", {}),
        )

    logger.info("Graph built: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
    return G
