# Setup Requirements

## Quick Answer

**No special setup is needed if you use Docker** - just run `docker-compose up --build` and you're done!

For local development, you need Python, Node.js, and OpenCV system libraries.

## Option 1: Docker (Recommended - No Special Setup)

### Requirements
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose

### Setup
```bash
docker-compose up --build
```

**That's it!** Docker handles all dependencies including OpenCV system libraries.

## Option 2: Local Development

### Prerequisites

#### Essential
- **Python 3.9+** (3.11 recommended)
- **Node.js 16+** (18+ recommended)
- **pip** (Python package manager)
- **npm** (Node package manager)

#### OpenCV System Dependencies (Important!)

OpenCV requires system libraries that must be installed separately:

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1
```

**macOS:**
```bash
brew install opencv
# Or the system libraries are usually included
```

**Windows:**
- OpenCV is usually handled by the pip package `opencv-python`
- If you encounter issues, you may need to install Visual C++ Redistributables
- Alternatively, use Docker (recommended for Windows)

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run frontend:**
```bash
npm start
```

## Configuration

### No Configuration Required
The application works out of the box with default settings:
- Demo webcams are enabled by default
- Default ports: Backend 8000, Frontend 3000
- Default fetch interval: 60 seconds

### Optional Configuration

#### Environment Variables
Create a `.env` file (optional):
```bash
# Backend
FETCH_INTERVAL_SECONDS=60
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_HOST=localhost
REACT_APP_WS_PORT=8000
```

#### Webcam Configuration
Edit `backend/app/config.py` to add real webcam URLs (optional - demo webcams work by default).

## System Requirements

### Minimum
- **CPU**: 1 core
- **RAM**: 2GB
- **Disk**: 1GB free space
- **Network**: Internet connection (for fetching webcam images)

### Recommended
- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Disk**: 2GB+ free space
- **Network**: Stable internet connection

## Platform-Specific Notes

### Windows
- **Docker**: Use Docker Desktop (easiest)
- **Local**: Python and Node.js work well, but OpenCV may require Visual C++ Redistributables
- **Recommendation**: Use Docker for easiest setup

### macOS
- **Docker**: Use Docker Desktop
- **Local**: Works well with Homebrew-installed dependencies
- **OpenCV**: Usually works out of the box with pip install

### Linux
- **Docker**: Use Docker Engine + Docker Compose
- **Local**: Requires system libraries for OpenCV (see above)
- **OpenCV**: Install system dependencies before pip install

## Common Issues

### OpenCV Import Error
**Error**: `ImportError: libGL.so.1: cannot open shared object file`

**Solution (Linux):**
```bash
sudo apt-get install -y libgl1-mesa-glx
```

### Port Already in Use
**Error**: Port 8000 or 3000 already in use

**Solution**: Change ports in `docker-compose.yml` or stop other services using those ports

### Python Version
**Error**: Python version too old

**Solution**: Use Python 3.9+ (3.11 recommended). Check with `python --version`

### Node Version
**Error**: Node.js version too old

**Solution**: Use Node.js 16+ (18+ recommended). Check with `node --version`

## Verification

After setup, verify everything works:

1. **Backend health check:**
```bash
curl http://localhost:8000/health
```

2. **Frontend loads:**
Open http://localhost:3000 in browser

3. **API documentation:**
Open http://localhost:8000/docs in browser

## Summary

### Easiest Setup (Recommended)
1. Install Docker Desktop
2. Run `docker-compose up --build`
3. Open http://localhost:3000

### Local Development Setup
1. Install Python 3.9+ and Node.js 16+
2. Install OpenCV system dependencies (Linux/Mac)
3. Install Python dependencies: `pip install -r requirements.txt`
4. Install Node dependencies: `npm install`
5. Run backend and frontend separately

**No special configuration or setup files needed** - the application works with defaults!

