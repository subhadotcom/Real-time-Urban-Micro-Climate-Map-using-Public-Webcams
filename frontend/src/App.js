import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap, Circle } from 'react-leaflet';
import L from 'leaflet';
import './index.css';
import WebSocketService from './services/websocket';
import { getWebcams, getLatestAnalysis } from './services/api';

// Fix for default marker icon in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icon component for webcam markers
const createCustomIcon = (analysis) => {
  if (!analysis) {
    return L.divIcon({
      className: 'custom-marker',
      html: '<div style="background-color: #999; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>',
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });
  }

  // Color based on sun exposure and wetness
  const sunExposure = analysis.sun_exposure || 0.5;
  const wetness = analysis.wetness_score || 0;
  
  // Calculate color: yellow for sun, blue for wet, gray for shadow
  let r = Math.floor(255 * sunExposure);
  let g = Math.floor(200 * sunExposure);
  let b = Math.floor(100 + 155 * wetness);
  
  // Ensure values are within range
  r = Math.min(255, Math.max(0, r));
  g = Math.min(255, Math.max(0, g));
  b = Math.min(255, Math.max(0, b));

  const color = `rgb(${r}, ${g}, ${b})`;
  const size = 15 + Math.floor(sunExposure * 10); // Larger marker for more sun

  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: ${size}px; height: ${size}px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
};

// Component to handle map bounds
function MapBounds({ webcams }) {
  const map = useMap();
  
  useEffect(() => {
    if (webcams.length > 0) {
      const bounds = webcams.map(w => [w.latitude, w.longitude]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, webcams]);
  
  return null;
}

function App() {
  const [webcams, setWebcams] = useState([]);
  const [analyses, setAnalyses] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  // Fetch webcam locations on mount
  useEffect(() => {
    const fetchWebcams = async () => {
      try {
        const data = await getWebcams();
        setWebcams(data);
        
        // Also fetch latest analysis
        const latest = await getLatestAnalysis();
        if (latest.data) {
          const analysisMap = {};
          latest.data.forEach(analysis => {
            analysisMap[analysis.webcam_id] = analysis;
          });
          setAnalyses(analysisMap);
        }
      } catch (err) {
        setError(`Failed to fetch webcams: ${err.message}`);
        console.error(err);
      }
    };

    fetchWebcams();
  }, []);

  // Handle WebSocket updates
  const handleUpdate = useCallback((data) => {
    setAnalyses(prev => ({
      ...prev,
      [data.webcam_id]: data
    }));
  }, []);

  const handleStatusChange = useCallback((connected) => {
    setIsConnected(connected);
  }, []);

  // Set up WebSocket connection
  useEffect(() => {
    const wsService = new WebSocketService();
    
    wsService.onUpdate(handleUpdate);
    wsService.onStatusChange(handleStatusChange);
    wsService.connect();

    return () => {
      wsService.disconnect();
    };
  }, [handleUpdate, handleStatusChange]);

  const [showHeatmap, setShowHeatmap] = useState(true);

  // Default center (will be adjusted by MapBounds)
  const defaultCenter = webcams.length > 0 
    ? [webcams[0].latitude, webcams[0].longitude]
    : [40.7128, -74.0060]; // Default to NYC

  return (
    <div className="map-container">
      <MapContainer
        center={defaultCenter}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapBounds webcams={webcams} />
        
        {webcams.map(webcam => {
          const analysis = analyses[webcam.id];
          const icon = createCustomIcon(analysis);
          
          // Heatmap circles for sun exposure
          const sunExposure = analysis ? analysis.sun_exposure : 0.5;
          const radius = 200 + (sunExposure * 300); // Radius based on sun exposure
          const opacity = 0.2 + (sunExposure * 0.3);
          
          return (
            <React.Fragment key={webcam.id}>
              {showHeatmap && analysis && (
                <Circle
                  center={[webcam.latitude, webcam.longitude]}
                  radius={radius}
                  pathOptions={{
                    color: `rgb(${Math.floor(255 * sunExposure)}, ${Math.floor(200 * sunExposure)}, 0)`,
                    fillColor: `rgb(${Math.floor(255 * sunExposure)}, ${Math.floor(200 * sunExposure)}, 0)`,
                    fillOpacity: opacity,
                    weight: 1
                  }}
                />
              )}
              <Marker
                position={[webcam.latitude, webcam.longitude]}
                icon={icon}
              >
                <Popup>
                  <div className="tooltip-content">
                    <strong>{webcam.name}</strong>
                    {analysis ? (
                      <>
                        <div style={{ marginTop: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span>Sun Exposure:</span>
                            <span style={{ fontWeight: 'bold' }}>{(analysis.sun_exposure * 100).toFixed(1)}%</span>
                          </div>
                          <div style={{ 
                            width: '100%', 
                            height: '8px', 
                            backgroundColor: '#ddd', 
                            borderRadius: '4px',
                            overflow: 'hidden',
                            marginBottom: '8px'
                          }}>
                            <div style={{
                              width: `${analysis.sun_exposure * 100}%`,
                              height: '100%',
                              backgroundColor: `rgb(${Math.floor(255 * analysis.sun_exposure)}, ${Math.floor(200 * analysis.sun_exposure)}, 0)`,
                              transition: 'width 0.3s ease'
                            }}></div>
                          </div>
                        </div>
                        <div style={{ marginTop: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span>Shadow:</span>
                            <span>{(analysis.shadow_exposure * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                        <div style={{ marginTop: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span>Wetness:</span>
                            <span style={{ color: analysis.wetness_score > 0.5 ? '#2196F3' : '#666' }}>
                              {(analysis.wetness_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div style={{ 
                            width: '100%', 
                            height: '8px', 
                            backgroundColor: '#ddd', 
                            borderRadius: '4px',
                            overflow: 'hidden',
                            marginBottom: '8px'
                          }}>
                            <div style={{
                              width: `${analysis.wetness_score * 100}%`,
                              height: '100%',
                              backgroundColor: `rgba(33, 150, 243, ${0.5 + analysis.wetness_score * 0.5})`,
                              transition: 'width 0.3s ease'
                            }}></div>
                          </div>
                        </div>
                        <div style={{ marginTop: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Brightness:</span>
                            <span>{(analysis.brightness * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                        <div style={{ 
                          marginTop: '10px', 
                          paddingTop: '8px', 
                          borderTop: '1px solid #eee',
                          fontSize: '10px', 
                          color: '#666' 
                        }}>
                          Updated: {new Date(analysis.timestamp).toLocaleTimeString()}
                        </div>
                      </>
                    ) : (
                      <div style={{ color: '#999', fontStyle: 'italic' }}>No data available</div>
                    )}
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Status Bar */}
      <div className="status-bar">
        <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
        <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        {error && <span style={{ marginLeft: '10px', color: '#f44336' }}>{error}</span>}
      </div>

      {/* Legend */}
      <div className="legend">
        <h3>Legend</h3>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'rgb(255, 200, 100)' }}></div>
          <span>High Sun Exposure</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'rgb(150, 150, 150)' }}></div>
          <span>Shadow/Cloudy</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: 'rgb(100, 150, 255)' }}></div>
          <span>Wet Surface</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#999' }}></div>
          <span>No Data</span>
        </div>
        <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '14px' }}>
            <input
              type="checkbox"
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
              style={{ marginRight: '8px', cursor: 'pointer' }}
            />
            Show Heatmap
          </label>
        </div>
        <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
          Marker size indicates sun exposure level
        </div>
      </div>
    </div>
  );
}

export default App;

