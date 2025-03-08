// /src/lib/services/websocketManager.js
import { browser } from '$app/environment';
import { writable } from 'svelte/store';
import { isAuthenticated } from '$lib/stores/authStore';
import { notificationStore } from '$lib/stores/notificationStore';
import { get } from 'svelte/store';

// Constants
const WS_BASE_URL = browser ? (import.meta.env.VITE_WS_BASE_URL || `ws://${window.location.host}/ws`) : '';
const WS_RECONNECT_DELAY = 1000; // Base delay in milliseconds
const WS_MAX_RECONNECT_ATTEMPTS = 5;
const WS_PING_INTERVAL = 30000; // 30 seconds for heartbeat

/**
 * WebSocket connection manager that handles reconnections, error handling, and authentication
 */
class WebSocketConnection {
  /**
   * Create a new WebSocket connection
   * @param {string} url - WebSocket URL
   * @param {Object} options - Configuration options
   */
  constructor(url, options = {}) {
    // Required properties
    this.url = url;
    this.type = options.type || 'generic';
    this.handlers = options.handlers || {};
    this.messageHandler = options.messageHandler;
    this.pingMessage = options.pingMessage || { type: 'ping' };
    
    // State
    this.socket = null;
    this.status = writable('disconnected');
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.pingTimer = null;
    this.isClosing = false;
    this.isReconnecting = false;
    this.lastMessageTime = Date.now();
    
    // Options with defaults
    this.maxReconnectAttempts = options.maxReconnectAttempts || WS_MAX_RECONNECT_ATTEMPTS;
    this.reconnectDelay = options.reconnectDelay || WS_RECONNECT_DELAY;
    this.pingInterval = options.pingInterval || WS_PING_INTERVAL;
    this.debug = options.debug || false;
    this.autoReconnect = options.autoReconnect !== false;
    this.authToken = options.authToken;
    
    // Auto-connect if specified
    if (options.autoConnect) {
      this.connect();
    }
  }
  
  /**
   * Connect to the WebSocket
   */
  connect() {
    if (!browser) {
      this.log('Cannot connect: Not in browser environment');
      return;
    }
    
    try {
      this.status.set('connecting');
      
      // Close existing connection if any
      if (this.socket) {
        this.socket.close();
      }
      
      // Get authentication token
      const accessToken = this.authToken || localStorage.getItem('accessToken') || '';
      
      // Construct URL with auth token
      let fullUrl = this.url;
      if (accessToken) {
        const separator = this.url.includes('?') ? '&' : '?';
        fullUrl = `${this.url}${separator}token=${encodeURIComponent(accessToken)}`;
      }
      
      // Create WebSocket connection
      this.socket = new WebSocket(fullUrl);
      
      // Set up event handlers
      this.socket.addEventListener('open', this.handleOpen.bind(this));
      this.socket.addEventListener('error', this.handleError.bind(this));
      this.socket.addEventListener('close', this.handleClose.bind(this));
      this.socket.addEventListener('message', this.handleMessage.bind(this));
      
      this.log(`Connecting to ${this.url}...`);
    } catch (error) {
      this.logError('Error creating WebSocket connection:', error);
      this.status.set('error');
      if (this.autoReconnect) {
        this.handleDisconnect();
      }
    }
  }
  
  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    this.log(`Connection opened for ${this.type}`);
    this.status.set('connected');
    this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
    this.isReconnecting = false;
    this.lastMessageTime = Date.now();
    
    // Setup ping interval to keep connection alive
    if (this.pingTimer) clearInterval(this.pingTimer);
    this.pingTimer = setInterval(() => {
      this.sendPing();
    }, this.pingInterval);
    
