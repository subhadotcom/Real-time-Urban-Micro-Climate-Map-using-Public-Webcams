# Real-time Urban Micro-Climate Map

A hyper-local "comfort map" of a city that analyzes public webcam feeds in real-time to infer environmental conditions like sun exposure and wetness.

## Features

- **Real-time Data Ingestion**: Continuously fetches images from public webcams using asyncio and aiohttp
- **Computer Vision Analysis**: 
  - Sun/shadow detection using adaptive thresholding and brightness analysis
  - Wetness detection using HSV color space analysis, edge detection, and specular highlight detection
  - Brightness analysis for overall illumination assessment
- **Live Dashboard**: 
  - Interactive map with Leaflet showing webcam locations
  - Real-time updates via WebSockets
  - Heatmap visualization for sun exposure patterns (toggleable)
  - Detailed popups with progress bars and metrics
  - Color-coded markers based on sun exposure and wetness
- **Micro-climate Insights**: Hyper-local environmental data not captured by official weather stations
- **Scalable Architecture**: Docker-based deployment with separate backend and frontend services
- **In-Memory Storage**: Latest analysis data stored in memory for fast access

## Architecture

- **Backend**: Python, FastAPI, WebSockets, OpenCV
- **Frontend**: React.js, Leaflet
- **DevOps**: Docker, Docker Compose

## Project Structure

```
.
├── backend/          # Python FastAPI backend
├── frontend/         # React frontend
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

**Option 1: Docker (Recommended - No Special Setup)**
- Docker and Docker Compose
- That's it! Docker handles all dependencies.

**Option 2: Local Development**
- Python 3.9+ (3.11 recommended)
- Node.js 16+ (18+ recommended)
- OpenCV system libraries (see REQUIREMENTS.md for details)

### Running with Docker

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration

### Adding Webcams

Edit `backend/app/config.py` to add webcam URLs and their coordinates. You can either:

1. **Use the `WEBCAM_LOCATIONS` list** for real webcam URLs (must be direct image URLs, not HTML pages)
2. **Use the `DEMO_WEBCAMS` list** for demonstration purposes (currently active by default)

**Important**: Many public webcams serve HTML pages, not direct images. You need to find the direct image URL. Look for URLs ending in `.jpg`, `.png`, or similar image formats, or check the webcam provider's API documentation.

Example of a direct image URL:
```
https://example.com/webcam/live/image.jpg
```

### Environment Variables

Create a `.env` file (optional):

```bash
# Backend Configuration
FETCH_INTERVAL_SECONDS=60
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration  
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_HOST=localhost
REACT_APP_WS_PORT=8000
```

### Adjusting Analysis Parameters

The computer vision analysis parameters can be adjusted in `backend/app/cv_analysis.py`:

- **Sun/Shadow Detection**: Brightness thresholds (default: 60% for sun, 40% for shadow)
- **Wetness Detection**: Saturation, edge density, and specular highlight weights

## License

MIT

