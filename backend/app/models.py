"""Data models for the micro-climate map application."""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class WebcamLocation(BaseModel):
    """Represents a webcam location with metadata."""
    id: str
    name: str
    url: str
    latitude: float
    longitude: float
    enabled: bool = True


class ClimateAnalysis(BaseModel):
    """Results from computer vision analysis of a webcam image."""
    model_config = ConfigDict()
    
    webcam_id: str
    timestamp: datetime
    sun_exposure: float  # 0.0 to 1.0 (percentage of image in sun)
    shadow_exposure: float  # 0.0 to 1.0 (percentage of image in shadow)
    wetness_score: float  # 0.0 to 1.0 (likelihood of wet surfaces)
    brightness: float  # Average brightness of the image
    image_url: Optional[str] = None


class WebSocketMessage(BaseModel):
    """Message format for WebSocket communication."""
    model_config = ConfigDict()
    
    type: str  # "update", "error", "status"
    data: dict
    timestamp: datetime

