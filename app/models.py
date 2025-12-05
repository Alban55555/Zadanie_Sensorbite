# app/models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class RouteMetadata(BaseModel):
    length_m: float = Field(..., description="Długość trasy w metrach")
    num_edges: int = Field(..., description="Liczba krawędzi w trasie")
    avoided_edges: int = Field(..., description="Liczba krawędzi oznaczonych jako zagrożone")


class Feature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = {}


class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]


class RouteResponse(BaseModel):
    route: FeatureCollection
    meta: RouteMetadata
