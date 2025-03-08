// /src/lib/websocketService.js
import { browser } from '$app/environment';
import { writable } from 'svelte/store';
import { authStore } from './stores/authStore';
import { notificationStore } from './stores/notificationStore';

/**
 * Constants for WebSocket operations
 */
const WS_BASE_URL = browser ? (import.meta.env.VITE_WS_BASE_URL || `ws://${window.location.host}/ws`) : '';
const WS_RECONNECT_DELAY = 1000; // Base delay of 1 second
const WS_MAX_RECONNECT_ATTEMPTS = 5;
const WS_PING_INTERVAL = 30000; // 30 seconds

/**
 * Create a dashboard WebSocket connection for a specific user
 * @param {string} userId - The user ID
 * @returns {Object} - Object with stores and methods for interacting with WebSocket
 */
export function createDashboardConnection(userId) {
  if (!browser || !userId) {
    return {
      dashboardData: writable({}),
      status: writable('disconnected'),
      refreshDashboard: () => console.warn('WebSocket not available in server environment'),
      getSection: () => console.warn('WebSocket not available in server environment'),
      reconnect: () => console.warn('WebSocket not available in server environment'),
      isConnected: () => false,
      close: () => {}
    };
  }
  
  // Create stores for dashboard data and connection status
  const dashboardData = writable({});
  const status = writable('connecting');
  
  let socket = null;
  let reconnectAttempts = 0;
  let reconnectTimer = null;
  let pingTimer = null;
  let isClosing = false;
  
  function connect() {
    try {
      status.set('connecting');
      
      // Get authentication token and ensure it's properly formatted
      let accessToken = '';
      try {
        accessToken = localStorage.getItem('accessToken') || '';
        // Ensure token is properly URL encoded to prevent 400 Bad Request errors
        accessToken = encodeURIComponent(accessToken);
      } catch (e) {
        console.error('Error accessing localStorage:', e);
      }
      
      // Create WebSocket connection with authentication token
      const wsUrl = `${WS_BASE_URL}/dashboard/${userId}/?token=${accessToken}`;
      console.log(`Connecting to dashboard WebSocket: ${wsUrl}`);
      socket = new WebSocket(wsUrl);
      
      // Connection opened handler
      socket.addEventListener('open', (event) => {
        console.log(`Dashboard WebSocket connection opened for user ${userId}`);
        status.set('connected');
        reconnectAttempts = 0; // Reset reconnect attempts on successful connection
        
        // Setup ping interval to keep connection alive
        if (pingTimer) clearInterval(pingTimer);
        pingTimer = setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);
        
        // Request initial dashboard data
        socket.send(JSON.stringify({ action: 'get_dashboard' }));
      });
      
      // Connection error handler with more detailed logging
      socket.addEventListener('error', (event) => {
        console.error(`Dashboard WebSocket error for user ${userId}:`, event);
        status.set('error');
      });
      
      // Connection closed handler with more detailed logging
      socket.addEventListener('close', (event) => {
        console.log(`Dashboard WebSocket connection closed for user ${userId}. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}, Was Clean: ${event.wasClean}`);
        status.set('disconnected');
        
        // Clear ping timer
        if (pingTimer) {
          clearInterval(pingTimer);
          pingTimer = null;
        }
        
        // Handle disconnection with exponential backoff
        if (!isClosing) {
          handleDisconnect();
        }
      });
      
      // Message handler with improved error handling
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'pong') {
            // Heartbeat response, no further action needed
            return;
          } else if (data.type === 'error') {
            console.error('WebSocket error message:', data.error);
            notificationStore.error(`Dashboard error: ${data.error}`);
            return;
          } else if (data.type === 'dashboard_data') {
            // Update dashboard data store
            console.log('Received dashboard data update');
            dashboardData.set(data.data || {});
          } else if (data.type === 'section_data') {
            // Update a specific section of the dashboard data
            console.log(`Received section data update for: ${data.section}`);
            dashboardData.update(currentData => {
              return {
                ...currentData,
                [data.section]: data.data
              };
            });
          } else {
            console.warn('Unknown message type received:', data.type);
          }
        } catch (error) {
          console.error('Error parsing dashboard WebSocket message:', error);
        }
      });
    } catch (error) {
      console.error('Error creating dashboard WebSocket connection:', error);
      status.set('error');
      handleDisconnect();
    }
  }
  
  function handleDisconnect() {
    if (reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      console.log(`Attempting to reconnect (${reconnectAttempts}/${WS_MAX_RECONNECT_ATTEMPTS})...`);
      
      // Clear any existing reconnect timer
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      
      // Use exponential backoff with jitter for reconnection
      const delay = WS_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
      const jitter = Math.random() * 1000;
      reconnectTimer = setTimeout(connect, delay + jitter);
      
      // Update status to show reconnecting
      status.set('reconnecting');
    } else {
      console.log(`Max reconnection attempts (${WS_MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`);
      status.set('failed');
    }
  }
  
  // Initialize the connection
  connect();
  
  // Return public interface
  return {
    dashboardData,
    status,
    
    /**
     * Request a full dashboard refresh
     */
    refreshDashboard: () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          action: 'get_dashboard'
        }));
      } else {
        console.warn('Cannot request dashboard refresh: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Request a specific section refresh
     * @param {string} section - The section name to refresh (e.g., 'recent_auctions', 'statistics')
     */
    getSection: (section) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          action: 'get_section',
          section: section
        }));
      } else {
        console.warn(`Cannot request section ${section}: WebSocket not connected`);
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Check if WebSocket is connected
     * @returns {boolean} - True if connected, false otherwise
     */
    isConnected: () => {
      return socket && socket.readyState === WebSocket.OPEN;
    },
    
    /**
     * Manually attempt to reconnect
     * @returns {boolean} - True if reconnection was initiated, false otherwise
     */
    reconnect: () => {
      if (socket && socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING) {
        reconnectAttempts = 0; // Reset counter for manual reconnect
        connect();
        return true;
      }
      return false;
    },
    
    /**
     * Send any message via WebSocket
     * @param {object} data - Data to send
     */
    send: (data) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        console.warn('Cannot send message: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Close the WebSocket connection
     */
    close: () => {
      isClosing = true;
      
      // Clear timers
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      
      if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
      }
      
      // Close socket
      if (socket) {
        socket.close();
        socket = null;
      }
      
      status.set('disconnected');
    }
  };
}

