// src/lib/api/dashboard.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const DASHBOARD_URL = `${API_BASE_URL}/dashboard`;

/**
 * Enhanced API request handler with better error handling
 */
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('accessToken');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };

  const requestOptions = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    let response = await fetch(url, requestOptions);
    
    // Handle token refresh for 401 responses
    if (response.status === 401 && token) {
      try {
        const newToken = await refreshToken();
        requestOptions.headers.Authorization = `Bearer ${newToken}`;
        response = await fetch(url, requestOptions);
      } catch (refreshError) {
        throw new Error('Your session has expired. Please log in again.');
      }
    }

    // Parse response data
    let data;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Handle error responses
    if (!response.ok) {
      const errorMessage = extractErrorMessage(data, response.status);
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    throw error;
  }
}

/**
 * Extract error message from different response formats
 */
function extractErrorMessage(data, status) {
  if (typeof data === 'string') {
    return data || `HTTP Error ${status}`;
  }

  if (data && typeof data === 'object') {
    if (data.error && data.error.message) {
      return data.error.message;
    }
    
    if (data.error && typeof data.error === 'string') {
      return data.error;
    }

    if (data.detail) {
      return data.detail;
    }

    if (data.message) {
      return data.message;
    }

    // Handle validation errors
    const validationErrors = [];
    for (const [field, messages] of Object.entries(data)) {
      if (field !== 'error' && field !== 'message' && field !== 'detail') {
        if (Array.isArray(messages)) {
          validationErrors.push(`${field}: ${messages.join(', ')}`);
        } else if (typeof messages === 'string') {
          validationErrors.push(`${field}: ${messages}`);
        }
      }
    }

    if (validationErrors.length > 0) {
      return validationErrors.join('; ');
    }
  }

  return `HTTP Error ${status}`;
}

/**
 * Get user dashboard statistics
 */
export async function getUserDashboardStats() {
  return await apiRequest(`${DASHBOARD_URL}/`, { method: 'GET' });
}

/**
 * Get system dashboard statistics (admin/appraiser only)
 */
export async function getSystemDashboardStats() {
  return await apiRequest(`${DASHBOARD_URL}/system/`, { method: 'GET' });
}

/**
 * Get recent activity feed
 */
export async function getRecentActivity(limit = 20) {
  const queryParams = new URLSearchParams();
  if (limit) queryParams.append('limit', limit.toString());
  
  const url = `${DASHBOARD_URL}/activity/?${queryParams.toString()}`;
  return await apiRequest(url, { method: 'GET' });
}

/**
 * Get dashboard properties with filtering
 */
export async function getDashboardProperties(filters = {}) {
  const queryParams = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  const url = `${DASHBOARD_URL}/properties/?${queryParams.toString()}`;
  return await apiRequest(url, { method: 'GET' });
}

/**
 * Get dashboard auctions with filtering
 */
export async function getDashboardAuctions(filters = {}) {
  const queryParams = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  const url = `${DASHBOARD_URL}/auctions/?${queryParams.toString()}`;
  return await apiRequest(url, { method: 'GET' });
}

/**
 * Get dashboard bids with filtering
 */
export async function getDashboardBids(filters = {}) {
  const queryParams = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  const url = `${DASHBOARD_URL}/bids/?${queryParams.toString()}`;
  return await apiRequest(url, { method: 'GET' });
}

/**
 * Refresh dashboard data
 */
export async function refreshDashboardData() {
  try {
    const [userStats, recentActivity] = await Promise.all([
      getUserDashboardStats(),
      getRecentActivity(10)
    ]);
    
    return {
      userStats,
      recentActivity,
      success: true
    };
  } catch (error) {
    throw error;
  }
}

/**
 * Get dashboard summary for mobile/compact view
 */
export async function getDashboardSummary() {
  try {
    const stats = await getUserDashboardStats();
    
    return {
      totalProperties: stats.total_properties || 0,
      totalAuctions: stats.total_auctions || 0,
      totalBids: stats.total_bids || 0,
      unreadMessages: stats.messages_unread || 0,
      userRole: stats.user_role || 'user',
      userPriority: stats.user_priority || 1
    };
  } catch (error) {
    throw error;
  }
}