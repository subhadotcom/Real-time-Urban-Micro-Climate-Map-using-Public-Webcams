# Setup Guide

## Quick Start with Docker

The easiest way to run the application is using Docker Compose:

```bash
docker-compose up --build
```

This will start:
- Backend API on port 8000
- Frontend on port 3000

Access the application at http://localhost:3000

## Local Development Setup

### Prerequisites

- Python 3.9+ (3.11 recommended)
- Node.js 16+ (18+ recommended)
- **OpenCV System Dependencies** (important for local development)

#### OpenCV System Dependencies

OpenCV requires system libraries that must be installed before installing Python packages:

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx
```

**macOS:**
```bash
brew install opencv
# Or system libraries are usually included
```

**Windows:**
- OpenCV usually works with pip install
- If issues occur, install Visual C++ Redistributables
- **Recommendation**: Use Docker for Windows (easier)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: If you get OpenCV import errors, install the system dependencies above first.

4. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## Adding Real Webcam URLs

1. Find public webcam URLs that provide direct image access (not HTML pages)
2. Edit `backend/app/config.py`
3. Add webcam locations to the `WEBCAM_LOCATIONS` list or modify `DEMO_WEBCAMS`
4. Set `WEBCAMS = WEBCAM_LOCATIONS` to use real webcams instead of demos

Example:
```python
WEBCAM_LOCATIONS: List[WebcamLocation] = [
    WebcamLocation(
        id="webcam_1",
        name="Times Square, NYC",
        url="https://example.com/webcam/image.jpg",  # Direct image URL
        latitude=40.7580,
        longitude=-73.9855,
        enabled=True
    ),
]
```

## Troubleshooting

### Backend Issues

- **Webcam fetch errors**: Check that webcam URLs are accessible and return image data (not HTML)
- **OpenCV errors**: Ensure system dependencies are installed (see Dockerfile for requirements)

### Frontend Issues

- **WebSocket connection errors**: Check that the backend is running and CORS is properly configured
- **Map not loading**: Ensure Leaflet CSS is loaded (check `public/index.html`)
- **No data displayed**: Check browser console for errors and verify WebSocket connection status

### Docker Issues

- **Port conflicts**: Change port mappings in `docker-compose.yml` if ports 3000 or 8000 are already in use
- **Build errors**: Ensure Docker and Docker Compose are up to date
- **Permission errors**: On Linux, you may need to run with `sudo` or add your user to the docker group

## Production Deployment

1. Set appropriate environment variables
2. Use a production WSGI server like Gunicorn for the backend
3. Build the frontend for production: `npm run build`
4. Use a reverse proxy (nginx) for serving the frontend and proxying API requests
5. Set up SSL/TLS certificates
6. Configure proper CORS origins
7. Set up monitoring and logging

## Performance Tuning

- Adjust `FETCH_INTERVAL_SECONDS` to balance update frequency and server load
- Use CDN for frontend assets in production
- Consider using a message queue (e.g., RabbitMQ) for high-volume scenarios
- Implement rate limiting for webcam requests
- For persistence, consider adding a database (PostgreSQL, MongoDB) for historical data storage

