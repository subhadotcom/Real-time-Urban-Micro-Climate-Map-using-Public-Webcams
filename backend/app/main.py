"""Main FastAPI application."""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

from app.config import (
    WEBCAMS, CORS_ORIGINS, FETCH_INTERVAL_SECONDS
)
from app.models import WebcamLocation, ClimateAnalysis
from app.data_ingestion import WebcamFetcher
from app.websocket_manager import WebSocketManager
from app.cv_analysis import analyze_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global objects
websocket_manager = WebSocketManager()
webcam_fetcher: WebcamFetcher = None
fetcher_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global webcam_fetcher, fetcher_task
    
    # Startup
    logger.info("Starting application...")
    
    # Initialize webcam fetcher
    webcam_fetcher = WebcamFetcher(WEBCAMS)
    logger.info(f"Initialized webcam fetcher with {len(webcam_fetcher.webcams)} webcams")
    
    # Start background task for continuous fetching
    async def fetch_and_broadcast():
        async def callback(analysis: ClimateAnalysis):
            # Broadcast via WebSocket
            await websocket_manager.broadcast(analysis)
            logger.debug(f"Broadcasted analysis for {analysis.webcam_id} to {len(websocket_manager.active_connections)} clients")
        
        # Process webcams immediately on startup
        logger.info("Processing webcams immediately on startup...")
        try:
            initial_analyses = await webcam_fetcher.process_all_webcams()
            logger.info(f"Initial processing complete: {len(initial_analyses)} webcams processed")
            for analysis in initial_analyses:
                await callback(analysis)
        except Exception as e:
            logger.error(f"Error in initial webcam processing: {str(e)}")
        
        # Continue with periodic fetching
        await webcam_fetcher.run_continuous(callback)
    
    fetcher_task = asyncio.create_task(fetch_and_broadcast())
    logger.info("Webcam fetcher task started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if fetcher_task:
        fetcher_task.cancel()
        try:
            await fetcher_task
        except asyncio.CancelledError:
            pass
    
    if webcam_fetcher:
        await webcam_fetcher.close_session()
    
    logger.info("Application shut down")


# Create FastAPI app
app = FastAPI(
    title="Urban Micro-Climate Map API",
    description="Real-time micro-climate analysis from public webcams",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Urban Micro-Climate Map API",
        "version": "1.0.0",
        "endpoints": {
            "webcams": "/api/webcams",
            "latest": "/api/latest",
            "websocket": "/ws"
        }
    }


@app.get("/api/webcams", response_model=List[WebcamLocation])
async def get_webcams():
    """Get list of all webcam locations."""
    return WEBCAMS


@app.get("/api/webcams/{webcam_id}/test")
async def test_webcam(webcam_id: str):
    """Test connection to a specific webcam."""
    webcam = None
    for w in WEBCAMS:
        if w.id == webcam_id:
            webcam = w
            break
    
    if not webcam:
        raise HTTPException(status_code=404, detail=f"Webcam {webcam_id} not found")
    
    if not webcam_fetcher:
        raise HTTPException(status_code=503, detail="Webcam fetcher not initialized")
    
    # Test the connection
    try:
        image_data = await webcam_fetcher.fetch_image(webcam)
        if image_data:
            return {
                "webcam_id": webcam_id,
                "status": "success",
                "image_size": len(image_data),
                "url": webcam.url,
                "message": "Image fetched successfully"
            }
        else:
            # Check if it's a demo webcam by checking URL patterns
            url_lower = webcam.url.lower()
            id_lower = webcam.id.lower()
            is_demo = ("placeholder" in url_lower or "demo" in id_lower or 
                      "via.placeholder.com" in url_lower)
            
            if is_demo:
                return {
                    "webcam_id": webcam_id,
                    "status": "demo",
                    "url": webcam.url,
                    "message": "This is a demo webcam - will generate synthetic data"
                }
            return {
                "webcam_id": webcam_id,
                "status": "failed",
                "url": webcam.url,
                "message": "Could not fetch image from URL"
            }
    except Exception as e:
        return {
            "webcam_id": webcam_id,
            "status": "error",
            "url": webcam.url,
            "error": str(e),
            "error_type": type(e).__name__
        }


@app.get("/api/latest")
async def get_latest_analysis():
    """Get latest analysis for all webcams."""
    latest_data = websocket_manager.get_latest_data()
    
    return {
        "data": [analysis.model_dump() for analysis in latest_data.values()],
        "count": len(latest_data)
    }


@app.get("/api/latest/{webcam_id}")
async def get_webcam_analysis(webcam_id: str):
    """Get latest analysis for a specific webcam."""
    latest_data = websocket_manager.get_latest_data()
    
    if webcam_id in latest_data:
        return latest_data[webcam_id].model_dump()
    
    raise HTTPException(status_code=404, detail="Webcam analysis not found")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            logger.debug(f"Received message: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_websocket_connections": len(websocket_manager.active_connections),
        "webcams_configured": len(WEBCAMS)
    }