/**
 * Create a notification WebSocket connection for a specific user
 * @param {string} userId - The user ID
 * @returns {Object} - Object with stores and methods for interacting with WebSocket
 */
export function createNotificationConnection(userId) {
  if (!browser || !userId) {
    return {
      notifications: writable([]),
      status: writable('disconnected'),
      markAsRead: () => console.warn('WebSocket not available in server environment'),
      markAllAsRead: () => console.warn('WebSocket not available in server environment'),
      reconnect: () => console.warn('WebSocket not available in server environment'),
      close: () => {}
    };
  }
  
  // Create stores for notifications and connection status
  const notifications = writable([]);
  const status = writable('connecting');
  
  let socket = null;
  let reconnectAttempts = 0;
  let reconnectTimer = null;
  let pingTimer = null;
  let isClosing = false;
  
  function connect() {
    try {
      status.set('connecting');
      
      // Get authentication token and ensure it's properly formatted
      let accessToken = '';
      try {
        accessToken = localStorage.getItem('accessToken') || '';
        // Ensure token is properly URL encoded to prevent 400 Bad Request errors
        accessToken = encodeURIComponent(accessToken);
      } catch (e) {
        console.error('Error accessing localStorage:', e);
      }
      
      // Create WebSocket connection with authentication token
      const wsUrl = `${WS_BASE_URL}/notifications/${userId}/?token=${accessToken}`;
      console.log(`Connecting to notification WebSocket: ${wsUrl}`);
      socket = new WebSocket(wsUrl);
      
      // Connection opened handler
      socket.addEventListener('open', (event) => {
        console.log(`Notification WebSocket connection opened for user ${userId}`);
        status.set('connected');
        reconnectAttempts = 0; // Reset reconnect attempts on successful connection
        
        // Setup ping interval to keep connection alive
        if (pingTimer) clearInterval(pingTimer);
        pingTimer = setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);
      });
      
      // Connection error handler with more detailed logging
      socket.addEventListener('error', (event) => {
        console.error(`Notification WebSocket error for user ${userId}:`, event);
        status.set('error');
      });
      
      // Connection closed handler with more detailed logging
      socket.addEventListener('close', (event) => {
        console.log(`Notification WebSocket connection closed for user ${userId}. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}, Was Clean: ${event.wasClean}`);
        status.set('disconnected');
        
        // Clear ping timer
        if (pingTimer) {
          clearInterval(pingTimer);
          pingTimer = null;
        }
        
        // Handle disconnection with exponential backoff
        if (!isClosing) {
          handleDisconnect();
        }
      });
      
      // Message handler with improved error handling
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'pong') {
            // Heartbeat response, no further action needed
            return;
          } else if (data.type === 'error') {
            console.error('WebSocket error message:', data.error);
            notificationStore.error(`Notification error: ${data.error}`);
            return;
          } else if (data.type === 'notifications') {
            // Update notifications store with initial notifications
            console.log('Received initial notifications:', data.notifications?.length || 0);
            notifications.set(data.notifications || []);
          } else if (data.type === 'new_notification') {
            // Add new notification to existing notifications
            console.log('Received new notification:', data.notification);
            notifications.update(currentNotifications => {
              const newNotification = data.notification;
              
              // Check if this notification already exists
              const existingNotificationIndex = currentNotifications.findIndex(n => n.id === newNotification.id);
              
              if (existingNotificationIndex >= 0) {
                // Update existing notification
                const updatedNotifications = [...currentNotifications];
                updatedNotifications[existingNotificationIndex] = newNotification;
                return updatedNotifications;
              } else {
                // Add new notification to the beginning
                return [newNotification, ...currentNotifications];
              }
            });
            
            // Display notification using notification system
            if (data.notification.message) {
              notificationStore.info(data.notification.message);
            }
          } else if (data.type === 'notification_read') {
            // Update notification read status
            console.log('Notification marked as read:', data.notification_id);
            notifications.update(currentNotifications => {
              return currentNotifications.map(notification => {
                if (notification.id === data.notification_id) {
                  return { ...notification, read: true };
                }
                return notification;
              });
            });
          } else if (data.type === 'all_read') {
            // Mark all notifications as read
            console.log('All notifications marked as read');
            notifications.update(currentNotifications => {
              return currentNotifications.map(notification => ({
                ...notification,
                read: true
              }));
            });
          } else {
            console.warn('Unknown message type received:', data.type);
          }
        } catch (error) {
          console.error('Error parsing notification WebSocket message:', error);
        }
      });
    } catch (error) {
      console.error('Error creating notification WebSocket connection:', error);
      status.set('error');
      handleDisconnect();
    }
  }
  
  function handleDisconnect() {
    if (reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      console.log(`Attempting to reconnect (${reconnectAttempts}/${WS_MAX_RECONNECT_ATTEMPTS})...`);
      
      // Clear any existing reconnect timer
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      
      // Use exponential backoff with jitter for reconnection
      const delay = WS_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
      const jitter = Math.random() * 1000;
      reconnectTimer = setTimeout(connect, delay + jitter);
      
      // Update status to show reconnecting
      status.set('reconnecting');
    } else {
      console.log(`Max reconnection attempts (${WS_MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`);
      status.set('failed');
      
      // We avoid notifying the user here since this IS the notification system
      // Instead, we'll show a subtle indicator in the UI
    }
  }
  
  // Initialize the connection
  connect();
  
  // Return public interface
  return {
    notifications,
    status,
    
    /**
     * Mark a notification as read
     * @param {string} notificationId - Notification ID to mark as read
     */
    markAsRead: (notificationId) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          action: 'mark_read',
          notification_id: notificationId
        }));
        
        // Optimistically update UI
        notifications.update(currentNotifications => {
          return currentNotifications.map(notification => {
            if (notification.id === notificationId) {
              return { ...notification, read: true };
            }
            return notification;
          });
        });
      } else {
        console.warn('Cannot mark notification as read: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Mark all notifications as read
     */
    markAllAsRead: () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          action: 'mark_all_read'
        }));
        
        // Optimistically update UI
        notifications.update(currentNotifications => {
          return currentNotifications.map(notification => ({
            ...notification,
            read: true
          }));
        });
      } else {
        console.warn('Cannot mark all notifications as read: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Manually attempt to reconnect
     * @returns {boolean} - True if reconnection was initiated, false otherwise
     */
    reconnect: () => {
      if (socket && socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING) {
        reconnectAttempts = 0; // Reset counter for manual reconnect
        connect();
        return true;
      }
      return false;
    },
    
    /**
     * Check if WebSocket is connected
     * @returns {boolean} - True if connected, false otherwise
     */
    isConnected: () => {
      return socket && socket.readyState === WebSocket.OPEN;
    },
    
    /**
     * Send any message via WebSocket
     * @param {object} data - Data to send
     */
    send: (data) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        console.warn('Cannot send message: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Close the WebSocket connection
     */
    close: () => {
      isClosing = true;
      
      // Clear timers
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      
      if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
      }
      
      // Close socket
      if (socket) {
        socket.close();
        socket = null;
      }
      
      status.set('disconnected');
    }
  };
}



