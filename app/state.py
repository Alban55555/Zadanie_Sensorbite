# app/state.py
from functools import lru_cache
from pathlib import Path
from .geo_loader import load_geojson, build_hazard_index, build_road_graph

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@lru_cache(maxsize=1)
def get_graph():
    roads = load_geojson(DATA_DIR / "roads.geojson")
    floods = load_geojson(DATA_DIR / "flood_zones.geojson")
    index, _ = build_hazard_index(floods)
    return build_road_graph(roads, index)
