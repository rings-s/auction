// /src/lib/stores/notificationStore.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Types of notifications
export const NotificationType = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Default timeout in milliseconds
const DEFAULT_TIMEOUT = 5000;

// Generate a unique ID
function generateId() {
  return `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

// Create toast notification store
function createToastStore() {
  const { subscribe, update } = writable([]);

  return {
    subscribe,
    
    /**
     * Add a notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type
     * @param {number} timeout - Auto-dismiss timeout in ms (0 for no auto-dismiss)
     * @returns {string} - Generated notification ID
     */
    add: (message, type = NotificationType.INFO, timeout = DEFAULT_TIMEOUT) => {
      if (!browser) return; // Skip during SSR
      
      const id = generateId();
      const notification = {
        id,
        message,
        type,
        timeout,
        timestamp: new Date(),
      };
      
      update(notifications => [notification, ...notifications]);
      
      if (timeout) {
        setTimeout(() => {
          update(notifications => notifications.filter(n => n.id !== id));
        }, timeout);
      }
      
      return id;
    },
    
    /**
     * Remove a notification by ID
     * @param {string} id - Notification ID
     */
    remove: (id) => {
      if (!browser) return; // Skip during SSR
      update(notifications => notifications.filter(n => n.id !== id));
    },
    
    /**
     * Success notification shorthand
     * @param {string} message - Success message
     * @param {number} timeout - Auto-dismiss timeout
     * @returns {string} - Generated notification ID
     */
    success: (message, timeout = DEFAULT_TIMEOUT) => {
      if (!browser) return; // Skip during SSR
      const store = createToastStore();
      return store.add(message, NotificationType.SUCCESS, timeout);
    },
    
    /**
     * Error notification shorthand
     * @param {string} message - Error message
     * @param {number} timeout - Auto-dismiss timeout
     * @returns {string} - Generated notification ID
     */
    error: (message, timeout = DEFAULT_TIMEOUT) => {
      if (!browser) return; // Skip during SSR
      const store = createToastStore();
      return store.add(message, NotificationType.ERROR, timeout);
    },
    
    /**
     * Warning notification shorthand
     * @param {string} message - Warning message
     * @param {number} timeout - Auto-dismiss timeout
     * @returns {string} - Generated notification ID
     */
    warning: (message, timeout = DEFAULT_TIMEOUT) => {
      if (!browser) return; // Skip during SSR
      const store = createToastStore();
      return store.add(message, NotificationType.WARNING, timeout);
    },
    
    /**
     * Info notification shorthand
     * @param {string} message - Info message
     * @param {number} timeout - Auto-dismiss timeout
     * @returns {string} - Generated notification ID
     */
    info: (message, timeout = DEFAULT_TIMEOUT) => {
      if (!browser) return; // Skip during SSR
      const store = createToastStore();
      return store.add(message, NotificationType.INFO, timeout);
    },
    
    /**
     * Clear all notifications
     */
    clearAll: () => {
      if (!browser) return; // Skip during SSR
      update(() => []);
    },
  };
}

// Create and export the toast notification store
export const notificationStore = createToastStore();

// Create the persistent notifications store (unread notifications)
function createUserNotificationsStore() {
  // Initialize with empty array
  const { subscribe, set, update } = writable([]);
  
  // Derived stores
  const unreadCount = derived({ subscribe }, $notifications => 
    $notifications.filter(n => !n.read).length
  );
  
  return {
    subscribe,
    unreadCount: { subscribe: unreadCount.subscribe },
    
    /**
     * Set all notifications
     * @param {Array} notifications - Array of notification objects
     */
    set,
    
    /**
     * Add a new notification
     * @param {Object} notification - Notification object
     */
    add: (notification) => {
      if (!browser) return; // Skip during SSR
      
      update(notifications => {
        // Check if this notification already exists
        const exists = notifications.some(n => n.id === notification.id);
        if (exists) {
          // Update existing notification
          return notifications.map(n => n.id === notification.id ? { ...n, ...notification } : n);
        } else {
          // Add new notification at the beginning
          return [notification, ...notifications];
        }
      });
      
      // Show a toast for the new notification if we're in a browser
      if (!notification.silent) {
        notificationStore.info(notification.message || notification.title, 5000);
      }
    },
    
    /**
     * Mark a notification as read
     * @param {string} id - Notification ID
     */
    markAsRead: (id) => {
      if (!browser) return; // Skip during SSR
      
      update(notifications => 
        notifications.map(n => n.id === id ? { ...n, read: true } : n)
      );
    },
    
    /**
     * Mark all notifications as read
     */
    markAllAsRead: () => {
      if (!browser) return; // Skip during SSR
      
      update(notifications => 
        notifications.map(n => ({ ...n, read: true }))
      );
    },
    
    /**
     * Remove a notification
     * @param {string} id - Notification ID
     */
    remove: (id) => {
      if (!browser) return; // Skip during SSR
      
      update(notifications => notifications.filter(n => n.id !== id));
    },
    
    /**
     * Get notifications by category
     * @param {string} category - Category to filter by
     * @returns {Array} - Filtered notifications
     */
    getByCategory: (category) => {
      if (!browser) return []; // Return empty array during SSR
      
      let result = [];
      update(notifications => {
        result = notifications.filter(n => n.category === category);
        return notifications;
      });
      return result;
    },
    
    /**
     * Get unread notifications
     * @returns {Array} - Unread notifications
     */
    getUnread: () => {
      if (!browser) return []; // Return empty array during SSR
      
      let result = [];
      update(notifications => {
        result = notifications.filter(n => !n.read);
        return notifications;
      });
      return result;
    },
    
    /**
     * Search notifications by text
     * @param {string} query - Search query
     * @returns {Array} - Matching notifications
     */
    search: (query) => {
      if (!browser) return []; // Return empty array during SSR
      if (!query) return [];
      
      let result = [];
      const lowercaseQuery = query.toLowerCase();
      
      update(notifications => {
        result = notifications.filter(n => 
          (n.title && n.title.toLowerCase().includes(lowercaseQuery)) || 
          (n.message && n.message.toLowerCase().includes(lowercaseQuery))
        );
        return notifications;
      });
      
      return result;
    }
  };
}

// Export the persistent user notifications store
export const userNotificationsStore = createUserNotificationsStore();

// Export combined store for convenience
export const notifications = {
  toast: notificationStore,
  user: userNotificationsStore
};

export default notificationStore;