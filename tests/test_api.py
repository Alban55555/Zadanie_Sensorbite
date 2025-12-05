# tests/test_api.py
import sys
from pathlib import Path

# dodaj katalog projektu (tam gdzie jest folder app/) do sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api import router


# Tworzymy osobną aplikację do testów – nie importujemy main.py
test_app = FastAPI()
test_app.include_router(router)

client = TestClient(test_app)


def test_evac_route_ok():
    params = {
        "start_lat": 50.0600,
        "start_lon": 19.9400,
        "end_lat": 50.0610,
        "end_lon": 19.9410,
    }

    response = client.get("/api/evac/route", params=params)
    assert response.status_code == 200

    data = response.json()
    assert "route" in data
    assert "meta" in data

    route = data["route"]
    meta = data["meta"]

    assert route["type"] == "FeatureCollection"
    assert len(route["features"]) >= 1
    assert meta["length_m"] > 0
    assert meta["num_edges"] > 0


def test_evac_route_missing_params():
    response = client.get("/api/evac/route")
    assert response.status_code == 422
