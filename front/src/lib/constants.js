// front/src/lib/constants.js

// =============================================================================
// ENVIRONMENT CONFIGURATION
// =============================================================================

// Base URLs from environment variables with fallbacks
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8451/api';
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8451/ws';

// Environment detection
export const IS_DEVELOPMENT = import.meta.env.DEV;
export const IS_PRODUCTION = import.meta.env.PROD;

// =============================================================================
// ENDPOINT DEFINITIONS (for frontend components)
// =============================================================================

// Authentication endpoints
export const AUTH_ENDPOINTS = {
	BASE: `${API_BASE_URL}/accounts`,
	LOGIN: `${API_BASE_URL}/accounts/login/`,
	LOGOUT: `${API_BASE_URL}/accounts/logout/`,
	REGISTER: `${API_BASE_URL}/accounts/register/`,
	REFRESH_TOKEN: `${API_BASE_URL}/accounts/token/refresh/`,
	VERIFY_EMAIL: `${API_BASE_URL}/accounts/verify-email/`,
	PROFILE: `${API_BASE_URL}/accounts/profile/`,
	CHANGE_PASSWORD: `${API_BASE_URL}/accounts/password/change/`,
	REQUEST_PASSWORD_RESET: `${API_BASE_URL}/accounts/password/reset/request/`,
	CONFIRM_PASSWORD_RESET: `${API_BASE_URL}/accounts/password/reset/confirm/`
};

// Property endpoints
export const PROPERTY_ENDPOINTS = {
	BASE: `${API_BASE_URL}/properties/`,
	LIST: `${API_BASE_URL}/properties/`,
	DETAIL: function (id) {
		return `${API_BASE_URL}/properties/${id}/`;
	},
	BY_SLUG: function (slug) {
		return `${API_BASE_URL}/properties/${encodeURIComponent(slug)}/`;
	},
	CONTACT_OWNER: function (id) {
		return `${API_BASE_URL}/properties/${id}/contact/`;
	},
	STATS: `${API_BASE_URL}/property-stats/`
};

// Auction endpoints
export const AUCTION_ENDPOINTS = {
	BASE: `${API_BASE_URL}/auctions/`,
	LIST: `${API_BASE_URL}/auctions/`,
	DETAIL: function (id) {
		return `${API_BASE_URL}/auctions/${id}/`;
	},
	BY_SLUG: function (slug) {
		return `${API_BASE_URL}/auctions/${encodeURIComponent(slug)}/`;
	},
	STATUS: function (id) {
		return `${API_BASE_URL}/auctions/${id}/status/`;
	},
	REGISTER: function (id) {
		return `${API_BASE_URL}/auctions/${id}/register/`;
	},
	WATCH: function (id) {
		return `${API_BASE_URL}/auctions/${id}/watch/`;
	},
	UNWATCH: function (id) {
		return `${API_BASE_URL}/auctions/${id}/watch/`;
	}
};

// Bid endpoints
export const BID_ENDPOINTS = {
	BASE: `${API_BASE_URL}/bids/`,
	LIST: `${API_BASE_URL}/bids/`,
	DETAIL: function (id) {
		return `${API_BASE_URL}/bids/${id}/`;
	},
	USER_BIDS: `${API_BASE_URL}/bids/?bidder=current`,
	BY_AUCTION: function (auctionId) {
		return `${API_BASE_URL}/bids/?auction=${auctionId}&ordering=-bid_time`;
	}
};

// Media endpoints
export const MEDIA_ENDPOINTS = {
	BASE: `${API_BASE_URL}/media/`,
	LIST: `${API_BASE_URL}/media/`,
	DETAIL: function (id) {
		return `${API_BASE_URL}/media/${id}/`;
	},
	DELETE: function (id) {
		return `${API_BASE_URL}/media/${id}/`;
	},
	UPDATE: function (id) {
		return `${API_BASE_URL}/media/${id}/`;
	}
};

// Dashboard endpoints
export const DASHBOARD_ENDPOINTS = {
	BASE: `${API_BASE_URL}/dashboard/`,
	USER_STATS: `${API_BASE_URL}/dashboard/`,
	SYSTEM_STATS: `${API_BASE_URL}/dashboard/system/`,
	ACTIVITY: `${API_BASE_URL}/dashboard/activity/`,
	PROPERTIES: `${API_BASE_URL}/dashboard/properties/`,
	AUCTIONS: `${API_BASE_URL}/dashboard/auctions/`,
	BIDS: `${API_BASE_URL}/dashboard/bids/`
};

