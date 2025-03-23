// src/lib/services/websocket.js
import { browser } from '$app/environment';
import { writable, get } from 'svelte/store';
import { goto } from '$app/navigation';
import { toast } from '$lib/stores/toast';

/**
 * Enhanced WebSocket service for real-time communication with the backend.
 * Provides robust connection management, error handling, and reconnection logic.
 */

// Configuration
const WS_BASE_URL = browser ? 
  (import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`) : 
  null;

// Connection management constants
const RECONNECT_INTERVAL = 3000; // 3 seconds initial reconnect time
const MAX_RECONNECT_INTERVAL = 30000; // Maximum 30 seconds between reconnect attempts
const MAX_RECONNECT_ATTEMPTS = 10;
const PING_INTERVAL = 30000; // 30 seconds ping interval to keep connection alive

// Stores for active connections and their status
export const connections = writable({});
export const connectionStatus = writable({});

/**
 * Base WebSocket connection manager with enhanced error handling
 */
class WebSocketConnection {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      autoConnect: true,
      autoReconnect: true,
      pingInterval: PING_INTERVAL,
      debug: false,
      getToken: () => localStorage.getItem('accessToken'),
      onOpen: null,
      onClose: null,
      onError: null,
      onMessage: null,
      onReconnect: null,
      redirectOnAuthFailure: true,
      ...options
    };
    
    // Connection state
    this.socket = null;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.pingTimer = null;
    this.reconnectInterval = RECONNECT_INTERVAL;
    
    // Message handlers and event registry
    this.messageHandlers = new Map();
    this.eventHandlers = {
      onOpen: [],
      onClose: [],
      onError: [],
      onMessage: [],
      onReconnect: [],
      onReconnectFailed: []
    };
    
    // Pending messages queue for reconnection
    this.pendingMessages = [];
    
    // Register initial handlers from options
    if (this.options.onOpen) this.on('open', this.options.onOpen);
    if (this.options.onClose) this.on('close', this.options.onClose);
    if (this.options.onError) this.on('error', this.options.onError);
    if (this.options.onMessage) this.on('message', this.options.onMessage);
    if (this.options.onReconnect) this.on('reconnect', this.options.onReconnect);
    
    // Auto-connect if enabled
    if (this.options.autoConnect) {
      this.connect();
    }
  }
  
  /**
   * Connect to WebSocket with enhanced error handling
   */
  connect() {
    if (!browser) return Promise.reject(new Error('WebSocket is only available in browser environment'));
    
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return Promise.resolve(this.socket);
    }
    
    return new Promise((resolve, reject) => {
      this.isConnecting = true;
      this.updateStatus('connecting');
      
      const onOpenHandler = (event) => {
        this.socket.removeEventListener('open', onOpenHandler);
        resolve(this.socket);
      };
      
      const onErrorHandler = (event) => {
        this.socket.removeEventListener('error', onErrorHandler);
        reject(new Error('Connection failed'));
      };
      
      try {
        // Get authentication token
        const token = this.options.getToken();
        
        // Build URL with authentication token
        const wsUrl = new URL(this.url, WS_BASE_URL);
        
        // Add token as query parameter if provided
        if (token) {
          wsUrl.searchParams.append('token', token);
        }
        
        // Create WebSocket with proper error handling
        this.socket = new WebSocket(wsUrl.toString());
        this.socket.addEventListener('open', onOpenHandler);
        this.socket.addEventListener('error', onErrorHandler);
        
        // Setup core event handlers
        this.socket.onopen = (event) => this.handleOpen(event);
        this.socket.onclose = (event) => this.handleClose(event);
        this.socket.onerror = (event) => this.handleError(event);
        this.socket.onmessage = (event) => this.handleMessage(event);
        
        if (this.options.debug) {
          console.log(`Connecting to WebSocket: ${wsUrl.toString()}`);
        }
      } catch (error) {
        this.isConnecting = false;
        console.error(`WebSocket connection error for ${this.url}:`, error);
        this.updateStatus('error', error.message);
        this.scheduleReconnect();
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket with proper cleanup
   */
  disconnect() {
    this.clearTimers();
    
    if (this.socket) {
      // Prevent reconnection on intentional disconnect
      this.options.autoReconnect = false;
      
      if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
        this.socket.close(1000, 'User disconnected');
      }
      this.socket = null;
    }
    
    this.updateStatus('disconnected');
    
    // Clear pending messages
    this.pendingMessages = [];
    
    return Promise.resolve();
  }
  
  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.reconnectInterval = RECONNECT_INTERVAL; // Reset reconnect interval
    this.updateStatus('connected');
    
    if (this.options.debug) {
      console.log(`WebSocket connected: ${this.url}`);
    }
    
    // Setup ping interval to keep connection alive
    this.setupPing();
    
    // Process any pending messages
    this.processPendingMessages();
    
    // Call event handlers
    this.eventHandlers.onOpen.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('Error in onOpen handler:', error);
      }
    });
  }
  
  /**
   * Handle WebSocket close event with improved reconnection logic
   */
  handleClose(event) {
    this.clearTimers();
    
    const wasIntentional = event.code === 1000;
    
    // Determine close reason for better UX feedback
    let closeReason = 'Connection closed';
    if (event.reason) {
      closeReason = event.reason;
    } else if (event.code === 1006) {
      closeReason = 'Connection lost unexpectedly';
    } else if (event.code === 1001) {
      closeReason = 'Server is going away';
    } else if (event.code === 1011) {
      closeReason = 'Server error';
    } else if (event.code === 4003) {
      closeReason = 'Authentication failed';
    }
    
    if (this.options.debug) {
      console.log(`WebSocket closed: ${this.url}, Code: ${event.code}, Reason: ${closeReason}`);
    }
    
    // Update status based on close code
    if (wasIntentional) {
      // Normal closure
      this.updateStatus('disconnected', 'Connection closed normally');
    } else if (event.code === 4003) {
      // Authentication failure
      this.updateStatus('auth_failed', 'Authentication failed');
      
      // Redirect to login if configured
      if (this.options.redirectOnAuthFailure) {
        if (browser && typeof toast !== 'undefined') {
          toast.error('Your session has expired. Please log in again.');
        }
        goto('/auth/login');
      }
    } else {
      // Abnormal closure, attempt reconnect
      this.updateStatus('disconnected', closeReason);
      if (this.options.autoReconnect) {
        this.scheduleReconnect();
      }
    }
    
    // Call event handlers
    this.eventHandlers.onClose.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('Error in onClose handler:', error);
      }
    });
  }
  
  /**
   * Handle WebSocket error event
   */
  handleError(event) {
    console.error(`WebSocket error for ${this.url}:`, event);
    this.updateStatus('error', 'Connection error');
    
    // Call event handlers
    this.eventHandlers.onError.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('Error in onError handler:', error);
      }
    });
  }
  
  /**
   * Handle WebSocket message event with improved parsing
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      
      // Handle ping/pong for keepalive
      if (data.type === 'pong') {
        if (this.options.debug) {
          console.log(`Received pong from server: ${this.url}`);
        }
        return;
      }
      
      // Handle error messages
      if (data.type === 'error') {
        console.error(`WebSocket error from server (${this.url}):`, data);
        
        // Show toast notification if available
        if (browser && typeof toast !== 'undefined') {
          toast.error(data.message || 'An error occurred');
        }
        
        // Update status
        this.updateStatus('error', data.message || 'Server error');
        
        // Check if client_id is provided and call specific handler
        if (data.client_id && this.messageHandlers.has(`error:${data.client_id}`)) {
          this.messageHandlers.get(`error:${data.client_id}`)(data);
          return;
        }
      }
      
      // Call specific message type handlers
      if (data.type && this.messageHandlers.has(data.type)) {
        try {
          this.messageHandlers.get(data.type)(data);
        } catch (error) {
          console.error(`Error in message handler for type '${data.type}':`, error);
        }
      }
      
      // Call message event handlers
      this.eventHandlers.onMessage.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in onMessage handler:', error);
        }
      });
    } catch (error) {
      console.error(`Error parsing WebSocket message:`, error, event.data);
    }
  }
  
  /**
   * Send message to WebSocket with improved queue handling
   */
  send(data) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      if (this.options.debug) {
        console.warn(`Cannot send message, WebSocket is not connected. ${this.options.autoReconnect ? 'Queuing message.' : ''}`);
      }
      
      // Queue message if auto reconnect is enabled
      if (this.options.autoReconnect) {
        return new Promise((resolve, reject) => {
          // Store the message for later sending
          this.pendingMessages.push({
            data,
            resolve,
            reject,
            timestamp: Date.now()
          });
          
          // Try to reconnect
          this.connect().catch(error => {
            // Don't reject here, we'll try to send later
            if (this.options.debug) {
              console.warn(`Reconnect attempt failed, message queued: ${error.message}`);
            }
          });
        });
      }
      
      return Promise.reject(new Error('WebSocket is not connected'));
    }
    
    try {
      // Convert data to JSON string if needed
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      
      if (this.options.debug && data.type !== 'ping') {
        console.log(`Sent WebSocket message: ${this.url}`, data);
      }
      
      return Promise.resolve();
    } catch (error) {
      console.error(`Error sending WebSocket message:`, error);
      return Promise.reject(error);
    }
  }
  
  /**
   * Process any pending messages after reconnection
   */
  processPendingMessages() {
    if (this.pendingMessages.length === 0) return;
    
    const now = Date.now();
    const maxAge = 60000; // Don't send messages older than 1 minute
    
    // Process each pending message
    [...this.pendingMessages].forEach((item, index) => {
      // Skip old messages
      if (now - item.timestamp > maxAge) {
        item.reject(new Error('Message expired'));
        this.pendingMessages.splice(index, 1);
        return;
      }
      
      // Try to send the message
      this.send(item.data)
        .then(() => {
          item.resolve();
          this.pendingMessages.splice(index, 1);
        })
        .catch(error => {
          // Keep the message in the queue for next reconnect
          if (this.options.debug) {
            console.warn(`Failed to send queued message: ${error.message}`);
          }
        });
    });
  }
  
  /**
   * Subscribe to a specific message type
   */
  onMessage(type, callback) {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    
    this.messageHandlers.set(type, callback);
    
    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(type);
    };
  }
  
  /**
   * Subscribe to events (open, close, error, message, reconnect)
   */
  on(event, callback) {
    const eventType = `on${event.charAt(0).toUpperCase()}${event.slice(1)}`;
    
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType].push(callback);
      
      // Return unsubscribe function
      return () => {
        this.off(event, callback);
      };
    }
    
    throw new Error(`Unknown event type: ${event}`);
  }
  
  /**
   * Unsubscribe from events
   */
  off(event, callback) {
    const eventType = `on${event.charAt(0).toUpperCase()}${event.slice(1)}`;
    
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = this.eventHandlers[eventType].filter(cb => cb !== callback);
    }
  }
  
  /**
   * Update connection status
   */
  updateStatus(status, message = null) {
    connectionStatus.update(current => ({
      ...current,
      [this.url]: { 
        status, 
        message, 
        timestamp: new Date().toISOString(),
        reconnectAttempts: this.reconnectAttempts
      }
    }));
    
    // Log status change if debugging
    if (this.options.debug) {
      console.log(`WebSocket status changed: ${this.url} - ${status}${message ? ` (${message})` : ''}`);
    }
  }
  
  /**
   * Schedule reconnection with exponential backoff
   */
  scheduleReconnect() {
    if (!this.options.autoReconnect || this.reconnectTimer) {
      return;
    }
    
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts > MAX_RECONNECT_ATTEMPTS) {
      this.updateStatus('reconnect_failed', `Failed after ${MAX_RECONNECT_ATTEMPTS} attempts`);
      
      // Call reconnect failed handlers
      this.eventHandlers.onReconnectFailed.forEach(handler => {
        try {
          handler();
        } catch (error) {
          console.error('Error in onReconnectFailed handler:', error);
        }
      });
      return;
    }
    
    // Exponential backoff with jitter
    const jitter = Math.random() * 0.3 + 0.85; // Random factor between 0.85 and 1.15
    this.reconnectInterval = Math.min(
      this.reconnectInterval * 1.5 * jitter,
      MAX_RECONNECT_INTERVAL
    );
    
    const delay = this.reconnectInterval;
    
    this.updateStatus('reconnecting', `Attempt ${this.reconnectAttempts} of ${MAX_RECONNECT_ATTEMPTS}`);
    
    if (this.options.debug) {
      console.log(`Scheduling reconnect in ${Math.round(delay)}ms, attempt ${this.reconnectAttempts} of ${MAX_RECONNECT_ATTEMPTS}`);
    }
    
    // Schedule reconnect
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      
      // Call reconnect handlers
      this.eventHandlers.onReconnect.forEach(handler => {
        try {
          handler(this.reconnectAttempts);
        } catch (error) {
          console.error('Error in onReconnect handler:', error);
        }
      });
      
      // Attempt reconnection
      this.connect().catch(error => {
        if (this.options.debug) {
          console.warn(`Reconnect attempt ${this.reconnectAttempts} failed: ${error.message}`);
        }
        // scheduleReconnect will be called by handleClose
      });
    }, delay);
  }
  
  /**
   * Setup ping interval to keep connection alive
   */
  setupPing() {
    this.clearTimers();
    
    // Skip if ping is disabled
    if (!this.options.pingInterval) return;
    
    this.pingTimer = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' }).catch(error => {
          if (this.options.debug) {
            console.warn('Failed to send ping:', error);
          }
        });
      }
    }, this.options.pingInterval);
    
    if (this.options.debug) {
      console.log(`Ping timer set up: ${this.options.pingInterval}ms`);
    }
  }
  
  /**
   * Clear all timers
   */
  clearTimers() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
  
  /**
   * Get current connection status
   */
  getStatus() {
    const currentStatus = get(connectionStatus)[this.url];
    return currentStatus || { status: 'unknown' };
  }
  
  /**
   * Check if connection is open
   */
  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

/**
 * Create a WebSocket connection
 * @param {string} path - WebSocket path (without base URL)
 * @param {Object} options - Connection options
 * @returns {WebSocketConnection} WebSocket connection instance
 */
export function createWebSocket(path, options = {}) {
  if (!browser) return null;
  
  // Check if connection already exists
  const connectionsStore = get(connections);
  if (connectionsStore[path]) {
    return connectionsStore[path];
  }
  
  // Create new connection
  const connection = new WebSocketConnection(path, options);
  
  // Store connection
  connections.update(current => ({
    ...current,
    [path]: connection
  }));
  
  return connection;
}

/**
 * Auction WebSocket service
 */
export class AuctionService {
  constructor(auctionId, options = {}) {
    this.auctionId = auctionId;
    this.path = `ws/auctions/${auctionId}/updates/`;
    this.options = {
      debug: false,
      ...options
    };
    
    this.socket = createWebSocket(this.path, {
      autoReconnect: true,
      ...options
    });
    
    // Initialize callback registry
    this._callbacks = new Set();
  }
  
  /**
   * Subscribe to auction updates
   * @param {Function} callback - Handler for all auction-related events
   * @returns {Function} Unsubscribe function
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
    // Keep track of the callback for reconnection handling
    this._callbacks.add(callback);
    
    // Subscribe to all auction-related messages
    const handlers = [
      this.socket.onMessage('initial_state', callback),
      this.socket.onMessage('auction_state', callback),
      this.socket.onMessage('status_update', callback),
      this.socket.onMessage('price_update', callback),
      this.socket.onMessage('time_update', callback),
      this.socket.onMessage('extension_update', callback),
      this.socket.onMessage('auction_update', callback),
      this.socket.onMessage('watch_status', callback)
    ];
    
    // Return unsubscribe function
    return () => {
      handlers.forEach(unsubscribe => unsubscribe && unsubscribe());
      this._callbacks.delete(callback);
    };
  }
  
  /**
   * Subscribe to specific update type
   * @param {string} updateType - Update type to subscribe to
   * @param {Function} callback - Event handler
   * @returns {Function} Unsubscribe function
   */
  on(updateType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(updateType, callback);
  }
  
  /**
   * Get current auction state
   * @returns {Promise} Promise resolving when request is sent
   */
  getState() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_state'
    });
  }
  
  /**
   * Watch auction (add to user's watched auctions)
   * @returns {Promise} Promise resolving when request is sent
   */
  watch() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'watch_auction'
    });
  }
  
  /**
   * Unwatch auction (remove from user's watched auctions)
   * @returns {Promise} Promise resolving when request is sent
   */
  unwatch() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'unwatch_auction'
    });
  }
  
  /**
   * Check if user is watching this auction
   * @returns {Promise} Promise resolving when request is sent
   */
  getWatchStatus() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_watch_status'
    });
  }
  
  /**
   * Close auction connection and cleanup
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
      
      // Clear callback registry
      this._callbacks.clear();
    }
  }
  
  /**
   * Get connection status
   * @returns {Object} Current connection status
   */
  getStatus() {
    return this.socket ? this.socket.getStatus() : { status: 'disconnected' };
  }
}

/**
 * Bidding WebSocket service
 */
export class BiddingService {
  constructor(auctionId, options = {}) {
    this.auctionId = auctionId;
    this.path = `ws/auctions/${auctionId}/bids/`;
    this.options = {
      debug: false,
      ...options
    };
    
    this.socket = createWebSocket(this.path, {
      autoReconnect: true,
      ...options
    });
    
    // Generate unique client ID for this instance
    this.clientId = `bid_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    // Initialize callback registry
    this._callbacks = new Set();
  }
  
  /**
   * Subscribe to bidding updates
   * @param {Function} callback - Handler for all bidding-related events
   * @returns {Function} Unsubscribe function
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
    // Keep track of the callback for reconnection handling
    this._callbacks.add(callback);
    
    // Subscribe to all bidding-related messages
    const handlers = [
      this.socket.onMessage('bidding_init', callback),
      this.socket.onMessage('new_bid', callback),
      this.socket.onMessage('recent_bids', callback),
      this.socket.onMessage('bid_history', callback),
      this.socket.onMessage('auction_status', callback),
      this.socket.onMessage('bidding_update', callback)
    ];
    
    // Return unsubscribe function
    return () => {
      handlers.forEach(unsubscribe => unsubscribe && unsubscribe());
      this._callbacks.delete(callback);
    };
  }
  
  /**
   * Subscribe to specific update type
   * @param {string} updateType - Update type to subscribe to
   * @param {Function} callback - Event handler
   * @returns {Function} Unsubscribe function
   */
  on(updateType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(updateType, callback);
  }
  
  /**
   * Place a bid with improved error handling
   * @param {number} amount - Bid amount
   * @param {number|null} autoBidLimit - Maximum auto-bid amount (optional)
   * @param {string|null} userId - User ID (will be taken from localStorage if not provided)
   * @returns {Promise} Promise resolving with bid data when bid is placed
   */
  placeBid(amount, autoBidLimit = null, userId = null) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    // Get user ID from localStorage if not provided
    if (!userId && browser) {
      try {
        const userData = JSON.parse(localStorage.getItem('user'));
        userId = userData?.id;
      } catch (error) {
        console.warn('Failed to get user ID from localStorage:', error);
      }
    }
    
    if (!userId) {
      return Promise.reject(new Error('User ID is required to place a bid'));
    }
    
    // Validate bid amount
    if (!amount || isNaN(parseFloat(amount))) {
      return Promise.reject(new Error('Valid bid amount is required'));
    }
    
    return new Promise((resolve, reject) => {
      // Listen for error response
      const errorHandler = this.socket.onMessage(`error:${this.clientId}`, (data) => {
        removeHandlers();
        reject(new Error(data.message || 'Failed to place bid'));
      });
      
      // Listen for new bid response
      const newBidHandler = this.socket.onMessage('new_bid', (data) => {
        // Check if this is our bid (matching client_id)
        if (data.bid && data.bid.client_id === this.clientId) {
          removeHandlers();
          resolve(data.bid);
        }
      });
      
      // Function to clean up handlers
      const removeHandlers = () => {
        errorHandler && errorHandler();
        newBidHandler && newBidHandler();
      };
      
      // Send bid
      this.socket.send({
        action: 'place_bid',
        amount: amount,
        auto_bid_limit: autoBidLimit,
        user_id: userId,
        client_id: this.clientId
      }).catch(error => {
        removeHandlers();
        reject(error);
      });
      
      // Timeout after 10 seconds
      setTimeout(() => {
        removeHandlers();
        reject(new Error('Bid request timed out'));
      }, 10000);
    });
  }
  
  /**
   * Get recent bids
   * @param {number} limit - Number of bids to retrieve
   * @returns {Promise} Promise resolving when request is sent
   */
  getRecentBids(limit = 10) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_recent_bids',
      limit: limit
    });
  }
  
  /**
   * Get complete bid history with pagination
   * @param {number} page - Page number (1-based)
   * @param {number} pageSize - Number of bids per page
   * @returns {Promise} Promise resolving when request is sent
   */
  getBidHistory(page = 1, pageSize = 20) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_bid_history',
      page: page,
      page_size: pageSize
    });
  }
  
  /**
   * Close bidding connection and cleanup
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
      
      // Clear callback registry
      this._callbacks.clear();
    }
  }
  
  /**
   * Get connection status
   * @returns {Object} Current connection status
   */
  getStatus() {
    return this.socket ? this.socket.getStatus() : { status: 'disconnected' };
  }
}

