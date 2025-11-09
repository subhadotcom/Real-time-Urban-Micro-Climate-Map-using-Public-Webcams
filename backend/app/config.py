"""Configuration settings for the application."""

import os
from typing import List
from app.models import WebcamLocation

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Image fetch configuration
FETCH_INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL_SECONDS", 60))  # Fetch every minute
IMAGE_TIMEOUT_SECONDS = int(os.getenv("IMAGE_TIMEOUT_SECONDS", 10))
IMAGE_CACHE_DIR = os.getenv("IMAGE_CACHE_DIR", "images_cache")

# Webcam locations
# You can add more webcams here. These are example public webcam URLs.
WEBCAM_LOCATIONS: List[WebcamLocation] = [
    WebcamLocation(
        id="webcam_1",
        name="Times Square, NYC",
        url="https://www.earthcam.com/cams/newyork/timessquare/?cam=tsrobo1",
        latitude=40.7580,
        longitude=-73.9855,
        enabled=True
    ),
    # Add more webcam URLs here
    # Note: Many public webcams require direct image URLs, not HTML pages
    # You may need to find direct image URLs like: "https://example.com/webcam/image.jpg"
]

# For demo purposes, we'll use placeholder coordinates with sample image analysis
# In production, replace with actual public webcam image URLs
DEMO_WEBCAMS: List[WebcamLocation] = [
    WebcamLocation(
        id="demo_1",
        name="Downtown Demo",
        url="https://via.placeholder.com/800x600/87CEEB/FFFFFF?text=Sunny+Street",
        latitude=40.7128,
        longitude=-74.0060,
        enabled=True
    ),
    WebcamLocation(
        id="demo_2",
        name="Park Area Demo",
        url="https://via.placeholder.com/800x600/2F4F4F/FFFFFF?text=Shadowy+Park",
        latitude=40.7829,
        longitude=-73.9654,
        enabled=True
    ),
    WebcamLocation(
        id="demo_3",
        name="Waterfront Demo",
        url="https://via.placeholder.com/800x600/4682B4/FFFFFF?text=Wet+Surface",
        latitude=40.6892,
        longitude=-74.0445,
        enabled=True
    ),
]

# Use demo webcams by default (replace with real webcam URLs)
WEBCAMS = DEMO_WEBCAMS

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

