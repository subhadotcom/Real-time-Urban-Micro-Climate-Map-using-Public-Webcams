# Architecture Overview

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Webcams   │────────▶│   Backend    │────────▶│  Frontend   │
│  (Public)   │  HTTP   │   (FastAPI)  │  WS/API │   (React)   │
└─────────────┘         └──────────────┘         └─────────────┘
```

## Components

### Backend (`backend/`)

1. **Data Ingestion** (`data_ingestion.py`)
   - Asynchronously fetches images from webcam URLs
   - Handles errors and timeouts
   - Processes multiple webcams in parallel
   - Generates demo data for testing

2. **Computer Vision Analysis** (`cv_analysis.py`)
   - **Sun/Shadow Detection**: Uses grayscale conversion, adaptive thresholding, and brightness analysis
   - **Wetness Detection**: Analyzes HSV color space, edge density, and specular highlights
   - **Brightness Analysis**: Calculates average image brightness

3. **WebSocket Manager** (`websocket_manager.py`)
   - Manages WebSocket connections
   - Broadcasts analysis updates to all connected clients
   - Stores latest analysis data

4. **FastAPI Application** (`main.py`)
   - REST API endpoints for webcam data and analysis
   - WebSocket endpoint for real-time updates
   - Background task for continuous image fetching
   - In-memory storage of latest analysis data

5. **Configuration** (`config.py`)
   - Webcam locations and URLs
   - Environment variables
   - API settings

### Frontend (`frontend/`)

1. **React Application** (`src/App.js`)
   - Main application component
   - Map visualization with Leaflet
   - Real-time updates via WebSocket
   - Heatmap visualization

2. **WebSocket Service** (`src/services/websocket.js`)
   - Manages WebSocket connection
   - Handles reconnection logic
   - Provides callback interface for updates

3. **API Service** (`src/services/api.js`)
   - HTTP API client
   - Fetches webcam locations and analysis data

## Data Flow

1. **Image Fetching**
   - Backend continuously fetches images from webcam URLs (every 60 seconds by default)
   - Images are processed asynchronously using asyncio

2. **Analysis**
   - Each image is analyzed using OpenCV
   - Results include: sun exposure, shadow exposure, wetness score, brightness

3. **Storage**
   - Latest analysis results are stored in memory
   - Data is maintained by WebSocket manager for fast access

4. **Real-time Updates**
   - Analysis results are broadcast via WebSocket to all connected clients
   - Frontend receives updates and updates the map visualization

5. **Visualization**
   - Map markers are color-coded based on sun exposure and wetness
   - Marker size indicates sun exposure level
   - Heatmap circles show sun exposure patterns
   - Popups display detailed metrics with progress bars

## Technology Stack

### Backend
- **Python 3.11**: Programming language
- **FastAPI**: Web framework and API
- **OpenCV**: Computer vision library
- **asyncio/aiohttp**: Asynchronous HTTP client
- **WebSockets**: Real-time communication

### Frontend
- **React 18**: UI framework
- **Leaflet**: Map visualization
- **WebSocket API**: Real-time updates

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy (production frontend)

## Performance Considerations

1. **Asynchronous Processing**: All I/O operations are asynchronous to handle multiple webcams efficiently
2. **In-Memory Storage**: Latest analysis results are kept in memory for fast access
3. **Parallel Processing**: Multiple webcams are processed in parallel
4. **Connection Pooling**: aiohttp session is reused for multiple requests
5. **WebSocket Efficiency**: Only sends updates when data changes

## Scalability

- **Horizontal Scaling**: Backend can be scaled horizontally with load balancer
- **CDN**: Frontend can be served via CDN
- **Message Queue**: For high-volume scenarios, consider adding RabbitMQ or similar
- **Database**: For persistence, consider adding a database (PostgreSQL, MongoDB) for historical data

## Security Considerations

- **CORS**: Configured to allow specific origins
- **Input Validation**: Pydantic models validate all inputs
- **Error Handling**: Comprehensive error handling prevents crashes
- **Rate Limiting**: Consider adding rate limiting for webcam requests (future enhancement)

## Monitoring and Logging

- **Logging**: Python logging module for backend
- **Health Checks**: `/health` endpoint for monitoring
- **Error Tracking**: Errors are logged with context

## Future Enhancements

1. **Machine Learning Models**: Replace rule-based CV with trained ML models
2. **Historical Data**: Store analysis history in a database
3. **Predictions**: Predict future conditions based on historical patterns
4. **User Submissions**: Allow users to submit webcam URLs
5. **Video Streams**: Support video stream analysis (currently images only)
6. **More Metrics**: Add temperature estimation, wind detection, etc.
7. **Mobile App**: Native mobile applications
8. **Notifications**: Alert users about conditions in specific areas

