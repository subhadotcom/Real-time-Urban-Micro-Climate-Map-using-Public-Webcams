import aiohttp
import asyncio
import logging
from typing import List, Dict
from cv_module import analyze_image

logger = logging.getLogger(__name__)

# Mock list of webcams for Phase 1
# In a real scenario, this might come from a database or config file
WEBCAMS = [
    {
        "id": "cam_01",
        "name": "City Center Plaza",
        "url": "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg", # Placeholder image
        "lat": 40.7128,
        "lng": -74.0060
    },
    {
        "id": "cam_02",
        "name": "Central Park West",
        "url": "https://images.pexels.com/photos/258447/pexels-photo-258447.jpeg", # Placeholder image
        "lat": 40.785091,
        "lng": -73.968285
    }
]

async def fetch_image(session: aiohttp.ClientSession, url: str) -> bytes:
    """Fetches an image from a URL."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                logger.error(f"Failed to fetch image from {url}: Status {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

async def ingest_all_webcams() -> List[Dict]:
    """Fetches images from all configured webcams and analyzes them."""
    results_data = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, cam["url"]) for cam in WEBCAMS]
        images = await asyncio.gather(*tasks)
        
        for i, img in enumerate(images):
            if img:
                logger.info(f"Successfully fetched image for {WEBCAMS[i]['name']}")
                analysis = analyze_image(img)
                if analysis:
                    data = WEBCAMS[i].copy()
                    data.update(analysis)
                    # Remove binary data if any (url is fine)
                    results_data.append(data)
                    logger.info(f"Analysis for {WEBCAMS[i]['name']}: {analysis}")
            else:
                logger.warning(f"Failed to fetch image for {WEBCAMS[i]['name']}")
    return results_data

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    asyncio.run(ingest_all_webcams())
