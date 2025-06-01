// API endpoints and other constants
export const API_BASE_URL = 'http://localhost:7500/api';

// WebSocket base URL (derived from API_BASE_URL)
export const WS_BASE_URL = 'ws://localhost:7500/ws';

// API endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/accounts/login/`,
  LOGOUT: `${API_BASE_URL}/accounts/logout/`,
  REGISTER: `${API_BASE_URL}/accounts/register/`,
  REFRESH: `${API_BASE_URL}/accounts/token/refresh/`,
  VERIFY_EMAIL: `${API_BASE_URL}/accounts/verify-email/`,
  RESET_PASSWORD: `${API_BASE_URL}/accounts/password/reset/`,
};

export const AUCTION_ENDPOINTS = {
  LIST: `${API_BASE_URL}/auctions/`,
  BIDS: `${API_BASE_URL}/bids/`,
};