    // Call custom open handler if provided
    if (this.handlers.onOpen) {
      try {
        this.handlers.onOpen(event);
      } catch (error) {
        this.logError('Error in onOpen handler:', error);
      }
    }
  }
  
  /**
   * Handle WebSocket error event
   */
  handleError(event) {
    this.logError(`Error in ${this.type} connection:`, event);
    this.status.set('error');
    
    // Call custom error handler if provided
    if (this.handlers.onError) {
      try {
        this.handlers.onError(event);
      } catch (error) {
        this.logError('Error in onError handler:', error);
      }
    }
  }
  
  /**
   * Handle WebSocket close event
   */
  handleClose(event) {
    this.log(`Connection closed for ${this.type}:`, event.code, event.reason);
    this.status.set('disconnected');
    
    // Clear ping timer
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    
    // Call custom close handler if provided
    if (this.handlers.onClose) {
      try {
        this.handlers.onClose(event);
      } catch (error) {
        this.logError('Error in onClose handler:', error);
      }
    }
    
    // Handle disconnection with exponential backoff
    if (!this.isClosing && this.autoReconnect) {
      this.handleDisconnect();
    }
  }
  
  /**
   * Handle WebSocket message event
   */
  handleMessage(event) {
    try {
      // Update last message time for keep-alive monitoring
      this.lastMessageTime = Date.now();
      
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (parseError) {
        this.logError('Error parsing message:', parseError);
        data = event.data;
      }
      
      // Handle standard message types
      if (typeof data === 'object' && data !== null) {
        // Handle ping/pong
        if (data.type === 'pong') {
          this.log('Received pong response');
          return;
        }
        
        // Handle error messages
        if (data.type === 'error') {
          this.logError('Received error message:', data.error || data);
          if (data.error) {
            notificationStore.error(`WebSocket error: ${data.error}`);
          }
          return;
        }
      }
      
      // Call custom message handler if provided
      if (this.messageHandler) {
        try {
          this.messageHandler(data, event);
        } catch (error) {
          this.logError('Error in message handler:', error);
        }
      }
    } catch (error) {
      this.logError('Error processing message:', error);
    }
  }
  
  /**
   * Handle disconnection with exponential backoff
   */
  handleDisconnect() {
    if (!this.autoReconnect || !get(isAuthenticated)) {
      this.log('Auto-reconnect disabled or user not authenticated');
      return;
    }
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      this.isReconnecting = true;
      this.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      // Clear any existing reconnect timer
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
      }
      
      // Use exponential backoff with jitter for reconnection
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      const jitter = Math.random() * 1000; // Add up to 1 second of jitter
      this.reconnectTimer = setTimeout(() => {
        if (get(isAuthenticated)) {
          this.connect();
        } else {
          this.log('Not reconnecting: User not authenticated');
        }
      }, delay + jitter);
      
      // Update status to show reconnecting
      this.status.set('reconnecting');
    } else {
      this.log(`Max reconnection attempts (${this.maxReconnectAttempts}) reached. Giving up.`);
      this.status.set('failed');
      
      if (this.type !== 'notification') { // Don't show error for notification socket
        notificationStore.error(`Connection lost for ${this.type}. Please refresh the page.`);
      }
    }
  }
  
  /**
   * Send a ping message to keep the connection alive
   */
  sendPing() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      // Check if we haven't received any messages for a while
      const timeSinceLastMessage = Date.now() - this.lastMessageTime;
      if (timeSinceLastMessage > this.pingInterval * 2) {
        this.log('No response for a long time, reconnecting...');
        this.socket.close();
        this.handleDisconnect();
        return;
      }
      
      // Send ping
      try {
        this.socket.send(JSON.stringify(this.pingMessage));
        this.log('Sent ping');
      } catch (error) {
        this.logError('Error sending ping:', error);
        this.socket.close();
      }
    } else if (this.socket) {
      // Connection not open, clear ping timer
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
  
  /**
   * Send data through the WebSocket
   * @param {Object|string} data - Data to send
   * @returns {boolean} - True if sent successfully, false otherwise
   */
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        this.socket.send(message);
        return true;
      } catch (error) {
        this.logError('Error sending message:', error);
        return false;
      }
    } else {
      this.log('Cannot send message: WebSocket not connected');
      if (this.autoReconnect && !this.isReconnecting) {
        this.handleDisconnect();
      }
      return false;
    }
  }
  
  /**
   * Check if WebSocket is connected
   * @returns {boolean} - True if connected, false otherwise
   */
  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
  
  /**
   * Manually attempt to reconnect
   * @returns {boolean} - True if reconnection was initiated, false otherwise
   */
  reconnect() {
    if (!this.socket || (this.socket.readyState !== WebSocket.OPEN && this.socket.readyState !== WebSocket.CONNECTING)) {
      this.reconnectAttempts = 0; // Reset counter for manual reconnect
      this.connect();
      return true;
    }
    return false;
  }
  
  /**
   * Close the WebSocket connection
   */
  close() {
    this.isClosing = true;
    this.autoReconnect = false;
    
    // Clear timers
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    
    // Close socket
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    this.status.set('disconnected');
    this.isClosing = false;
    this.log('Connection closed');
  }
  
  /**
   * Log a message (if debug is enabled)
   */
  log(...args) {
    if (this.debug) {
      console.log(`[WebSocket:${this.type}]`, ...args);
    }
  }
  
  /**
   * Log an error
   */
  logError(...args) {
    console.error(`[WebSocket:${this.type}]`, ...args);
  }
}

