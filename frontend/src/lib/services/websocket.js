// src/lib/services/websocket.js
import { browser } from '$app/environment';
import { writable, get } from 'svelte/store';
import { goto } from '$app/navigation';

/**
 * WebSocket service for real-time communication with the backend.
 * Handles connections to auction, bidding, chat, notifications, and dashboard.
 */

// Configuration
const WS_BASE_URL = browser ? 
  (import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`) : 
  null;

const RECONNECT_INTERVAL = 5000; // 5 seconds
const MAX_RECONNECT_ATTEMPTS = 5;
const PING_INTERVAL = 30000; // 30 seconds

// Store for active connections
export const connections = writable({});

// Store for connection statuses
export const connectionStatus = writable({});

/**
 * Base WebSocket connection manager
 */
class WebSocketConnection {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.socket = null;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.pingTimer = null;
    this.messageHandlers = new Map();
    this.eventHandlers = {
      onOpen: [],
      onClose: [],
      onError: [],
      onMessage: [],
      onReconnect: [],
      onReconnectFailed: []
    };
    
    // Automatically connect if autoConnect is enabled
    if (this.options.autoConnect !== false) {
      this.connect();
    }
  }
  
  /**
   * Connect to WebSocket
   */
  connect() {
    if (!browser) return;
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }
    
    this.isConnecting = true;
    
    try {
      // Get authentication token
      const token = this.options.getToken ? this.options.getToken() : localStorage.getItem('accessToken');
      
      // Build URL with authentication token
      const wsUrl = new URL(this.url, WS_BASE_URL);
      
      // Add token as query parameter if provided
      if (token) {
        wsUrl.searchParams.append('token', token);
      }
      
      // Create WebSocket
      this.socket = new WebSocket(wsUrl.toString());
      
      // Setup event handlers
      this.socket.onopen = (event) => this.handleOpen(event);
      this.socket.onclose = (event) => this.handleClose(event);
      this.socket.onerror = (event) => this.handleError(event);
      this.socket.onmessage = (event) => this.handleMessage(event);
      
      // Update connection status
      this.updateStatus('connecting');
    } catch (error) {
      console.error(`WebSocket connection error for ${this.url}:`, error);
      this.updateStatus('error', error.message);
      this.scheduleReconnect();
    }
  }
  
  /**
   * Disconnect from WebSocket
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
  }
  
  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.updateStatus('connected');
    
    // Setup ping interval to keep connection alive
    this.setupPing();
    
    // Call event handlers
    this.eventHandlers.onOpen.forEach(handler => handler(event));
  }
  
  /**
   * Handle WebSocket close event
   */
  handleClose(event) {
    this.clearTimers();
    
    // Update status based on close code
    if (event.code === 1000) {
      // Normal closure
      this.updateStatus('disconnected');
    } else if (event.code === 1006) {
      // Abnormal closure, attempt reconnect
      this.updateStatus('disconnected', 'Connection lost');
      if (this.options.autoReconnect !== false) {
        this.scheduleReconnect();
      }
    } else if (event.code === 4003) {
      // Authentication failure
      this.updateStatus('auth_failed', 'Authentication failed');
      
      // Redirect to login if configured
      if (this.options.redirectOnAuthFailure !== false) {
        goto('/auth/login');
      }
    } else {
      this.updateStatus('error', `Closed with code ${event.code}: ${event.reason}`);
      if (this.options.autoReconnect !== false) {
        this.scheduleReconnect();
      }
    }
    
    // Call event handlers
    this.eventHandlers.onClose.forEach(handler => handler(event));
  }
  
  /**
   * Handle WebSocket error event
   */
  handleError(event) {
    console.error(`WebSocket error for ${this.url}:`, event);
    this.updateStatus('error', 'Connection error');
    
    // Call event handlers
    this.eventHandlers.onError.forEach(handler => handler(event));
  }
  
  /**
   * Handle WebSocket message event
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      
      // Handle ping/pong for keepalive
      if (data.type === 'pong') {
        return;
      }
      
      // Handle error messages
      if (data.type === 'error') {
        console.error(`WebSocket error from server:`, data);
        
        // Update status
        this.updateStatus('error', data.message);
        
        // Check if client_id is provided and call specific handler
        if (data.client_id && this.messageHandlers.has(`error:${data.client_id}`)) {
          this.messageHandlers.get(`error:${data.client_id}`)(data);
          return;
        }
      }
      
      // Call specific message type handlers
      if (data.type && this.messageHandlers.has(data.type)) {
        this.messageHandlers.get(data.type)(data);
      }
      
      // Call message event handlers
      this.eventHandlers.onMessage.forEach(handler => handler(data));
    } catch (error) {
      console.error(`Error parsing WebSocket message:`, error, event.data);
    }
  }
  
  /**
   * Send message to WebSocket
   */
  send(data) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.warn(`Cannot send message, WebSocket is not connected. Attempting to connect...`);
      
      // Try to reconnect and queue the message
      if (this.options.autoReconnect !== false) {
        this.connect();
        
        // Wait for connection and retry sending
        return new Promise((resolve, reject) => {
          const openHandler = () => {
            this.off('open', openHandler);
            this.off('error', errorHandler);
            
            // Try sending again after connection
            resolve(this.send(data));
          };
          
          const errorHandler = (event) => {
            this.off('open', openHandler);
            this.off('error', errorHandler);
            reject(new Error('Failed to connect for sending message'));
          };
          
          this.on('open', openHandler);
          this.on('error', errorHandler);
          
          // Timeout if connection takes too long
          setTimeout(() => {
            this.off('open', openHandler);
            this.off('error', errorHandler);
            reject(new Error('Connection timeout while trying to send message'));
          }, 5000);
        });
      }
      
      return Promise.reject(new Error('WebSocket is not connected'));
    }
    
    try {
      // Convert data to JSON string
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      return Promise.resolve();
    } catch (error) {
      console.error(`Error sending WebSocket message:`, error);
      return Promise.reject(error);
    }
  }
  
  /**
   * Subscribe to message type
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
   * Subscribe to events
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
      [this.url]: { status, message, timestamp: new Date().toISOString() }
    }));
  }
  
  /**
   * Schedule reconnection
   */
  scheduleReconnect() {
    if (this.options.autoReconnect === false || this.reconnectTimer) {
      return;
    }
    
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts > MAX_RECONNECT_ATTEMPTS) {
      this.updateStatus('reconnect_failed', `Failed after ${MAX_RECONNECT_ATTEMPTS} attempts`);
      
      // Call reconnect failed handlers
      this.eventHandlers.onReconnectFailed.forEach(handler => handler());
      return;
    }
    
    // Exponential backoff
    const delay = Math.min(RECONNECT_INTERVAL * Math.pow(1.5, this.reconnectAttempts - 1), 60000);
    
    this.updateStatus('reconnecting', `Attempt ${this.reconnectAttempts} of ${MAX_RECONNECT_ATTEMPTS}`);
    
    // Schedule reconnect
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      
      // Call reconnect handlers
      this.eventHandlers.onReconnect.forEach(handler => handler(this.reconnectAttempts));
      
      // Attempt reconnection
      this.connect();
    }, delay);
  }
  
  /**
   * Setup ping interval to keep connection alive
   */
  setupPing() {
    this.clearTimers();
    
    this.pingTimer = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' }).catch(error => {
          console.warn('Failed to send ping:', error);
        });
      }
    }, PING_INTERVAL);
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
}

/**
 * Create a WebSocket connection with connection management
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
  constructor(auctionId) {
    this.auctionId = auctionId;
    this.path = `ws/auctions/${auctionId}/updates/`;
    this.socket = createWebSocket(this.path, {
      autoReconnect: true
    });
    
    // Initialize handlers
    this.handlers = {};
  }
  
  /**
   * Subscribe to auction updates
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
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
    };
  }
  
  /**
   * Subscribe to specific update type
   */
  on(updateType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(updateType, callback);
  }
  
  /**
   * Get current auction state
   */
  getState() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_state'
    });
  }
  
  /**
   * Watch auction
   */
  watch() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'watch_auction'
    });
  }
  
  /**
   * Unwatch auction
   */
  unwatch() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'unwatch_auction'
    });
  }
  
  /**
   * Check if user is watching auction
   */
  getWatchStatus() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_watch_status'
    });
  }
  
  /**
   * Close auction connection
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
    }
  }
}

/**
 * Bidding WebSocket service
 */
export class BiddingService {
  constructor(auctionId) {
    this.auctionId = auctionId;
    this.path = `ws/auctions/${auctionId}/bids/`;
    this.socket = createWebSocket(this.path, {
      autoReconnect: true
    });
    
    // Generate unique client ID for this instance
    this.clientId = `bid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Subscribe to bidding updates
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
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
    };
  }
  
  /**
   * Subscribe to specific update type
   */
  on(updateType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(updateType, callback);
  }
  
  /**
   * Place a bid
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
      return Promise.reject(new Error('User ID is required'));
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
   * Close bidding connection
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
    }
  }
}

/**
 * Chat WebSocket service
 */
