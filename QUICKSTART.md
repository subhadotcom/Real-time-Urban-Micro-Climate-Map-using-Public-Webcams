# Quick Start Guide

## Prerequisites

**Docker (Recommended - No Special Setup):**
- Docker and Docker Compose installed
- That's all you need!

**Local Development:**
- Python 3.9+ (3.11 recommended)
- Node.js 16+ (18+ recommended)
- OpenCV system libraries (Linux/Mac) - see REQUIREMENTS.md

## Quick Start with Docker (Recommended)

1. **Clone or navigate to the project directory**

2. **Start all services**:
```bash
docker-compose up --build
```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **View the map**: The frontend will automatically load and display webcam locations with real-time climate analysis.

## Local Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```


## Adding Real Webcams

1. Edit `backend/app/config.py`
2. Find webcam URLs that provide direct image access (not HTML pages)
3. Add to `WEBCAM_LOCATIONS` list:
```python
WEBCAM_LOCATIONS: List[WebcamLocation] = [
    WebcamLocation(
        id="webcam_1",
        name="Your Webcam Name",
        url="https://example.com/webcam/image.jpg",  # Direct image URL
        latitude=40.7128,
        longitude=-74.0060,
        enabled=True
    ),
]
```
4. Change `WEBCAMS = DEMO_WEBCAMS` to `WEBCAMS = WEBCAM_LOCATIONS`

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Check logs: `docker-compose logs backend`

### Frontend won't connect
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/config.py`
- Check browser console for errors

### No data on map
- Verify webcam URLs are accessible
- Check backend logs for fetch errors
- Ensure WebSocket connection is established (check status indicator)

### Docker issues
- Ensure Docker is running
- Try: `docker-compose down` then `docker-compose up --build`
- Check port conflicts (3000, 8000)

## Next Steps

1. **Add Real Webcams**: Replace demo webcams with real public webcam URLs
2. **Customize Analysis**: Adjust CV parameters in `backend/app/cv_analysis.py`
3. **Enhance UI**: Modify frontend components in `frontend/src/App.js`
4. **Deploy**: Follow deployment instructions in `SETUP.md`

## Support

For detailed documentation, see:
- `README.md` - Project overview
- `SETUP.md` - Detailed setup instructions
- `ARCHITECTURE.md` - System architecture