/**
 * Create a chat WebSocket connection for a specific room
 * @param {string} roomId - The chat room ID
 * @returns {Object} - Object with stores and methods for interacting with WebSocket
 */
export function createChatConnection(roomId) {
  if (!browser || !roomId) {
    return {
      messages: writable([]),
      status: writable('disconnected'),
      sendMessage: () => console.warn('WebSocket not available in server environment'),
      reconnect: () => console.warn('WebSocket not available in server environment'),
      close: () => {}
    };
  }
  
  // Create stores for messages and connection status
  const messages = writable([]);
  const status = writable('connecting');
  
  let socket = null;
  let reconnectAttempts = 0;
  let reconnectTimer = null;
  let pingTimer = null;
  let isClosing = false;
  
  function connect() {
    try {
      status.set('connecting');
      
      // Get authentication token
      let accessToken = '';
      try {
        accessToken = localStorage.getItem('accessToken') || '';
        // Ensure token is properly URL encoded
        accessToken = encodeURIComponent(accessToken);
      } catch (e) {
        console.error('Error accessing localStorage:', e);
      }
      
      // Create WebSocket connection with authentication token
      const wsUrl = `${WS_BASE_URL}/chat/${roomId}/?token=${accessToken}`;
      console.log(`Connecting to chat WebSocket: ${wsUrl}`);
      socket = new WebSocket(wsUrl);
      
      // Connection opened handler
      socket.addEventListener('open', (event) => {
        console.log(`WebSocket connection opened for chat room ${roomId}`);
        status.set('connected');
        reconnectAttempts = 0; // Reset reconnect attempts on successful connection
        
        // Setup ping interval to keep connection alive
        if (pingTimer) clearInterval(pingTimer);
        pingTimer = setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);
      });
      
      // Connection error handler
      socket.addEventListener('error', (event) => {
        console.error(`WebSocket error for chat room ${roomId}:`, event);
        status.set('error');
      });
      
      // Connection closed handler
      socket.addEventListener('close', (event) => {
        console.log(`WebSocket connection closed for chat room ${roomId}. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}, Was Clean: ${event.wasClean}`);
        status.set('disconnected');
        
        // Clear ping timer
        if (pingTimer) {
          clearInterval(pingTimer);
          pingTimer = null;
        }
        
        // Handle disconnection with exponential backoff
        if (!isClosing) {
          handleDisconnect();
        }
      });
      
      // Message handler with improved error handling
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types
          if (data.type === 'pong') {
            // Heartbeat response, no further action needed
            return;
          } else if (data.type === 'error') {
            console.error('WebSocket error message:', data.error);
            notificationStore.error(`Chat error: ${data.error}`);
            
            // Handle client-side message error if client_id is provided
            if (data.client_id) {
              messages.update(currentMessages => {
                return currentMessages.map(m => {
                  if (m.client_id === data.client_id) {
                    return { ...m, error: true, errorMessage: data.error };
                  }
                  return m;
                });
              });
            }
            return;
          } else if (data.type === 'system') {
            // System messages (join/leave notifications)
            messages.update(currentMessages => {
              return [...currentMessages, {
                id: `system-${Date.now()}`,
                type: 'system',
                message: data.message,
                event: data.event,
                timestamp: data.timestamp || new Date().toISOString()
              }];
            });
            return;
          } else if (data.type === 'message') {
            // Handle message confirmation (convert pending to confirmed)
            let userData = null;
            try {
              userData = authStore?.user || JSON.parse(localStorage.getItem('user')) || {};
            } catch (e) {
              console.error('Error accessing user data:', e);
            }
            
            const isConfirmation = data.client_id && userData && data.user_id === userData.id;
            
            messages.update(currentMessages => {
              // If this is a confirmation of a pending message
              if (isConfirmation) {
                const hasPendingMessage = currentMessages.some(m => m.client_id === data.client_id);
                
                if (hasPendingMessage) {
                  return currentMessages.map(msg => {
                    if (msg.client_id === data.client_id) {
                      return {
                        ...msg,
                        id: data.id || msg.id,
                        pending: false,
                        confirmed: true
                      };
                    }
                    return msg;
                  });
                }
              }
              
              // Check if this message already exists (by id if available)
              if (data.id) {
                const exists = currentMessages.some(m => m.id === data.id);
                if (exists) return currentMessages;
              }
              
              // Add timestamp if not present
              if (!data.timestamp) {
                data.timestamp = new Date().toISOString();
              }
              
              return [...currentMessages, {
                ...data,
                pending: false,
                type: 'message'
              }];
            });
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      });
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      status.set('error');
      handleDisconnect();
    }
  }
  
  function handleDisconnect() {
    if (reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      console.log(`Attempting to reconnect (${reconnectAttempts}/${WS_MAX_RECONNECT_ATTEMPTS})...`);
      
      // Clear any existing reconnect timer
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      
      // Use exponential backoff with jitter for reconnection
      const delay = WS_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
      const jitter = Math.random() * 1000; // Add up to 1 second of jitter
      reconnectTimer = setTimeout(connect, delay + jitter);
      
      // Update status to show reconnecting
      status.set('reconnecting');
    } else {
      console.log(`Max reconnection attempts (${WS_MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`);
      status.set('failed');
      
      // Notify user about the connection failure
      notificationStore.error('Chat connection lost. Please refresh the page or click reconnect.');
    }
  }
  
  // Initialize the connection
  connect();
  
  // Return public interface
  return {
    messages,
    status,
    
    /**
     * Send a message via WebSocket
     * @param {string} message - Message content
     * @param {string} userId - Sender user ID
     */
    sendMessage: (message, userId) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        const clientId = `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const messageData = {
          type: 'message',
          message,
          user_id: userId,
          timestamp: new Date().toISOString(),
          client_id: clientId
        };
        
        socket.send(JSON.stringify(messageData));
        
        // Try to get user data
        let userData = null;
        try {
          userData = authStore?.user || JSON.parse(localStorage.getItem('user')) || {};
        } catch (e) {
          console.error('Error accessing localStorage:', e);
        }
        
        // Optimistically add message to store
        messages.update(currentMessages => [
          ...currentMessages, 
          {
            id: `pending-${clientId}`,
            client_id: clientId,
            type: 'message',
            message,
            user_id: userId,
            username: userData?.first_name || userData?.email?.split('@')[0] || 'You',
            timestamp: new Date().toISOString(),
            pending: true
          }
        ]);
        
        return clientId;
      } else {
        notificationStore.error('Cannot send message: Connection lost. Trying to reconnect...');
        handleDisconnect(); // Try to reconnect
        throw new Error('WebSocket not connected');
      }
    },
    
    /**
     * Check if WebSocket is connected
     * @returns {boolean} - True if connected, false otherwise
     */
    isConnected: () => {
      return socket && socket.readyState === WebSocket.OPEN;
    },
    
    /**
     * Manually attempt to reconnect
     */
    reconnect: () => {
      if (socket && socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING) {
        reconnectAttempts = 0; // Reset counter for manual reconnect
        connect();
      }
    },
    
    /**
     * Send any message via WebSocket
     * @param {object} data - Data to send
     */
    send: (data) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        notificationStore.error('Cannot send data: Connection lost');
        throw new Error('WebSocket not connected');
      }
    },
    
    /**
     * Close the WebSocket connection
     */
    close: () => {
      isClosing = true;
      
      // Clear timers
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      
      if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
      }
      
      // Close socket
      if (socket) {
        socket.close();
        socket = null;
      }
      
      status.set('disconnected');
    }
  };
}


/**
 * Create an auction WebSocket connection for a specific auction
 * @param {string} auctionId - The auction ID
 * @returns {Object} - Object with stores and methods for interacting with WebSocket
 */
export function createAuctionConnection(auctionId) {
  if (!browser || !auctionId) {
    return {
      updates: writable([]),
      status: writable('disconnected'),
      reconnect: () => console.warn('WebSocket not available in server environment'),
      isConnected: () => false,
      close: () => {}
    };
  }
  
  // Create stores for updates and connection status
  const updates = writable([]);
  const status = writable('connecting');
  
  let socket = null;
  let reconnectAttempts = 0;
  let reconnectTimer = null;
  let pingTimer = null;
  let isClosing = false;
  
  function connect() {
    try {
      status.set('connecting');
      
      // Get authentication token and ensure it's properly formatted
      let accessToken = '';
      try {
        accessToken = localStorage.getItem('accessToken') || '';
        // Ensure token is properly URL encoded to prevent 400 Bad Request errors
        accessToken = encodeURIComponent(accessToken);
      } catch (e) {
        console.error('Error accessing localStorage:', e);
      }
      
      // Create WebSocket connection with authentication token
      const wsUrl = `${WS_BASE_URL}/auction/${auctionId}/?token=${accessToken}`;
      console.log(`Connecting to auction WebSocket: ${wsUrl}`);
      socket = new WebSocket(wsUrl);
      
      // Connection opened handler
      socket.addEventListener('open', (event) => {
        console.log(`Auction WebSocket connection opened for auction ${auctionId}`);
        status.set('connected');
        reconnectAttempts = 0; // Reset reconnect attempts on successful connection
        
        // Setup ping interval to keep connection alive
        if (pingTimer) clearInterval(pingTimer);
        pingTimer = setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);
      });
      
      // Connection error handler with more detailed logging
      socket.addEventListener('error', (event) => {
        console.error(`Auction WebSocket error for auction ${auctionId}:`, event);
        status.set('error');
      });
      
      // Connection closed handler with more detailed logging
      socket.addEventListener('close', (event) => {
        console.log(`Auction WebSocket connection closed for auction ${auctionId}. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}, Was Clean: ${event.wasClean}`);
        status.set('disconnected');
        
        // Clear ping timer
        if (pingTimer) {
          clearInterval(pingTimer);
          pingTimer = null;
        }
        
        // Handle disconnection with exponential backoff
        if (!isClosing) {
          handleDisconnect();
        }
      });
      
      // Message handler with improved error handling
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'pong') {
            // Heartbeat response, no further action needed
            return;
          } else if (data.type === 'error') {
            console.error('WebSocket error message:', data.error);
            notificationStore.error(`Auction error: ${data.error}`);
            return;
          } else if (data.type === 'initial_state' || data.type === 'auction_state') {
            // Initial auction state or state update
            console.log('Received auction state update');
          } else if (data.type === 'auction_update') {
            // Update the updates store with this new update
            updates.update(currentUpdates => {
              // Add the new update at the beginning of the array
              return [data, ...currentUpdates];
            });
          }
        } catch (error) {
          console.error('Error parsing auction WebSocket message:', error);
        }
      });
    } catch (error) {
      console.error('Error creating auction WebSocket connection:', error);
      status.set('error');
      handleDisconnect();
    }
  }
  
  function handleDisconnect() {
    if (reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      console.log(`Attempting to reconnect (${reconnectAttempts}/${WS_MAX_RECONNECT_ATTEMPTS})...`);
      
      // Clear any existing reconnect timer
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      
      // Use exponential backoff with jitter for reconnection
      const delay = WS_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
      const jitter = Math.random() * 1000;
      reconnectTimer = setTimeout(connect, delay + jitter);
      
      // Update status to show reconnecting
      status.set('reconnecting');
    } else {
      console.log(`Max reconnection attempts (${WS_MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`);
      status.set('failed');
    }
  }
  
  // Initialize the connection
  connect();
  
  // Return public interface
  return {
    updates,
    status,
    
    /**
     * Request current auction state
     */
    getState: () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          action: 'get_state'
        }));
      } else {
        console.warn('Cannot request auction state: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Check if WebSocket is connected
     * @returns {boolean} - True if connected, false otherwise
     */
    isConnected: () => {
      return socket && socket.readyState === WebSocket.OPEN;
    },
    
    /**
     * Manually attempt to reconnect
     * @returns {boolean} - True if reconnection was initiated, false otherwise
     */
    reconnect: () => {
      if (socket && socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING) {
        reconnectAttempts = 0; // Reset counter for manual reconnect
        connect();
        return true;
      }
      return false;
    },
    
    /**
     * Send any message via WebSocket
     * @param {object} data - Data to send
     */
    send: (data) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        console.warn('Cannot send message: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Close the WebSocket connection
     */
    close: () => {
      isClosing = true;
      
      // Clear timers
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      
      if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
      }
      
      // Close socket
      if (socket) {
        socket.close();
        socket = null;
      }
      
      status.set('disconnected');
    }
  };
}

/**
 * Create a bidding WebSocket connection for a specific auction
 * @param {string} auctionId - The auction ID
 * @returns {Object} - Object with stores and methods for interacting with WebSocket
 */
export function createBiddingConnection(auctionId) {
  if (!browser || !auctionId) {
    return {
      bids: writable([]),
      status: writable('disconnected'),
      placeBid: () => console.warn('WebSocket not available in server environment'),
      reconnect: () => console.warn('WebSocket not available in server environment'),
      isConnected: () => false,
      close: () => {}
    };
  }
  
  // Create stores for bids and connection status
  const bids = writable([]);
  const status = writable('connecting');
  
  let socket = null;
  let reconnectAttempts = 0;
  let reconnectTimer = null;
  let pingTimer = null;
  let isClosing = false;
  
  function connect() {
    try {
      status.set('connecting');
      
      // Get authentication token and ensure it's properly formatted
      let accessToken = '';
      try {
        accessToken = localStorage.getItem('accessToken') || '';
        // Ensure token is properly URL encoded to prevent 400 Bad Request errors
        accessToken = encodeURIComponent(accessToken);
      } catch (e) {
        console.error('Error accessing localStorage:', e);
      }
      
      // Create WebSocket connection with authentication token
      const wsUrl = `${WS_BASE_URL}/bidding/${auctionId}/?token=${accessToken}`;
      console.log(`Connecting to bidding WebSocket: ${wsUrl}`);
      socket = new WebSocket(wsUrl);
      
      // Connection opened handler
      socket.addEventListener('open', (event) => {
        console.log(`Bidding WebSocket connection opened for auction ${auctionId}`);
        status.set('connected');
        reconnectAttempts = 0; // Reset reconnect attempts on successful connection
        
        // Setup ping interval to keep connection alive
        if (pingTimer) clearInterval(pingTimer);
        pingTimer = setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, WS_PING_INTERVAL);
      });
      
      // Connection error handler with more detailed logging
      socket.addEventListener('error', (event) => {
        console.error(`Bidding WebSocket error for auction ${auctionId}:`, event);
        status.set('error');
      });
      
      // Connection closed handler with more detailed logging
      socket.addEventListener('close', (event) => {
        console.log(`Bidding WebSocket connection closed for auction ${auctionId}. Code: ${event.code}, Reason: ${event.reason || 'No reason provided'}, Was Clean: ${event.wasClean}`);
        status.set('disconnected');
        
        // Clear ping timer
        if (pingTimer) {
          clearInterval(pingTimer);
          pingTimer = null;
        }
        
        // Handle disconnection with exponential backoff
        if (!isClosing) {
          handleDisconnect();
        }
      });
      
      // Message handler with improved error handling
      socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'pong') {
            // Heartbeat response, no further action needed
            return;
          } else if (data.type === 'error') {
            console.error('WebSocket error message:', data.error);
            notificationStore.error(`Bidding error: ${data.error}`);
            return;
          } else if (data.type === 'new_bid') {
            // Update bids store
            bids.update(currentBids => {
              // Check if this bid already exists in the array
              if (data.bid && data.bid.id) {
                const exists = currentBids.some(b => b.id === data.bid.id);
                if (!exists) {
                  // Sort bids by amount (descending)
                  const newBids = [data.bid, ...currentBids].sort((a, b) => b.amount - a.amount);
                  return newBids;
                }
              }
              return currentBids;
            });
          }
        } catch (error) {
          console.error('Error parsing bidding WebSocket message:', error);
        }
      });
    } catch (error) {
      console.error('Error creating bidding WebSocket connection:', error);
      status.set('error');
      handleDisconnect();
    }
  }
  
  function handleDisconnect() {
    if (reconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      console.log(`Attempting to reconnect (${reconnectAttempts}/${WS_MAX_RECONNECT_ATTEMPTS})...`);
      
      // Clear any existing reconnect timer
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      
      // Use exponential backoff with jitter for reconnection
      const delay = WS_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
      const jitter = Math.random() * 1000;
      reconnectTimer = setTimeout(connect, delay + jitter);
      
      // Update status to show reconnecting
      status.set('reconnecting');
    } else {
      console.log(`Max reconnection attempts (${WS_MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`);
      status.set('failed');
    }
  }
  
  // Initialize the connection
  connect();
  
  // Return public interface
  return {
    bids,
    status,
    
    /**
     * Place a bid via WebSocket
     * @param {Object} bidData - Bid data (amount, auto_bid_limit, bidder)
     */
    placeBid: (bidData) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          action: 'place_bid',
          amount: bidData.amount,
          auto_bid_limit: bidData.auto_bid_limit,
          user_id: bidData.bidder
        }));
      } else {
        console.warn('Cannot place bid: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
        throw new Error('WebSocket not connected');
      }
    },
    
    /**
     * Check if WebSocket is connected
     * @returns {boolean} - True if connected, false otherwise
     */
    isConnected: () => {
      return socket && socket.readyState === WebSocket.OPEN;
    },
    
    /**
     * Manually attempt to reconnect
     * @returns {boolean} - True if reconnection was initiated, false otherwise
     */
    reconnect: () => {
      if (socket && socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING) {
        reconnectAttempts = 0; // Reset counter for manual reconnect
        connect();
        return true;
      }
      return false;
    },
    
    /**
     * Send any message via WebSocket
     * @param {object} data - Data to send
     */
    send: (data) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        console.warn('Cannot send message: WebSocket not connected');
        handleDisconnect(); // Try to reconnect
      }
    },
    
    /**
     * Close the WebSocket connection
     */
    close: () => {
      isClosing = true;
      
      // Clear timers
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      
      if (pingTimer) {
        clearInterval(pingTimer);
        pingTimer = null;
      }
      
      // Close socket
      if (socket) {
        socket.close();
        socket = null;
      }
      
      status.set('disconnected');
    }
  };
}

export default {
  createDashboardConnection,
  createNotificationConnection,
  createChatConnection, 
  createAuctionConnection,
  createBiddingConnection
};