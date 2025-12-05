# tests/test_routing.py
import sys
from pathlib import Path

from shapely.geometry import LineString, Polygon, mapping

# dodaj katalog projektu (z app/) do sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.geo_loader import build_road_graph, build_hazard_index
from app.routing import compute_safe_route


def _make_simple_network():
    roads_fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "A"},
                "geometry": mapping(LineString([(19.94, 50.06), (19.941, 50.06)])),
            },
            {
                "type": "Feature",
                "properties": {"name": "B"},
                "geometry": mapping(LineString([(19.941, 50.06), (19.941, 50.061)])),
            },
            {
                "type": "Feature",
                "properties": {"name": "C"},
                "geometry": mapping(LineString([(19.941, 50.061), (19.94, 50.061)])),
            },
            {
                "type": "Feature",
                "properties": {"name": "D"},
                "geometry": mapping(LineString([(19.94, 50.061), (19.94, 50.06)])),
            },
        ],
    }
    return roads_fc


def _make_flood_no_block():
    return {"type": "FeatureCollection", "features": []}


def _make_flood_middle():
    poly = Polygon(
        [
            (19.9405, 50.0602),
            (19.9405, 50.0608),
            (19.9409, 50.0608),
            (19.9409, 50.0602),
            (19.9405, 50.0602),
        ]
    )
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"hazard": "flood"},
                "geometry": mapping(poly),
            }
        ],
    }


def test_compute_route_basic_no_flood():
    roads = _make_simple_network()
    floods = _make_flood_no_block()
    hazard_index, _ = build_hazard_index(floods)
    G = build_road_graph(roads, hazard_index)

    feature, meta = compute_safe_route(G, 50.0600, 19.9400, 50.0610, 19.9410)

    assert feature["geometry"]["type"] == "LineString"
    assert meta["num_edges"] > 0
    assert meta["length_m"] > 0


def test_compute_route_with_flood_penalty():
    roads = _make_simple_network()
    floods = _make_flood_middle()
    hazard_index, _ = build_hazard_index(floods)
    G = build_road_graph(roads, hazard_index)

    feature, meta = compute_safe_route(G, 50.0600, 19.9400, 50.0610, 19.9410)

    assert meta["num_edges"] == 2
    assert meta["length_m"] > 0
