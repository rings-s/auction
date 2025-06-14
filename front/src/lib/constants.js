// front/src/lib/constants.js

// Use environment variables with fallbacks
export const VITE_API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8451/api";
export const VITE_WS_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8451/ws";


// Ensure trailing slashes are consistent
const normalizeUrl = (url) => url.endsWith('/') ? url : url + '/';

// Authentication endpoints
export const AUTH_ENDPOINTS = {
  BASE: `${VITE_API_URL}/accounts`,
  LOGIN: `${VITE_API_URL}/accounts/login/`,
  LOGOUT: `${VITE_API_URL}/accounts/logout/`,
  REGISTER: `${VITE_API_URL}/accounts/register/`,
  REFRESH_TOKEN: `${VITE_API_URL}/accounts/token/refresh/`,
  VERIFY_EMAIL: `${VITE_API_URL}/accounts/verify-email/`,
  PROFILE: `${VITE_API_URL}/accounts/profile/`,
  CHANGE_PASSWORD: `${VITE_API_URL}/accounts/password/change/`,
  REQUEST_PASSWORD_RESET: `${VITE_API_URL}/accounts/password/reset/request/`,
  CONFIRM_PASSWORD_RESET: `${VITE_API_URL}/accounts/password/reset/confirm/`,
};

// Property endpoints
export const PROPERTY_ENDPOINTS = {
  BASE: `${VITE_API_URL}/properties/`,
  LIST: `${VITE_API_URL}/properties/`,
  DETAIL: function(id) { return `${VITE_API_URL}/properties/${id}/`; },
  BY_SLUG: function(slug) { return `${VITE_API_URL}/properties/${encodeURIComponent(slug)}/`; },
  CONTACT_OWNER: function(id) { return `${VITE_API_URL}/properties/${id}/contact/`; },
  STATS: `${VITE_API_URL}/property-stats/`,
};

// Auction endpoints
export const AUCTION_ENDPOINTS = {
  BASE: `${VITE_API_URL}/auctions/`,
  LIST: `${VITE_API_URL}/auctions/`,
  DETAIL: function(id) { return `${VITE_API_URL}/auctions/${id}/`; },
  BY_SLUG: function(slug) { return `${VITE_API_URL}/auctions/${encodeURIComponent(slug)}/`; },
  STATUS: function(id) { return `${VITE_API_URL}/auctions/${id}/status/`; },
  REGISTER: function(id) { return `${VITE_API_URL}/auctions/${id}/register/`; },
  WATCH: function(id) { return `${VITE_API_URL}/auctions/${id}/watch/`; },
  UNWATCH: function(id) { return `${VITE_API_URL}/auctions/${id}/watch/`; },
};

// Bid endpoints
export const BID_ENDPOINTS = {
  BASE: `${VITE_API_URL}/bids/`,
  LIST: `${VITE_API_URL}/bids/`,
  DETAIL: function(id) { return `${VITE_API_URL}/bids/${id}/`; },
  USER_BIDS: `${VITE_API_URL}/bids/?bidder=current`,
  BY_AUCTION: function(auctionId) { return `${VITE_API_URL}/bids/?auction=${auctionId}&ordering=-bid_time`; },
};

// Media endpoints
export const MEDIA_ENDPOINTS = {
  BASE: `${VITE_API_URL}/media/`,
  LIST: `${VITE_API_URL}/media/`,
  DETAIL: function(id) { return `${VITE_API_URL}/media/${id}/`; },
  DELETE: function(id) { return `${VITE_API_URL}/media/${id}/`; },
  UPDATE: function(id) { return `${VITE_API_URL}/media/${id}/`; },
};

// Room endpoints
export const ROOM_ENDPOINTS = {
  BASE: `${VITE_API_URL}/rooms/`,
  LIST: `${VITE_API_URL}/rooms/`,
  DETAIL: function(id) { return `${VITE_API_URL}/rooms/${id}/`; },
};

// Dashboard endpoints
export const DASHBOARD_ENDPOINTS = {
  BASE: `${VITE_API_URL}/dashboard/`,
  USER_STATS: `${VITE_API_URL}/dashboard/`,
  SYSTEM_STATS: `${VITE_API_URL}/dashboard/system/`,
  ACTIVITY: `${VITE_API_URL}/dashboard/activity/`,
  PROPERTIES: `${VITE_API_URL}/dashboard/properties/`,
  AUCTIONS: `${VITE_API_URL}/dashboard/auctions/`,
  BIDS: `${VITE_API_URL}/dashboard/bids/`,
};

// Message endpoints
export const MESSAGE_ENDPOINTS = {
  BASE: `${VITE_API_URL}/messages/`,
  LIST: `${VITE_API_URL}/messages/`,
  DETAIL: function(id) { return `${VITE_API_URL}/messages/${id}/`; },
  REPLY: function(id) { return `${VITE_API_URL}/messages/${id}/reply/`; },
  THREAD: function(threadId) { return `${VITE_API_URL}/messages/thread/${threadId}/`; },
  STATS: `${VITE_API_URL}/messages/stats/`,
};

// User endpoints
export const USER_ENDPOINTS = {
  BASE: `${VITE_API_URL}/user/`,
  PROFILE: `${VITE_API_URL}/user/`,
  BY_ID: function(userId) { return `${VITE_API_URL}/users/${userId}/`; },
};

// WebSocket endpoints
export const WS_ENDPOINTS = {
  AUCTION: function(auctionId) { return `${VITE_WS_URL}/auction/${auctionId}/`; },
  NOTIFICATIONS: `${VITE_WS_URL}/notifications/`,
  MESSAGES: `${VITE_WS_URL}/messages/`,
};

