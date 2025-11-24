import { useState, useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'
import L from 'leaflet';

// Fix for default marker icon in Leaflet with Webpack/Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Initial static data (will be replaced by live data)
const INITIAL_WEBCAMS = [
  {
    id: "cam_01",
    name: "City Center Plaza",
    lat: 40.7128,
    lng: -74.0060,
    url: "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg"
  },
  {
    id: "cam_02",
    name: "Central Park West",
    lat: 40.785091,
    lng: -73.968285,
    url: "https://images.pexels.com/photos/258447/pexels-photo-258447.jpeg"
  }
];

function App() {
  const [webcams, setWebcams] = useState(INITIAL_WEBCAMS);
  const [status, setStatus] = useState("Connecting...");
  const ws = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onopen = () => {
      setStatus("Connected");
      console.log("WebSocket Connected");
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "update") {
        console.log("Received update:", message.data);
        // Merge updates with existing data
        setWebcams(prevWebcams => {
          const updatedWebcams = [...prevWebcams];
          message.data.forEach(newData => {
            const index = updatedWebcams.findIndex(w => w.id === newData.id);
            if (index !== -1) {
              updatedWebcams[index] = { ...updatedWebcams[index], ...newData };
            } else {
              updatedWebcams.push(newData);
            }
          });
          return updatedWebcams;
        });
      }
    };

    ws.current.onclose = () => {
      setStatus("Disconnected");
      console.log("WebSocket Disconnected");
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Urban Micro-Climate Map</h1>
        <p>Real-time analysis of public webcams | Status: <span className={status === "Connected" ? "status-connected" : "status-disconnected"}>{status}</span></p>
      </header>
      <div className="map-container">
        <MapContainer center={[40.75, -73.98]} zoom={12} scrollWheelZoom={true} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {webcams.map(cam => (
            <Marker key={cam.id} position={[cam.lat, cam.lng]}>
              <Popup>
                <div className="popup-content">
                  <h3>{cam.name}</h3>
                  <img src={cam.url} alt={cam.name} style={{ width: '100%', borderRadius: '4px' }} />
                  <div className="stats">
                    {cam.sun_exposure !== undefined && (
                      <p><strong>Sun Exposure:</strong> {(cam.sun_exposure * 100).toFixed(0)}%</p>
                    )}
                    {cam.shadow_exposure !== undefined && (
                      <p><strong>Shadow:</strong> {(cam.shadow_exposure * 100).toFixed(0)}%</p>
                    )}
                    {cam.wetness_probability !== undefined && (
                      <p><strong>Wetness Prob:</strong> {(cam.wetness_probability * 100).toFixed(0)}%</p>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
        <Legend />
      </div>
    </div>
  )
}

function Legend() {
  return (
    <div className="legend">
      <h4>Legend</h4>
      <div className="legend-item">
        <span className="dot sun"></span> Sun
      </div>
      <div className="legend-item">
        <span className="dot shadow"></span> Shadow
      </div>
      <div className="legend-item">
        <span className="dot wet"></span> Wet
      </div>
    </div>
  );
}

export default App
