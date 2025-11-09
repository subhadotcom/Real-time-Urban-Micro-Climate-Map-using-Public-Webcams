/**
 * WebSocket service for real-time updates
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectInterval = 5000; // 5 seconds
    this.reconnectTimer = null;
    this.updateCallbacks = [];
    this.statusCallbacks = [];
    this.isConnected = false;
    
    // Determine WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.REACT_APP_WS_HOST || window.location.hostname;
    const port = process.env.REACT_APP_WS_PORT || '8000';
    this.wsUrl = `${protocol}//${host}:${port}/ws`;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.notifyStatusChange(true);
        this.clearReconnectTimer();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'update' && message.data) {
            this.notifyUpdate(message.data);
          } else if (message.type === 'status') {
            console.log('Status update:', message.data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnected = false;
        this.notifyStatusChange(false);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.notifyStatusChange(false);
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('Error connecting WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  disconnect() {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.notifyStatusChange(false);
  }

  scheduleReconnect() {
    this.clearReconnectTimer();
    this.reconnectTimer = setTimeout(() => {
      console.log('Attempting to reconnect WebSocket...');
      this.connect();
    }, this.reconnectInterval);
  }

  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  onUpdate(callback) {
    this.updateCallbacks.push(callback);
  }

  onStatusChange(callback) {
    this.statusCallbacks.push(callback);
  }

  notifyUpdate(data) {
    this.updateCallbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('Error in update callback:', error);
      }
    });
  }

  notifyStatusChange(connected) {
    this.statusCallbacks.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('Error in status callback:', error);
      }
    });
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }
}

export default WebSocketService;

