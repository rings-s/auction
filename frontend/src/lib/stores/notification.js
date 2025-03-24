// src/lib/stores/notification.js
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { toast } from '$lib/stores/toast';
import { NotificationService } from '$lib/services/websocket';

// Create writable stores for the notification system
export const notifications = writable([]);
export const unreadCount = writable(0);
export const lastNotification = writable(null);
export const connectionStatus = writable('disconnected');

// Limit for notifications to keep in memory
const MAX_NOTIFICATIONS = 100;

// Create a derived store for filtered notifications
export const recentNotifications = derived(
  notifications,
  ($notifications) => $notifications.slice(0, 10)
);

/**
 * Enhanced notification service with improved error handling
 * and better integration with the WebSocket service
 */
const notificationService = {
  // Public stores
  notifications,
  unreadCount,
  lastNotification,
  connectionStatus,
  recentNotifications,
  
  // Private properties
  _userId: null,
  _wsService: null,
  _unsubscribeAuth: null,
  _unsubscribeWs: null,
  _initialized: false,
  _debug: false,
  _authStore: null,
  _isAuthenticated: null,
  
  /**
   * Initialize the notification system
   * @param {Object} options - Configuration options
   */
  init(options = {}) {
    // Only initialize in browser
    if (!browser) return;
    
    this._debug = options.debug || false;
    
    // Avoid double initialization
    if (this._initialized) {
      if (this._debug) {
        console.log('Notification service already initialized');
      }
      return;
    }
    
    if (this._debug) {
      console.log('Initializing notification service');
    }
    
    // Use dynamic import to avoid circular dependencies
    if (browser) {
      // Dynamically import auth store
      import('./auth').then(authModule => {
        this._isAuthenticated = authModule.isAuthenticated;
        this._authStore = authModule.authStore;
        
        // Connect if already authenticated
        if (get(this._isAuthenticated)) {
          const user = this._authStore.getUser();
          if (user && user.id) {
            this.connect(user.id);
          }
        }
        
        // Set up subscription to auth changes
        this._unsubscribeAuth = this._isAuthenticated.subscribe(value => {
          if (value) {
            // User is now authenticated, connect to notifications
            const user = this._authStore.getUser();
            if (user && user.id) {
              this.connect(user.id);
            }
          } else {
            // User logged out, disconnect
            this.disconnect();
            // Clear notifications
            notifications.set([]);
            unreadCount.set(0);
            lastNotification.set(null);
          }
        });
      }).catch(error => {
        console.error('Failed to import auth module:', error);
      });
    }
    
    this._initialized = true;
  },
  
  /**
   * Connect to notification service for a specific user
   * @param {string} userId - User ID to connect with
   */
  connect(userId) {
    if (!browser || !userId) return;
    
    // If already connected to the same user, don't reconnect
    if (this._userId === userId && this._wsService && this._wsService.isConnected()) {
      return;
    }
    
    // Disconnect previous connection if any
    this.disconnect();
    
    this._userId = userId;
    
    try {
      if (this._debug) {
        console.log(`Connecting to notifications for user: ${userId}`);
      }
      
      // Create WebSocket service
      this._wsService = new NotificationService(userId, {
        debug: this._debug,
        onOpen: () => {
          connectionStatus.set('connected');
          if (this._debug) {
            console.log('Notification WebSocket connected');
          }
          
          // Request initial notifications
          this.requestNotifications();
        },
        onClose: (event) => {
          connectionStatus.set('disconnected');
          if (this._debug) {
            console.log('Notification WebSocket disconnected:', event.reason);
          }
        },
        onError: (event) => {
          connectionStatus.set('error');
          console.error('Notification WebSocket error:', event);
        }
      });
      
      // Subscribe to notifications
      this._unsubscribeWs = this._wsService.subscribe(this._handleNotificationMessage.bind(this));
      
    } catch (error) {
      console.error('Failed to connect to notification service:', error);
      connectionStatus.set('error');
    }
  },
  
  /**
   * Disconnect from notification service and clean up
   */
  disconnect() {
    if (this._wsService) {
      if (this._debug) {
        console.log('Disconnecting notification service');
      }
      
      // Unsubscribe from WebSocket
      if (this._unsubscribeWs) {
        this._unsubscribeWs();
        this._unsubscribeWs = null;
      }
      
      // Close WebSocket connection
      this._wsService.close();
      this._wsService = null;
    }
    
    this._userId = null;
    connectionStatus.set('disconnected');
  },
  
  /**
   * Clean up event listeners and connections
   */
  cleanup() {
    if (this._unsubscribeAuth) {
      this._unsubscribeAuth();
      this._unsubscribeAuth = null;
    }
    
    this.disconnect();
    this._initialized = false;
  },
  
  /**
   * Handle notification messages received from WebSocket
   * @private
   * @param {Object} data - Message data
   */
  _handleNotificationMessage(data) {
    try {
      switch (data.type) {
        case 'notifications':
          // Replace notifications with the received list
          notifications.set(data.notifications || []);
          // Update unread count
          unreadCount.set(data.notifications?.filter(n => !n.is_read)?.length || 0);
          break;
          
        case 'new_notification':
          // Add new notification to the top of the list
          notifications.update(current => {
            // Avoid duplicates
            const filtered = current.filter(n => n.id !== data.notification.id);
            const updated = [data.notification, ...filtered];
            
            // Limit the number of notifications in memory
            return updated.slice(0, MAX_NOTIFICATIONS);
          });
          
          // Update unread count
          if (!data.notification.is_read) {
            unreadCount.update(count => count + 1);
          }
          
          // Update last notification
          lastNotification.set(data.notification);
          
          // Show toast if enabled and notification is new
          if (browser && typeof toast !== 'undefined' && !data.notification.is_read) {
            toast.info(data.notification.title, {
              description: data.notification.content,
              action: {
                label: 'View',
                onClick: () => {
                  // Mark as read and navigate if action URL is provided
                  this.markAsRead(data.notification.id);
                  if (data.notification.action_url) {
                    window.location.href = data.notification.action_url;
                  }
                }
              }
            });
          }
          break;
          
        case 'notification_read':
          // Mark specific notification as read
          notifications.update(items => 
            items.map(item => 
              item.id === data.notification_id 
                ? { ...item, is_read: true, read_at: new Date().toISOString() }
                : item
            )
          );
          
          // Update unread count
          unreadCount.update(count => Math.max(0, count - 1));
          break;
          
        case 'all_read':
          // Mark all notifications as read
          notifications.update(items => 
            items.map(item => ({ 
              ...item, 
              is_read: true, 
              read_at: item.read_at || new Date().toISOString() 
            }))
          );
          
          // Reset unread count
          unreadCount.set(0);
          break;
          
        case 'notification_deleted':
          // Remove deleted notification
          notifications.update(items => 
            items.filter(item => item.id !== data.notification_id)
          );
          
          // Update unread count if needed
          unreadCount.update(count => {
            const currentNotifications = get(notifications);
            return currentNotifications.filter(n => !n.is_read).length;
          });
          break;
          
        case 'unread_count':
          // Update unread count directly
          unreadCount.set(data.count);
          break;
          
        default:
          if (this._debug) {
            console.log('Unknown notification message type:', data.type, data);
          }
      }
    } catch (error) {
      console.error('Error handling notification message:', error, data);
    }
  },
  
  /**
   * Mark a notification as read
   * @param {string} notificationId - ID of the notification to mark as read
   * @returns {Promise} Promise resolving when complete
   */
  markAsRead(notificationId) {
    if (!this._wsService) {
      return Promise.reject(new Error('Notification service not connected'));
    }
    
    // Optimistically update UI immediately
    notifications.update(items => 
      items.map(item => 
        item.id === notificationId 
          ? { ...item, is_read: true, read_at: new Date().toISOString() }
          : item
      )
    );
    
    // Recalculate unread count
    unreadCount.update(count => {
      const currentNotifications = get(notifications);
      return currentNotifications.filter(n => !n.is_read).length;
    });
    
    // Send to server
    return this._wsService.markRead(notificationId);
  },
  
  /**
   * Mark all notifications as read
   * @returns {Promise} Promise resolving when complete
   */
  markAllAsRead() {
    if (!this._wsService) {
      return Promise.reject(new Error('Notification service not connected'));
    }
    
    // Optimistically update UI immediately
    notifications.update(items => 
      items.map(item => ({ 
        ...item, 
        is_read: true, 
        read_at: item.read_at || new Date().toISOString() 
      }))
    );
    
    // Reset unread count
    unreadCount.set(0);
    
    // Send to server
    return this._wsService.markAllRead();
  },
  
  /**
   * Mark a notification as displayed (viewed)
   * @param {string} notificationId - ID of the notification
   * @returns {Promise} Promise resolving when complete
   */
  markAsDisplayed(notificationId) {
    if (!this._wsService) {
      return Promise.reject(new Error('Notification service not connected'));
    }
    
    return this._wsService.markDisplayed(notificationId);
  },
  
  /**
   * Request notifications from the server
   * @param {number} limit - Maximum number of notifications to retrieve
   * @param {number} offset - Pagination offset
   * @returns {Promise} Promise resolving when complete
   */
  requestNotifications(limit = 50, offset = 0) {
    if (!this._wsService) {
      return Promise.reject(new Error('Notification service not connected'));
    }
    
    return this._wsService.getNotifications(limit, offset);
  },
  
  /**
   * Request unread count from the server
   * @returns {Promise} Promise resolving when complete
   */
  requestUnreadCount() {
    if (!this._wsService) {
      return Promise.reject(new Error('Notification service not connected'));
    }
    
    return this._wsService.getUnreadCount();
  },
  
  /**
   * Get connection status
   * @returns {Object} Current connection status
   */
  getStatus() {
    return this._wsService ? this._wsService.getStatus() : { status: 'disconnected' };
  }
};

// Auto-initialize notifications in browser
if (browser) {
  // Delay initialization to avoid circular dependency issues
  setTimeout(() => {
    notificationService.init();
  }, 0);
}

export default notificationService;