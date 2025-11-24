import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def detect_wetness(img) -> float:
    """
    Heuristic to detect wetness based on reflections.
    Returns a probability between 0 and 1.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate standard deviation of pixel intensities
    # Wet surfaces often have high contrast (bright reflections vs dark wet asphalt)
    mean, std_dev = cv2.meanStdDev(gray)
    
    # Normalize std_dev to a 0-1 range (heuristic)
    # Assume std_dev > 80 is very high contrast (wet/sunny reflections)
    wetness_score = min(std_dev[0][0] / 80.0, 1.0)
    
    return round(wetness_score, 2)

def analyze_image(image_bytes: bytes) -> dict:
    """
    Analyzes an image to determine sun/shadow ratio and wetness.
    Returns a dictionary with analysis results.
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to separate sun (bright) and shadow (dark)
        # We use Otsu's binarization for automatic thresholding
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Count pixels
        total_pixels = thresh.size
        sun_pixels = cv2.countNonZero(thresh)
        shadow_pixels = total_pixels - sun_pixels
        
        sun_ratio = sun_pixels / total_pixels
        shadow_ratio = shadow_pixels / total_pixels
        
        wetness = detect_wetness(img)
        
        return {
            "sun_exposure": round(sun_ratio, 2),
            "shadow_exposure": round(shadow_ratio, 2),
            "wetness_probability": wetness,
            "status": "analyzed"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return None