// Combined API endpoints object for backward compatibility
export const API_ENDPOINTS = {
  // Authentication
  LOGIN: AUTH_ENDPOINTS.LOGIN,
  LOGOUT: AUTH_ENDPOINTS.LOGOUT,
  REGISTER: AUTH_ENDPOINTS.REGISTER,
  REFRESH: AUTH_ENDPOINTS.REFRESH_TOKEN,
  VERIFY_EMAIL: AUTH_ENDPOINTS.VERIFY_EMAIL,
  PROFILE: AUTH_ENDPOINTS.PROFILE,
  
  // Properties
  PROPERTIES: PROPERTY_ENDPOINTS.LIST,
  PROPERTY_DETAIL: PROPERTY_ENDPOINTS.DETAIL,
  PROPERTY_BY_SLUG: PROPERTY_ENDPOINTS.BY_SLUG,
  
  // Auctions
  AUCTIONS: AUCTION_ENDPOINTS.LIST,
  AUCTION_DETAIL: AUCTION_ENDPOINTS.DETAIL,
  AUCTION_BY_SLUG: AUCTION_ENDPOINTS.BY_SLUG,
  AUCTION_STATUS: AUCTION_ENDPOINTS.STATUS,
  
  // Bids
  BIDS: BID_ENDPOINTS.LIST,
  BID_DETAIL: BID_ENDPOINTS.DETAIL,
  
  // Media
  MEDIA: MEDIA_ENDPOINTS.LIST,
  MEDIA_DETAIL: MEDIA_ENDPOINTS.DETAIL,
  
  // Dashboard
  DASHBOARD: DASHBOARD_ENDPOINTS.BASE,
  DASHBOARD_STATS: DASHBOARD_ENDPOINTS.USER_STATS,
  DASHBOARD_ACTIVITY: DASHBOARD_ENDPOINTS.ACTIVITY,
  
  // Messages
  MESSAGES: MESSAGE_ENDPOINTS.LIST,
  MESSAGE_DETAIL: MESSAGE_ENDPOINTS.DETAIL,
  
  // Users
  USER: USER_ENDPOINTS.BASE,
  USER_BY_ID: USER_ENDPOINTS.BY_ID,
};

// Content types for media uploads
export const CONTENT_TYPES = {
  PROPERTY: 'base.property',
  ROOM: 'base.room',
  AUCTION: 'base.auction',
  USER: 'accounts.user',
};

// Media types
export const MEDIA_TYPES = {
  IMAGE: 'image',
  VIDEO: 'video',
  DOCUMENT: 'document',
  OTHER: 'other',
};

// HTTP status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
};

// Request timeouts (in milliseconds)
export const TIMEOUTS = {
  DEFAULT: 30000, // 30 seconds
  UPLOAD: 300000, // 5 minutes for file uploads
  WEBSOCKET_RECONNECT: 5000, // 5 seconds
};

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
};

// Application-specific constants
export const APP_CONFIG = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_IMAGE_FORMATS: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
  SUPPORTED_VIDEO_FORMATS: ['video/mp4', 'video/webm', 'video/ogg'],
  SUPPORTED_DOCUMENT_FORMATS: [
    'application/pdf', 
    'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ],
  
  // Retry configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000, // 1 second base delay
  
  // Cache configuration
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
};

// Environment-specific settings
export const ENV_CONFIG = {
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
  BASE_URL: import.meta.env.BASE_URL || '/',
};

// Helper functions for common operations
export const API_HELPERS = {
  // Build query string from object
  buildQueryString: function(params) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(function([key, value]) {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    return queryParams.toString();
  },
  
  // Get full URL with query parameters
  buildUrl: function(baseUrl, params) {
    if (!params || Object.keys(params).length === 0) {
      return baseUrl;
    }
    const queryString = this.buildQueryString(params);
    return queryString ? `${baseUrl}?${queryString}` : baseUrl;
  },
  
  // Normalize URL to ensure proper format
  normalizeUrl: function(url) {
    return url.endsWith('/') ? url : url + '/';
  }
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Authentication required. Please log in.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
  UPLOAD_ERROR: 'File upload failed. Please try again.',
  CONNECTION_ERROR: 'Connection error. Please check your internet connection.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  LOGOUT_SUCCESS: 'Successfully logged out!',
  REGISTRATION_SUCCESS: 'Registration successful! Please verify your email.',
  EMAIL_VERIFIED: 'Email verified successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  PASSWORD_CHANGED: 'Password changed successfully!',
  PROPERTY_CREATED: 'Property created successfully!',
  PROPERTY_UPDATED: 'Property updated successfully!',
  AUCTION_CREATED: 'Auction created successfully!',
  BID_PLACED: 'Bid placed successfully!',
  MESSAGE_SENT: 'Message sent successfully!',
  FILE_UPLOADED: 'File uploaded successfully!',
};

// Export legacy constants for backward compatibility

// Debug logging in development
if (ENV_CONFIG.IS_DEVELOPMENT) {
  console.log('🔗 API Configuration:', {
    API_BASE_URL: VITE_API_URL,
    WS_BASE_URL: VITE_WS_URL,
    AUTH_ENDPOINTS: AUTH_ENDPOINTS,
    PROPERTY_ENDPOINTS: PROPERTY_ENDPOINTS,
    AUCTION_ENDPOINTS: AUCTION_ENDPOINTS,
    BID_ENDPOINTS: BID_ENDPOINTS,
    MEDIA_ENDPOINTS: MEDIA_ENDPOINTS,
    DASHBOARD_ENDPOINTS: DASHBOARD_ENDPOINTS,
    MESSAGE_ENDPOINTS: MESSAGE_ENDPOINTS,
    WS_ENDPOINTS: WS_ENDPOINTS
  });
}