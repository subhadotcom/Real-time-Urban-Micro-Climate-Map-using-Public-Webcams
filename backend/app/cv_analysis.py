"""Computer Vision analysis module for detecting micro-climate conditions."""

import cv2
import numpy as np
from typing import Dict, Optional
import io
from datetime import datetime
from app.models import ClimateAnalysis


def analyze_sun_shadow(image: np.ndarray) -> Dict[str, float]:
    """
    Analyze an image to detect sun and shadow regions.
    
    Args:
        image: OpenCV image (BGR format)
        
    Returns:
        Dictionary with sun_exposure and shadow_exposure percentages
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate average brightness
    brightness = np.mean(gray) / 255.0
    
    # Use adaptive thresholding to separate bright (sun) and dark (shadow) regions
    # Otsu's method automatically determines the threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Calculate percentages
    total_pixels = gray.size
    bright_pixels = np.sum(binary == 255)
    dark_pixels = np.sum(binary == 0)
    
    sun_exposure = bright_pixels / total_pixels
    shadow_exposure = dark_pixels / total_pixels
    
    # Alternative method: Use brightness thresholds
    # Consider pixels above 60% brightness as sun, below 40% as shadow
    bright_threshold = int(255 * 0.6)
    dark_threshold = int(255 * 0.4)
    
    sun_pixels = np.sum(gray > bright_threshold)
    shadow_pixels = np.sum(gray < dark_threshold)
    
    sun_exposure_refined = sun_pixels / total_pixels
    shadow_exposure_refined = shadow_pixels / total_pixels
    
    # Use the refined method but normalize
    total_classified = sun_exposure_refined + shadow_exposure_refined
    if total_classified > 0:
        sun_exposure_final = sun_exposure_refined / total_classified
        shadow_exposure_final = shadow_exposure_refined / total_classified
    else:
        sun_exposure_final = 0.5
        shadow_exposure_final = 0.5
    
    return {
        "sun_exposure": float(sun_exposure_final),
        "shadow_exposure": float(shadow_exposure_final),
        "brightness": float(brightness)
    }


def analyze_wetness(image: np.ndarray) -> float:
    """
    Detect wet surfaces by analyzing reflections and surface properties.
    
    Args:
        image: OpenCV image (BGR format)
        
    Returns:
        Wetness score from 0.0 to 1.0
    """
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Wet surfaces often have:
    # 1. High saturation (reflections show colors more vividly)
    # 2. Specific brightness patterns (specular highlights)
    # 3. Reduced texture (smooth reflective surfaces)
    
    # Calculate saturation
    saturation = hsv[:, :, 1]
    avg_saturation = np.mean(saturation) / 255.0
    
    # Calculate value (brightness) variance - wet surfaces have higher variance
    value = hsv[:, :, 2]
    value_variance = np.var(value) / (255.0 ** 2)
    
    # Detect specular highlights (very bright spots)
    bright_spots = np.sum(value > 200) / value.size
    
    # Calculate edge density (wet surfaces have fewer edges due to reflections)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    # Lower edge density suggests wet/smooth surface
    smoothness_score = 1.0 - min(edge_density * 10, 1.0)
    
    # Combine factors
    # Higher saturation + bright spots + smoothness = wet surface
    wetness_score = (
        avg_saturation * 0.3 +
        bright_spots * 0.4 +
        smoothness_score * 0.3
    )
    
    # Normalize to 0-1 range
    wetness_score = min(max(wetness_score, 0.0), 1.0)
    
    return float(wetness_score)


def analyze_image(image_data: bytes, webcam_id: str) -> ClimateAnalysis:
    """
    Perform complete climate analysis on an image.
    
    Args:
        image_data: Raw image bytes
        webcam_id: Identifier for the webcam
        
    Returns:
        ClimateAnalysis object with all detected conditions
    """
    # Decode image
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Failed to decode image")
    
    # Analyze sun/shadow
    sun_shadow = analyze_sun_shadow(image)
    
    # Analyze wetness
    wetness_score = analyze_wetness(image)
    
    # Create analysis result
    analysis = ClimateAnalysis(
        webcam_id=webcam_id,
        timestamp=datetime.utcnow(),
        sun_exposure=sun_shadow["sun_exposure"],
        shadow_exposure=sun_shadow["shadow_exposure"],
        wetness_score=wetness_score,
        brightness=sun_shadow["brightness"]
    )
    
    return analysis


def analyze_image_from_url(image_url: str, webcam_id: str, image_bytes: Optional[bytes] = None) -> ClimateAnalysis:
    """
    Analyze an image from a URL or provided bytes.
    
    Args:
        image_url: URL of the image
        webcam_id: Identifier for the webcam
        image_bytes: Optional pre-fetched image bytes
        
    Returns:
        ClimateAnalysis object
    """
    if image_bytes is None:
        import aiohttp
        import asyncio
        
        async def fetch():
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    return await response.read()
        
        image_bytes = asyncio.run(fetch())
    
    return analyze_image(image_bytes, webcam_id)

