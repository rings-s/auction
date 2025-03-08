// /src/lib/api/notificationApi.js
import { api } from '$lib/api';
import { browser } from '$app/environment';

/**
 * Notification API calls
 */
export const notificationApi = {
  /**
   * List all notifications for the current user
   * @param {Object} options - Optional parameters
   * @returns {Promise<Object>} - API response with notifications
   */
  list: (options = {}) => {
    if (browser) console.log('Fetching notifications with params:', options.params || {});
    return api.request('/base/notifications/', {
      method: 'GET',
      params: options.params
    });
  },

  /**
   * Get a single notification by ID
   * @param {string} notificationId - Notification ID
   * @returns {Promise<Object>} - API response with notification
   */
  getById: (notificationId) => {
    if (browser) console.log('Fetching notification details:', notificationId);
    return api.request(`/base/notifications/${notificationId}/`, {
      method: 'GET',
    });
  },

  /**
   * Mark a notification as read
   * @param {string} notificationId - Notification ID
   * @returns {Promise<Object>} - API response
   */
  markAsRead: (notificationId) => {
    if (browser) console.log('Marking notification as read:', notificationId);
    return api.request(`/base/notifications/${notificationId}/read/`, {
      method: 'POST',
    });
  },

  /**
   * Mark all notifications as read
   * @returns {Promise<Object>} - API response
   */
  markAllAsRead: () => {
    if (browser) console.log('Marking all notifications as read');
    return api.request('/base/notifications/read-all/', {
      method: 'POST',
    });
  },

  /**
   * Delete a notification
   * @param {string} notificationId - Notification ID
   * @returns {Promise<Object>} - API response
   */
  delete: (notificationId) => {
    if (browser) console.log('Deleting notification:', notificationId);
    return api.request(`/base/notifications/${notificationId}/`, {
      method: 'DELETE',
    });
  },

  /**
   * Get notification settings
   * @returns {Promise<Object>} - API response with settings
   */
  getSettings: () => {
    if (browser) console.log('Fetching notification settings');
    return api.request('/base/notifications/settings/', {
      method: 'GET',
    });
  },

  /**
   * Update notification settings
   * @param {Object} settings - Settings to update
   * @returns {Promise<Object>} - API response
   */
  updateSettings: (settings) => {
    if (browser) console.log('Updating notification settings');
    return api.request('/base/notifications/settings/', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  },

  /**
   * Get unread notification count
   * @returns {Promise<Object>} - API response with count
   */
  getUnreadCount: () => {
    if (browser) console.log('Fetching unread notification count');
    return api.request('/base/notifications/unread-count/', {
      method: 'GET',
    });
  }
};

// Ensure the notification API is properly attached to the main API object
if (api && !api.notification) {
  api.notification = notificationApi;
}

export default notificationApi;