/**
 * WebSocket Manager to manage all WebSocket connections
 */
class WebSocketManager {
  constructor() {
    this.connections = {};
    this.isAuthenticated = false;
    
    // Initialize authentication watcher
    if (browser) {
      this.unsubscribeAuth = isAuthenticated.subscribe(value => {
        this.isAuthenticated = value;
        this.handleAuthChange(value);
      });
    }
  }
  
  /**
   * Handle authentication state changes
   * @param {boolean} authenticated - Whether the user is authenticated
   */
  handleAuthChange(authenticated) {
    if (authenticated) {
      // Auto-reconnect connections when user authenticates
      Object.values(this.connections).forEach(conn => {
        if (conn.autoReconnect && !conn.isConnected()) {
          conn.reconnect();
        }
      });
    } else {
      // Close all connections when user logs out
      Object.values(this.connections).forEach(conn => {
        conn.close();
      });
    }
  }
  
  /**
   * Create a new WebSocket connection
   * @param {string} type - Connection type identifier
   * @param {string} url - WebSocket URL
   * @param {Object} options - Connection options
   * @returns {WebSocketConnection} - The created connection
   */
  createConnection(type, url, options = {}) {
    // If connection already exists, return it
    if (this.connections[type]) {
      return this.connections[type];
    }
    
    // Create new connection
    const connection = new WebSocketConnection(url, {
      ...options,
      type
    });
    
    // Store connection
    this.connections[type] = connection;
    
    return connection;
  }
  
  /**
   * Get an existing connection
   * @param {string} type - Connection type identifier
   * @returns {WebSocketConnection|null} - The connection or null if not found
   */
  getConnection(type) {
    return this.connections[type] || null;
  }
  
  /**
   * Close a specific connection
   * @param {string} type - Connection type identifier
   */
  closeConnection(type) {
    if (this.connections[type]) {
      this.connections[type].close();
      delete this.connections[type];
    }
  }
  
  /**
   * Close all connections
   */
  closeAll() {
    Object.values(this.connections).forEach(conn => {
      conn.close();
    });
    this.connections = {};
  }
  
  /**
   * Clean up resources when the manager is destroyed
   */
  destroy() {
    this.closeAll();
    
    if (this.unsubscribeAuth) {
      this.unsubscribeAuth();
    }
  }
}

// Create singleton instance
const websocketManager = browser ? new WebSocketManager() : null;

/**
 * Get the WebSocket manager instance
 * @returns {WebSocketManager|null} - The WebSocket manager or null if not in browser
 */
export function getWebSocketManager() {
  return websocketManager;
}

export default websocketManager;