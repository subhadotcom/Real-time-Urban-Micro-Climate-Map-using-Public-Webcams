"""WebSocket manager for real-time updates."""

import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from app.models import ClimateAnalysis, WebSocketMessage

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts updates."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.latest_data: Dict[str, ClimateAnalysis] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send latest data for all webcams to the new connection
        if self.latest_data:
            for analysis in self.latest_data.values():
                await self.send_personal_message(websocket, analysis)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, analysis: ClimateAnalysis):
        """Send a message to a specific WebSocket connection."""
        try:
            message = WebSocketMessage(
                type="update",
                data=analysis.model_dump(),
                timestamp=datetime.utcnow()
            )
            await websocket.send_json(message.model_dump(mode='json'))
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
    
    async def broadcast(self, analysis: ClimateAnalysis):
        """Broadcast an analysis update to all connected clients."""
        # Store latest data
        self.latest_data[analysis.webcam_id] = analysis
        
        # Create message
        message = WebSocketMessage(
            type="update",
            data=analysis.model_dump(),
            timestamp=datetime.utcnow()
        )
        
        # Broadcast to all connections
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message.model_dump(mode='json'))
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {str(e)}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_status(self, status: str, message: str):
        """Broadcast a status message to all connected clients."""
        ws_message = WebSocketMessage(
            type="status",
            data={"status": status, "message": message},
            timestamp=datetime.utcnow()
        )
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(ws_message.model_dump(mode='json'))
            except Exception as e:
                logger.error(f"Error broadcasting status: {str(e)}")
                disconnected.add(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_latest_data(self) -> Dict[str, ClimateAnalysis]:
        """Get the latest analysis data for all webcams."""
        return self.latest_data.copy()

