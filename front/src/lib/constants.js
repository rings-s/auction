// front/src/lib/constants.js
// Development URLs - localhost
export const VITE_API_URL = "http://localhost:8451/api";
export const VITE_WS_URL = "ws://localhost:8451/ws";
export const API_BASE_URL = VITE_API_URL;
export const WS_BASE_URL = VITE_WS_URL;

export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/accounts/login/`,
  LOGOUT: `${API_BASE_URL}/accounts/logout/`,
  REGISTER: `${API_BASE_URL}/accounts/register/`,
  REFRESH: `${API_BASE_URL}/accounts/token/refresh/`,
  VERIFY_EMAIL: `${API_BASE_URL}/accounts/verify-email/`,
  VERIFY_EMAIL_CONFIRM: `${API_BASE_URL}/accounts/verify-email-confirm/`,
  RESET_PASSWORD: `${API_BASE_URL}/accounts/password/reset/`,
  RESET_PASSWORD_CONFIRM: `${API_BASE_URL}/accounts/password/reset-confirm/`,
  PROFILE: `${API_BASE_URL}/accounts/profile/`,
};

export const AUCTION_ENDPOINTS = {
  LIST: `${API_BASE_URL}/auctions/`,
  BIDS: `${API_BASE_URL}/bids/`,
  CATEGORIES: `${API_BASE_URL}/categories/`,
};

// WebSocket endpoints
export const WS_ENDPOINTS = {
  AUCTION: (auctionId) => `${WS_BASE_URL}/auctions/${auctionId}/`,
};