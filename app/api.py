# app/api.py
import logging
from fastapi import APIRouter, HTTPException, Query, Depends

from .models import RouteResponse, RouteMetadata, FeatureCollection
from .routing import compute_safe_route
from .state import get_graph  # funkcja, która zwraca singleton grafu

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/evac/route", response_model=RouteResponse)
def evac_route(
    start_lat: float = Query(...),
    start_lon: float = Query(...),
    end_lat: float = Query(...),
    end_lon: float = Query(...),
    G=Depends(get_graph),
):
    try:
        feature, meta = compute_safe_route(G, start_lat, start_lon, end_lat, end_lon)
    except Exception as exc:
        logger.exception("Failed to compute route")
        raise HTTPException(status_code=400, detail=str(exc))

    fc = FeatureCollection(features=[feature])
    metadata = RouteMetadata(**meta)

    return RouteResponse(route=fc, meta=metadata)
