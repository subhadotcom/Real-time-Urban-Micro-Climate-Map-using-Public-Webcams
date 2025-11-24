# Real-time Urban Micro-Climate Map

This project visualizes urban micro-climate conditions (sun exposure, shadow, wetness) using real-time analysis of public webcams.

## Architecture

- **Backend**: Python, FastAPI, OpenCV (for image analysis), WebSockets (for real-time updates).
- **Frontend**: React, Leaflet (for map visualization).

## Setup & Running

### Backend

1. Navigate to `backend` directory:
   ```bash
   cd backend
   ```
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

### Docker

You can also run the entire application using Docker Compose.

1. Ensure you have Docker and Docker Compose installed.
2. Run the following command in the root directory:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost:3000`. The API will be available at `http://localhost:8000`.

## Features

- **Real-time Data Ingestion**: Fetches images from configured public webcams.
- **Computer Vision Analysis**:
    - Sun/Shadow detection using thresholding.
    - Wetness detection using contrast/reflection heuristics.
- **Live Map**: Visualizes webcam locations and their current micro-climate status.
