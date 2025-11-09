"""Data ingestion module for fetching images from webcams."""

import aiohttp
import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime
from app.models import WebcamLocation, ClimateAnalysis
from app.config import IMAGE_TIMEOUT_SECONDS, FETCH_INTERVAL_SECONDS
from app.cv_analysis import analyze_image

logger = logging.getLogger(__name__)


class WebcamFetcher:
    """Handles fetching and processing images from webcams."""
    
    def __init__(self, webcams: List[WebcamLocation]):
        self.webcams = {webcam.id: webcam for webcam in webcams if webcam.enabled}
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_fetch_time: Dict[str, datetime] = {}
        self.last_analysis: Dict[str, ClimateAnalysis] = {}
        
    async def create_session(self):
        """Create aiohttp session with timeout configuration."""
        timeout = aiohttp.ClientTimeout(total=IMAGE_TIMEOUT_SECONDS)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def fetch_image(self, webcam: WebcamLocation) -> Optional[bytes]:
        """
        Fetch image from a webcam URL.
        
        Args:
            webcam: WebcamLocation object
            
        Returns:
            Image bytes or None if fetch failed
        """
        if not self.session:
            await self.create_session()
        
        try:
            logger.debug(f"Fetching image from {webcam.id} at {webcam.url}")
            async with self.session.get(webcam.url, allow_redirects=True) as response:
                logger.debug(f"Response status for {webcam.id}: {response.status}")
                
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    logger.debug(f"Content-Type for {webcam.id}: {content_type}")
                    
                    # Check if it's an image
                    if 'image' in content_type.lower():
                        image_data = await response.read()
                        logger.info(f"Successfully fetched image from {webcam.id} ({len(image_data)} bytes)")
                        return image_data
                    else:
                        # If it's HTML, try to find an image tag (simplified)
                        # For demo purposes, we'll return None and handle it differently
                        logger.warning(f"Webcam {webcam.id} returned non-image content: {content_type}. URL: {webcam.url}")
                        # Try to read the content to see what we got
                        content = await response.read()
                        logger.debug(f"Content preview (first 200 chars): {content[:200]}")
                        return None
                elif response.status == 404:
                    logger.error(f"Webcam {webcam.id} not found (404): {webcam.url}")
                    return None
                elif response.status == 403:
                    logger.error(f"Webcam {webcam.id} access forbidden (403): {webcam.url}")
                    return None
                else:
                    logger.error(f"Failed to fetch {webcam.id}: HTTP {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching image from {webcam.id} after {IMAGE_TIMEOUT_SECONDS}s: {webcam.url}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching image from {webcam.id}: {type(e).__name__}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching image from {webcam.id}: {type(e).__name__}: {str(e)}")
            return None
    
    def _is_demo_webcam(self, webcam: WebcamLocation) -> bool:
        """Check if this is a demo webcam that should generate synthetic data."""
        url_lower = webcam.url.lower()
        id_lower = webcam.id.lower()
        return (
            "placeholder" in url_lower or 
            "demo" in id_lower or
            "via.placeholder.com" in url_lower
        )
    
    async def process_webcam(self, webcam: WebcamLocation) -> Optional[ClimateAnalysis]:
        """
        Fetch and analyze a single webcam image.
        
        Args:
            webcam: WebcamLocation object
            
        Returns:
            ClimateAnalysis or None if processing failed
        """
        try:
            # Check if this is a demo webcam first
            is_demo = self._is_demo_webcam(webcam)
            
            if is_demo:
                logger.info(f"Processing demo webcam {webcam.id}, generating synthetic data")
                return self._generate_demo_analysis(webcam)
            
            # Fetch image for real webcams
            image_data = await self.fetch_image(webcam)
            
            if image_data is None:
                logger.warning(f"Could not fetch image from {webcam.id}, skipping analysis")
                return None
            
            # Analyze image
            try:
                analysis = analyze_image(image_data, webcam.id)
                self.last_analysis[webcam.id] = analysis
                self.last_fetch_time[webcam.id] = datetime.utcnow()
                
                logger.info(f"Processed {webcam.id}: sun={analysis.sun_exposure:.2f}, wetness={analysis.wetness_score:.2f}")
                return analysis
            except Exception as e:
                logger.error(f"Error analyzing image from {webcam.id}: {type(e).__name__}: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"Error processing webcam {webcam.id}: {type(e).__name__}: {str(e)}")
            return None
    
    def _generate_demo_analysis(self, webcam: WebcamLocation) -> ClimateAnalysis:
        """Generate synthetic analysis for demo webcams."""
        import random
        from app.models import ClimateAnalysis
        
        # Generate realistic demo data based on webcam ID or URL
        url_lower = webcam.url.lower()
        id_lower = webcam.id.lower()
        
        if "sunny" in url_lower or "demo_1" in id_lower or webcam.id == "demo_1":
            sun_exposure = 0.7 + random.uniform(-0.1, 0.1)
            wetness = 0.1 + random.uniform(-0.05, 0.05)
            logger.debug(f"Generated sunny demo data for {webcam.id}")
        elif "shadow" in url_lower or "demo_2" in id_lower or webcam.id == "demo_2":
            sun_exposure = 0.2 + random.uniform(-0.1, 0.1)
            wetness = 0.15 + random.uniform(-0.05, 0.05)
            logger.debug(f"Generated shadow demo data for {webcam.id}")
        elif "wet" in url_lower or "demo_3" in id_lower or webcam.id == "demo_3":
            sun_exposure = 0.5 + random.uniform(-0.1, 0.1)
            wetness = 0.8 + random.uniform(-0.1, 0.1)
            logger.debug(f"Generated wet demo data for {webcam.id}")
        else:
            # Default demo data
            sun_exposure = 0.5 + random.uniform(-0.2, 0.2)
            wetness = 0.3 + random.uniform(-0.2, 0.2)
            logger.debug(f"Generated default demo data for {webcam.id}")
        
        sun_exposure = max(0.0, min(1.0, sun_exposure))
        shadow_exposure = 1.0 - sun_exposure
        wetness = max(0.0, min(1.0, wetness))
        brightness = 0.4 + sun_exposure * 0.4 + random.uniform(-0.1, 0.1)
        brightness = max(0.0, min(1.0, brightness))
        
        analysis = ClimateAnalysis(
            webcam_id=webcam.id,
            timestamp=datetime.utcnow(),
            sun_exposure=sun_exposure,
            shadow_exposure=shadow_exposure,
            wetness_score=wetness,
            brightness=brightness
        )
        
        self.last_analysis[webcam.id] = analysis
        self.last_fetch_time[webcam.id] = datetime.utcnow()
        
        logger.info(f"Generated demo analysis for {webcam.id}: sun={sun_exposure:.2f}, wetness={wetness:.2f}")
        return analysis
    
    async def process_all_webcams(self) -> List[ClimateAnalysis]:
        """
        Fetch and analyze all enabled webcams in parallel.
        
        Returns:
            List of ClimateAnalysis objects
        """
        tasks = [
            self.process_webcam(webcam)
            for webcam in self.webcams.values()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        analyses = [
            result for result in results
            if isinstance(result, ClimateAnalysis)
        ]
        
        return analyses
    
    async def run_continuous(self, callback=None):
        """
        Continuously fetch and process webcam images.
        
        Args:
            callback: Optional async callback function to call with each analysis result
        """
        await self.create_session()
        
        try:
            while True:
                logger.info(f"Starting webcam fetch cycle at {datetime.utcnow()}")
                
                analyses = await self.process_all_webcams()
                
                # Call callback for each analysis
                if callback:
                    for analysis in analyses:
                        try:
                            await callback(analysis)
                        except Exception as e:
                            logger.error(f"Error in callback: {str(e)}")
                
                # Wait for next interval
                await asyncio.sleep(FETCH_INTERVAL_SECONDS)
                
        except asyncio.CancelledError:
            logger.info("Webcam fetcher stopped")
        finally:
            await self.close_session()