export class ChatService {
  constructor(roomName) {
    this.roomName = roomName;
    this.path = `ws/chat/${roomName}/`;
    this.socket = createWebSocket(this.path, {
      autoReconnect: true
    });
    
    // Generate unique client ID for this instance
    this.clientId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Subscribe to chat messages
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
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
    };
  }
  
  /**
   * Subscribe to specific message type
   */
  on(messageType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(messageType, callback);
  }
  
  /**
   * Send a chat message
   */
  sendMessage(message) {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
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
   * Close chat connection
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
    }
  }
}

/**
 * Notification WebSocket service
 */
export class NotificationService {
  constructor(userId) {
    this.userId = userId;
    this.path = `ws/notifications/${userId}/`;
    this.socket = createWebSocket(this.path, {
      autoReconnect: true
    });
  }
  
  /**
   * Subscribe to notifications
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
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
    };
  }
  
  /**
   * Subscribe to specific notification type
   */
  on(notificationType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(notificationType, callback);
  }
  
  /**
   * Mark notification as read
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
   */
  markAllRead() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'mark_all_read'
    });
  }
  
  /**
   * Mark notification as displayed
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
   */
  getUnreadCount() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'get_unread_count'
    });
  }
  
  /**
   * Close notification connection
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
    }
  }
}

/**
 * Dashboard WebSocket service
 */
export class DashboardService {
  constructor(userId) {
    this.userId = userId;
    this.path = `ws/dashboard/${userId}/`;
    this.socket = createWebSocket(this.path, {
      autoReconnect: true
    });
  }
  
  /**
   * Subscribe to dashboard updates
   */
  subscribe(callback) {
    if (!this.socket) return () => {};
    
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
    };
  }
  
  /**
   * Subscribe to specific update type
   */
  on(updateType, callback) {
    if (!this.socket) return () => {};
    return this.socket.onMessage(updateType, callback);
  }
  
  /**
   * Refresh dashboard data
   */
  refreshDashboard() {
    if (!this.socket) return Promise.reject(new Error('WebSocket not available'));
    
    return this.socket.send({
      action: 'refresh_dashboard'
    });
  }
  
  /**
   * Get specific dashboard section data
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
   * Close dashboard connection
   */
  close() {
    if (this.socket) {
      this.socket.disconnect();
      
      // Remove from connections store
      connections.update(current => {
        const { [this.path]: _, ...rest } = current;
        return rest;
      });
    }
  }
}

/**
 * Get token from localStorage
 */
function getToken() {
  if (!browser) return null;
  return localStorage.getItem('accessToken');
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
  connectionStatus
};