// Message endpoints
export const MESSAGE_ENDPOINTS = {
	BASE: `${API_BASE_URL}/messages/`,
	LIST: `${API_BASE_URL}/messages/`,
	DETAIL: function (id) {
		return `${API_BASE_URL}/messages/${id}/`;
	},
	REPLY: function (id) {
		return `${API_BASE_URL}/messages/${id}/reply/`;
	},
	THREAD: function (threadId) {
		return `${API_BASE_URL}/messages/thread/${threadId}/`;
	},
	STATS: `${API_BASE_URL}/messages/stats/`
};

// WebSocket endpoints
export const WS_ENDPOINTS = {
	AUCTION: function (auctionId) {
		return `${WS_BASE_URL}/auctions/${auctionId}/`;
	},
	NOTIFICATIONS: `${WS_BASE_URL}/notifications/`,
	MESSAGES: `${WS_BASE_URL}/messages/`
};

// =============================================================================
// CONTENT TYPES FOR MEDIA UPLOADS
// =============================================================================

export const CONTENT_TYPES = {
	PROPERTY: 'base.property',
	ROOM: 'base.room',
	AUCTION: 'base.auction',
	USER: 'accounts.user'
};

// =============================================================================
// MEDIA CONFIGURATION
// =============================================================================

export const MEDIA_TYPES = {
	IMAGE: 'image',
	VIDEO: 'video',
	DOCUMENT: 'document',
	OTHER: 'other'
};

export const MEDIA_CONFIG = {
	MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
	SUPPORTED_IMAGE_FORMATS: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
	SUPPORTED_VIDEO_FORMATS: ['video/mp4', 'video/webm', 'video/ogg'],
	SUPPORTED_DOCUMENT_FORMATS: [
		'application/pdf',
		'application/msword',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
	]
};

// =============================================================================
// HTTP CONFIGURATION
// =============================================================================

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
	INTERNAL_SERVER_ERROR: 500
};

export const REQUEST_CONFIG = {
	DEFAULT_TIMEOUT: 30000, // 30 seconds
	UPLOAD_TIMEOUT: 300000, // 5 minutes for file uploads
	WEBSOCKET_RECONNECT_DELAY: 5000, // 5 seconds
	MAX_RETRIES: 3,
	RETRY_DELAY: 1000 // 1 second base delay
};

// =============================================================================
// PAGINATION
// =============================================================================

export const PAGINATION = {
	DEFAULT_PAGE_SIZE: 20,
	MAX_PAGE_SIZE: 100
};

// =============================================================================
// ERROR MESSAGES
// =============================================================================

export const ERROR_MESSAGES = {
	NETWORK_ERROR: 'Network error. Please check your connection.',
	UNAUTHORIZED: 'Authentication required. Please log in.',
	FORBIDDEN: 'You do not have permission to perform this action.',
	NOT_FOUND: 'The requested resource was not found.',
	SERVER_ERROR: 'Server error. Please try again later.',
	VALIDATION_ERROR: 'Please check your input and try again.',
	SESSION_EXPIRED: 'Your session has expired. Please log in again.',
	UPLOAD_ERROR: 'File upload failed. Please try again.',
	CONNECTION_ERROR: 'Connection error. Please check your internet connection.'
};

// =============================================================================
// SUCCESS MESSAGES
// =============================================================================

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
	FILE_UPLOADED: 'File uploaded successfully!'
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

export const buildQueryString = (params) => {
	const queryParams = new URLSearchParams();
	Object.entries(params).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== '') {
			queryParams.append(key, value);
		}
	});
	return queryParams.toString();
};

export const buildUrl = (baseUrl, params) => {
	if (!params || Object.keys(params).length === 0) {
		return baseUrl;
	}
	const queryString = buildQueryString(params);
	return queryString ? `${baseUrl}?${queryString}` : baseUrl;
};

// =============================================================================
// DEBUG LOGGING (Development only)
// =============================================================================

if (IS_DEVELOPMENT) {
	console.log('🔗 API Configuration:', {
		API_BASE_URL,
		WS_BASE_URL,
		IS_DEVELOPMENT,
		IS_PRODUCTION
	});
}