/**
 * Chat WebSocket service
 */
export class ChatService {
  constructor(roomName, options = {}) {
    this.roomName = roomName;
    this.path = `ws/chat/${roomName}/`;
    this.options = {
      debug: false,
      ...options
    };
    
    this.socket = createWebSocket(this.path, {
      autoReconnect: true,
      ...options
    });
    
    // Generate unique client ID for this instance
    this.clientId = `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    // Initialize callback registry
    this._callbacks = new Set();
  }
  
  /**
   * Subscribe to chat messages
   * @param {Function} callback - Handler for all chat-related events
   * @returns {Function} Unsubscribe function
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
    // Keep track of the callback for reconnection handling
    this._callbacks.add(callback);
    
    // Subscribe to all chat-related messages
    const handlers = [
      this.socket.onMessage('chat_history', callback),
      this.socket.onMessage('message', callback),
      this.socket.onMessage('system', callback),
      this.socket.onMessage('typing', callback),
      this.socket.onMessage('read_receipt', callback),
      this.socket.onMessage('message_history', callback)
    ];
    
    // Return unsubscribe function
    return () => {
      handlers.forEach(unsubscribe => unsubscribe && unsubscribe());
      this._callbacks.delete(callback);
    };
  }
  
  /**
   * Subscribe to specific message type
   * @param {string} messageType - Message type to subscribe to
   * @param {Function} callback - Event handler
   * @returns {Function} Unsubscribe function
   */
  on(messageType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(messageType, callback);
  }
  
  /**
   * Send a chat message with improved error handling
   * @param {string} message - Message content
   * @returns {Promise} Promise resolving with message data when sent
   */
  sendMessage(message) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    // Validate message
    if (!message || typeof message !== 'string' || !message.trim()) {
      return Promise.reject(new Error('Message cannot be empty'));
    }
    
    if (message.length > 5000) {
      return Promise.reject(new Error('Message is too long (max 5000 characters)'));
    }
    
    return new Promise((resolve, reject) => {
      // Listen for error response
      const errorHandler = this.socket.onMessage(`error:${this.clientId}`, (data) => {
        removeHandlers();
        reject(new Error(data.message || 'Failed to send message'));
      });
      
      // Listen for message receipt
      const messageHandler = this.socket.onMessage('message', (data) => {
        // Check if this is our message (matching client_id)
        if (data.client_id === this.clientId) {
          removeHandlers();
          resolve(data);
        }
      });
      
      // Function to clean up handlers
      const removeHandlers = () => {
        errorHandler && errorHandler();
        messageHandler && messageHandler();
      };
      
      // Send message
      this.socket.send({
        type: 'message',
        message: message,
        client_id: this.clientId
      }).catch(error => {
        removeHandlers();
        reject(error);
      });
      
      // Timeout after 5 seconds
      setTimeout(() => {
        removeHandlers();
        reject(new Error('Message request timed out'));
      }, 5000);
    });
  }
  
  /**
   * Send typing indicator
   * @param {boolean} isTyping - Whether the user is typing
   * @returns {Promise} Promise resolving when request is sent
   */
  sendTypingIndicator(isTyping = true) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      type: 'typing',
      is_typing: isTyping
    });
  }
  
  /**
   * Mark message as read
   * @param {string} messageId - ID of the message to mark as read
   * @returns {Promise} Promise resolving when request is sent
   */
  markMessageRead(messageId) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      type: 'read_receipt',
      message_id: messageId
    });
  }
  
  /**
   * Load more message history
   * @param {string} beforeId - ID of the oldest loaded message
   * @param {number} limit - Number of messages to load
   * @returns {Promise} Promise resolving when request is sent
   */
  loadMoreMessages(beforeId, limit = 20) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      type: 'load_more',
      before_id: beforeId,
      limit: limit
    });
  }
  
  /**
   * Close chat connection and cleanup
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
      
      // Clear callback registry
      this._callbacks.clear();
    }
  }
  
  /**
   * Get connection status
   * @returns {Object} Current connection status
   */
  getStatus() {
    return this.socket ? this.socket.getStatus() : { status: 'disconnected' };
  }
}

/**
 * Notification WebSocket service
 */
export class NotificationService {
  constructor(userId, options = {}) {
    this.userId = userId;
    this.path = `ws/notifications/${userId}/`;
    this.options = {
      debug: false,
      ...options
    };
    
    this.socket = createWebSocket(this.path, {
      autoReconnect: true,
      ...options
    });
    
    // Initialize callback registry
    this._callbacks = new Set();
  }
  
  /**
   * Subscribe to notifications
   * @param {Function} callback - Handler for all notification-related events
   * @returns {Function} Unsubscribe function
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
    // Keep track of the callback for reconnection handling
    this._callbacks.add(callback);
    
    // Subscribe to all notification-related messages
    const handlers = [
      this.socket.onMessage('notifications', callback),
      this.socket.onMessage('new_notification', callback),
      this.socket.onMessage('notification_read', callback),
      this.socket.onMessage('all_read', callback),
      this.socket.onMessage('notification_deleted', callback),
      this.socket.onMessage('unread_count', callback)
    ];
    
    // Return unsubscribe function
    return () => {
      handlers.forEach(unsubscribe => unsubscribe && unsubscribe());
      this._callbacks.delete(callback);
    };
  }
  
  /**
   * Subscribe to specific notification type
   * @param {string} notificationType - Notification type to subscribe to
   * @param {Function} callback - Event handler
   * @returns {Function} Unsubscribe function
   */
  on(notificationType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(notificationType, callback);
  }
  
  /**
   * Mark notification as read
   * @param {string} notificationId - ID of the notification to mark as read
   * @returns {Promise} Promise resolving when request is sent
   */
  markRead(notificationId) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'mark_read',
      notification_id: notificationId
    });
  }
  
  /**
   * Mark all notifications as read
   * @returns {Promise} Promise resolving when request is sent
   */
  markAllRead() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'mark_all_read'
    });
  }
  
  /**
   * Mark notification as displayed
   * @param {string} notificationId - ID of the notification to mark as displayed
   * @returns {Promise} Promise resolving when request is sent
   */
  markDisplayed(notificationId) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'mark_displayed',
      notification_id: notificationId
    });
  }
  
  /**
   * Get notifications with pagination
   * @param {number} limit - Number of notifications to retrieve
   * @param {number} offset - Offset for pagination
   * @returns {Promise} Promise resolving when request is sent
   */
  getNotifications(limit = 50, offset = 0) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_notifications',
      limit: limit,
      offset: offset
    });
  }
  
  /**
   * Get unread notifications count
   * @returns {Promise} Promise resolving when request is sent
   */
  getUnreadCount() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_unread_count'
    });
  }
  
  /**
   * Close notification connection and cleanup
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
      
      // Clear callback registry
      this._callbacks.clear();
    }
  }
  
  /**
   * Get connection status
   * @returns {Object} Current connection status
   */
  getStatus() {
    return this.socket ? this.socket.getStatus() : { status: 'disconnected' };
  }
}

/**
 * Dashboard WebSocket service
 */
export class DashboardService {
  constructor(userId, options = {}) {
    this.userId = userId;
    this.path = `ws/dashboard/${userId}/`;
    this.options = {
      debug: false,
      ...options
    };
    
    this.socket = createWebSocket(this.path, {
      autoReconnect: true,
      ...options
    });
    
    // Initialize callback registry
    this._callbacks = new Set();
  }
  
  /**
   * Subscribe to dashboard updates
   * @param {Function} callback - Handler for all dashboard-related events
   * @returns {Function} Unsubscribe function
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
    // Keep track of the callback for reconnection handling
    this._callbacks.add(callback);
    
    // Subscribe to all dashboard-related messages
    const handlers = [
      this.socket.onMessage('dashboard_data', callback),
      this.socket.onMessage('section_data', callback),
      this.socket.onMessage('chart_data', callback),
      this.socket.onMessage('dashboard_update', callback),
      this.socket.onMessage('auction_update', callback),
      this.socket.onMessage('bid_update', callback),
      this.socket.onMessage('transaction_update', callback),
      this.socket.onMessage('notification', callback)
    ];
    
    // Return unsubscribe function
    return () => {
      handlers.forEach(unsubscribe => unsubscribe && unsubscribe());
      this._callbacks.delete(callback);
    };
  }
  
  /**
   * Subscribe to specific update type
   * @param {string} updateType - Update type to subscribe to
   * @param {Function} callback - Event handler
   * @returns {Function} Unsubscribe function
   */
  on(updateType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(updateType, callback);
  }
  
  /**
   * Refresh dashboard data
   * @returns {Promise} Promise resolving when request is sent
   */
  refreshDashboard() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'refresh_dashboard'
    });
  }
  
  /**
   * Get specific dashboard section data
   * @param {string} section - Section name (properties, auctions, bids, contracts, etc.)
   * @returns {Promise} Promise resolving when request is sent
   */
  getSection(section) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_section',
      section: section
    });
  }
  
  /**
   * Get chart data
   * @param {string} chartType - Chart type to retrieve data for
   * @param {Object} params - Additional parameters for the chart
   * @returns {Promise} Promise resolving when request is sent
   */
  getChartData(chartType, params = {}) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_chart_data',
      chart_type: chartType,
      params: params
    });
  }
  
  /**
   * Close dashboard connection and cleanup
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
      
      // Clear callback registry
      this._callbacks.clear();
    }
  }
  
  /**
   * Get connection status
   * @returns {Object} Current connection status
   */
  getStatus() {
    return this.socket ? this.socket.getStatus() : { status: 'disconnected' };
  }
}

/**
 * Get token from localStorage with validation
 * @returns {string|null} Access token or null if not found
 */
function getToken() {
  if (!browser) return null;
  
  try {
    // Try getting token directly
    const token = localStorage.getItem('accessToken');
    if (token && typeof token === 'string' && token.trim()) {
      return token;
    }
    
    // Try getting from auth object
    const authStr = localStorage.getItem('auth');
    if (authStr) {
      try {
        const auth = JSON.parse(authStr);
        if (auth && auth.token && typeof auth.token === 'string' && auth.token.trim()) {
          return auth.token;
        }
      } catch (e) {
        console.warn('Failed to parse auth data:', e);
      }
    }
    
    return null;
  } catch (e) {
    console.error('Error getting token:', e);
    return null;
  }
}

/**
 * Close all active WebSocket connections
 */
export function closeAllConnections() {
  if (!browser) return;
  
  const activeConnections = get(connections);
  
  Object.values(activeConnections).forEach(connection => {
    if (connection && typeof connection.disconnect === 'function') {
      connection.disconnect();
    }
  });
  
  // Clear connections store
  connections.set({});
}

// Export default object with all services
export default {
  createWebSocket,
  AuctionService,
  BiddingService,
  ChatService,
  NotificationService,
  DashboardService,
  closeAllConnections,
  connections,
  connectionStatus,
  getToken
};