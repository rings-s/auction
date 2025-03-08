// /src/lib/api.js
/**
 * API client for the Auction Platform backend
 * Enhanced with better error handling and debugging capabilities
 */
import { browser } from '$app/environment';

// Single base API URL - should typically come from environment variables
const API_URL = browser ? import.meta.env.VITE_API_URL || 'http://localhost:8000/api' : '';
const WS_BASE_URL = browser ? import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws' : '';

// Default headers for JSON requests
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * Helper function to handle API responses
 * Enhanced with better error handling and response parsing
 * @param {Response} response - The fetch response object
 * @returns {Promise<any>} - Parsed response data or rejected promise with error
 */
async function handleResponse(response) {
  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  
  if (browser) {
    console.log(`API Response: ${response.status} ${response.statusText} from ${response.url}`);
  }
  
  try {
    let data;
    
    // Only try to parse JSON if content-type is application/json
    if (isJson) {
      const text = await response.text();
      try {
        data = text ? JSON.parse(text) : {};
      } catch (parseError) {
        if (browser) console.error('Failed to parse JSON response:', parseError);
        data = { error: 'Invalid JSON response' };
      }
    } else {
      data = await response.text();
    }
    
    if (browser && import.meta.env.DEV) {
      console.log('Response data:', data);
    }
    
    if (!response.ok) {
      let errorMessage = response.statusText;
      let errorCode = null;
      
      if (data) {
        if (data.error) {
          errorMessage = data.error;
          errorCode = data.code;
        } else if (typeof data === 'object' && Object.keys(data).length > 0 && !Array.isArray(data)) {
          errorMessage = data; // For field-specific validation errors
          errorCode = 'validation_error';
        } else if (data.message) {
          errorMessage = data.message;
        } else if (typeof data === 'string') {
          errorMessage = data;
        }
      }
      
      const error = {
        status: response.status,
        error: errorMessage,
        code: errorCode || `http_${response.status}`,
        raw: data
      };
      
      if (browser) console.error('API Error:', error);
      return Promise.reject(error);
    }
    
    return data;
  } catch (parseError) {
    if (browser) console.error('Failed to parse response:', parseError);
    return Promise.reject({
      status: response.status,
      error: `Failed to parse response: ${parseError.message}`,
      code: 'parse_error',
      raw: parseError
    });
  }
}

/**
 * Adds authorization header with JWT access token
 * @returns {Object} - Headers with Authorization if token exists
 */
function authHeader() {
  let accessToken = null;
  
  if (browser) {
    try {
      accessToken = localStorage.getItem('accessToken');
    } catch (error) {
      console.error('Error accessing localStorage:', error);
    }
  }
  
  return accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {};
}

/**
 * Base request function with token refresh handling
 * Enhanced with better logging and error handling
 * @param {string} endpoint - API endpoint path
 * @param {Object} [options] - Fetch options (method, body, headers, auth)
 * @returns {Promise<any>} - Response data or rejected promise
 */
async function request(endpoint, options = {}) {
  if (!browser) {
    // During SSR, return a rejected promise for client-side only requests
    return Promise.reject({
      status: 0,
      error: 'API requests are only available in the browser environment',
      code: 'ssr_not_supported'
    });
  }
  
  const url = `${API_URL}${endpoint}`;
  
  const headers = {
    ...DEFAULT_HEADERS,
    ...(options.auth !== false ? authHeader() : {}),
    ...(options.headers || {}),
  };
  
  const config = {
    ...options,
    headers,
  };
  
  if (import.meta.env.DEV) {
    console.log(`Making request to: ${url}`, {
      method: options.method || 'GET',
      body: options.body ? 
        (typeof options.body === 'string' ? JSON.parse(options.body) : 'FormData or non-JSON body') 
        : undefined,
      headers: headers
    });
  }
  
  try {
    const response = await fetch(url, config);
    return await handleResponse(response);
  } catch (error) {
    // Server responded with an error
    if (error.status) {
      if (error.status === 401) {
        try {
          // Check if we have a refresh token
          const refreshToken = localStorage.getItem('refreshToken');
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }
          
          console.log('Attempting to refresh token...');
          const refreshResult = await refreshAccessToken();
          
          if (!refreshResult || !refreshResult.access) {
            throw new Error('Token refresh failed');
          }
          
          // Update headers with new token
          const newHeaders = {
            ...headers,
            Authorization: `Bearer ${refreshResult.access}`
          };
          
          console.log('Retrying request with new token');
          const newResponse = await fetch(url, {
            ...config,
            headers: newHeaders,
          });
          
          return await handleResponse(newResponse);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          
          // Clear auth data on token refresh failure
          try {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            localStorage.removeItem('lastActivity');
          } catch (storageError) {
            console.error('Error clearing localStorage:', storageError);
          }
          
          return Promise.reject({
            ...error,
            code: 'token_refresh_failed'
          });
        }
      }
      
      throw error;
    }
    
    // Network error or other issues
    console.error(`Network error for ${url}:`, error);
    return Promise.reject({
      status: 0,
      error: `Network error: ${error.message}`,
      code: 'network_error',
      raw: error
    });
  }
}

/**
 * Helper function for converting objects to query parameters
 * @param {Object} params - The parameters to convert
 * @returns {string} - Query string
 */
function objectToQueryParams(params = {}) {
  if (!params || Object.keys(params).length === 0) return '';
  
  const queryParams = new URLSearchParams();
  
  for (const key in params) {
    if (params[key] !== undefined && params[key] !== null) {
      queryParams.append(key, params[key]);
    }
  }
  
  return `?${queryParams.toString()}`;
}

/**
 * Refresh the access token using the refresh token
 * Enhanced with better error handling
 * @returns {Promise<Object>} - New tokens or rejected promise
 */
async function refreshAccessToken() {
  if (!browser) {
    return Promise.reject({
      status: 0,
      error: 'Token refresh is only available in the browser environment',
      code: 'ssr_not_supported'
    });
  }
  
  let refreshToken;
  
  try {
    refreshToken = localStorage.getItem('refreshToken');
  } catch (error) {
    console.error('Error accessing localStorage:', error);
    return Promise.reject({
      status: 401,
      error: 'Cannot access localStorage',
      code: 'storage_error'
    });
  }
  
  if (!refreshToken) {
    console.error('No refresh token available');
    return Promise.reject({
      status: 401,
      error: 'No refresh token available',
      code: 'no_refresh_token'
    });
  }
  
  console.log('Refreshing access token...');
  
  try {
    const response = await fetch(`${API_URL}/accounts/token/refresh/`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({ refresh: refreshToken }),
    });
    
    const data = await handleResponse(response);
    
    if (!data || !data.access) {
      throw new Error('Invalid refresh token response');
    }
    
    try {
      localStorage.setItem('accessToken', data.access);
      // Note: SimpleJWT's TokenRefreshView typically only returns 'access', not 'refresh'
      // If your backend customizes this to return a new refresh token, keep this line
      if (data.refresh) {
        localStorage.setItem('refreshToken', data.refresh);
      }
      localStorage.setItem('lastActivity', Date.now().toString());
    } catch (storageError) {
      console.error('Error saving token to localStorage:', storageError);
    }
    
    console.log('Token refreshed successfully');
    return data;
  } catch (error) {
    console.error('Token refresh failed:', error);
    
    try {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      localStorage.removeItem('lastActivity');
    } catch (storageError) {
      console.error('Error clearing localStorage:', storageError);
    }
    
    throw error;
  }
}

/**
 * Authentication API calls
 */
export const authApi = {
  register: (userData) => {
    if (browser) console.log('Registering user:', { ...userData, password: '[REDACTED]' });
    if (userData.date_of_birth) {
      const date = new Date(userData.date_of_birth);
      if (!isNaN(date.getTime())) {
        userData.date_of_birth = date.toISOString().split('T')[0];
      }
    }
    return request('/accounts/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
      auth: false,
    });
  },
  
  verifyEmail: (email, verificationCode) => {
    if (browser) console.log('Verifying email:', email);
    return request('/accounts/verify-email/', {
      method: 'POST',
      body: JSON.stringify({ email, verification_token: verificationCode }), // Match backend field
      auth: false,
    });
  },
  
  login: (email, password) => {
    if (browser) console.log('Logging in user:', email);
    return request('/accounts/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      auth: false,
    });
  },
  
  logout: () => {
    if (!browser) {
      return Promise.reject({
        status: 0,
        error: 'Logout is only available in the browser environment',
        code: 'ssr_not_supported'
      });
    }
    
    console.log('Logging out user');
    let refreshToken;
    
    try {
      refreshToken = localStorage.getItem('refreshToken');
    } catch (error) {
      console.error('Error accessing localStorage:', error);
    }
    
    if (refreshToken) {
      return request('/accounts/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh: refreshToken }),
      }).finally(() => {
        clearAuthData();
      });
    }
    
    clearAuthData();
    return Promise.resolve({ status: 'success', message: 'Logged out locally' });
  },
  
  verifyToken: () => {
    if (!browser) {
      return Promise.reject({
        status: 0,
        error: 'Token verification is only available in the browser environment',
        code: 'ssr_not_supported'
      });
    }
    
    console.log('Verifying token');
    let accessToken;
    
    try {
      accessToken = localStorage.getItem('accessToken');
    } catch (error) {
      console.error('Error accessing localStorage:', error);
      return Promise.reject({
        status: 401,
        error: 'Cannot access localStorage',
        code: 'storage_error'
      });
    }
    
    if (!accessToken) {
      return Promise.reject({
        status: 401,
        error: 'No access token found',
        code: 'missing_token'
      });
    }
    
    return request('/accounts/token/verify/', {
      method: 'POST',
      body: JSON.stringify({ token: accessToken }), // SimpleJWT expects 'token'
    });
  },
  
  requestPasswordReset: (email) => {
    if (browser) console.log('Requesting password reset for:', email);
    return request('/accounts/password/reset/', {
      method: 'POST',
      body: JSON.stringify({ email }),
      auth: false,
    });
  },
  
  verifyResetCode: (email, resetCode) => {
    if (browser) console.log('Verifying reset code for:', email);
    return request('/accounts/password/reset/verify/', {
      method: 'POST',
      body: JSON.stringify({ email, reset_token: resetCode }), // Match backend field
      auth: false,
    });
  },
  
  resetPassword: (email, resetCode, newPassword, confirmPassword) => {
    if (browser) console.log('Resetting password for:', email);
    return request('/accounts/password/reset/confirm/', {
      method: 'POST',
      body: JSON.stringify({
        email,
        reset_token: resetCode, // Match backend field
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
      auth: false,
    });
  },
  
  changePassword: (currentPassword, newPassword, confirmPassword) => {
    if (browser) console.log('Changing password for authenticated user');
    return request('/accounts/password/', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    });
  },
};

/**
 * User profile API calls
 */
export const profileApi = {
  getProfile: () => {
    if (browser) console.log('Fetching user profile');
    return request('/accounts/profile/', {
      method: 'GET',
    });
  },
  
  updateProfile: (profileData) => {
    if (browser) console.log('Updating user profile');
    if (profileData.date_of_birth) {
      const date = new Date(profileData.date_of_birth);
      if (!isNaN(date.getTime())) {
        profileData.date_of_birth = date.toISOString().split('T')[0];
      }
    }
    return request('/accounts/profile/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },
  
  patchProfile: (profileData) => {
    if (browser) console.log('Patching user profile with data:', profileData);
    if (profileData.date_of_birth) {
      const date = new Date(profileData.date_of_birth);
      if (!isNaN(date.getTime())) {
        profileData.date_of_birth = date.toISOString().split('T')[0];
      }
    }
    return request('/accounts/profile/', {
      method: 'PATCH',
      body: JSON.stringify(profileData),
    });
  },
  
  getPublicProfile: (userId) => {
    if (browser) console.log('Fetching public profile for user:', userId);
    return request(`/accounts/profile/${userId}/`, {
      method: 'GET',
    });
  },

  updateAvatar: (formData) => {
    if (browser) console.log('Uploading avatar image');
    return request('/accounts/profile/avatar/', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set multipart/form-data boundary
    });
  },
};

/**
 * Role management API calls
 */
export const roleApi = {
  assignRole: (userId, roles) => {
    if (browser) console.log('Assigning roles to user:', userId, roles);
    return request(`/accounts/roles/assign/${userId}/`, {
      method: 'POST',
      body: JSON.stringify({ roles }),
    });
  },
  
  getDashboard: () => {
    if (browser) console.log('Fetching role dashboard data');
    return request('/accounts/dashboard/role/', {
      method: 'GET',
    });
  },
};

/**
 * Category API calls
 */
export const categoryApi = {
  list: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching categories with params:', params);
    return request(`/base/categories/${queryParams}`, {
      method: 'GET',
    });
  },
  
  create: (categoryData) => {
    if (browser) console.log('Creating new category');
    return request('/base/categories/create/', {
      method: 'POST',
      body: JSON.stringify(categoryData),
    });
  },
  
  getBySlug: (slug) => {
    if (browser) console.log('Fetching category details:', slug);
    return request(`/base/categories/${slug}/`, {
      method: 'GET',
    });
  },
  
  update: (slug, categoryData) => {
    if (browser) console.log('Updating category:', slug);
    return request(`/base/categories/${slug}/update/`, {
      method: 'PUT',
      body: JSON.stringify(categoryData),
    });
  },
  
  delete: (slug) => {
    if (browser) console.log('Deleting category:', slug);
    return request(`/base/categories/${slug}/delete/`, {
      method: 'DELETE',
    });
  },

  // New: Get subcategories by category ID or slug
  listSubcategories: (categoryId, options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams({ 
      ...params,
      category: categoryId 
    });
    if (browser) console.log('Fetching subcategories for category:', categoryId);
    return request(`/base/subcategories/${queryParams}`, {
      method: 'GET',
    });
  },
};

/**
 * Auction API calls
 */
export const auctionApi = {
  list: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching auctions with params:', params);
    return request(`/base/auctions/${queryParams}`, {
      method: 'GET',
    });
  },
  
  getById: (auctionId) => {
    if (browser) console.log('Fetching auction details:', auctionId);
    return request(`/base/auctions/${auctionId}/`, {
      method: 'GET',
    });
  },
  
  create: (auctionData) => {
    if (browser) console.log('Creating new auction');
    return request('/base/auctions/create/', {
      method: 'POST',
      body: JSON.stringify(auctionData),
    });
  },
  
  update: (auctionId, auctionData) => {
    if (browser) console.log('Updating auction:', auctionId);
    return request(`/base/auctions/${auctionId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(auctionData),
    });
  },
  
  delete: (auctionId) => {
    if (browser) console.log('Deleting auction:', auctionId);
    return request(`/base/auctions/${auctionId}/delete/`, {
      method: 'DELETE',
    });
  },
  
  createBid: (auctionId, bidData) => {
    if (browser) console.log('Creating bid for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/bids/create/`, {
      method: 'POST',
      body: JSON.stringify(bidData),
    });
  },
  
  listBids: (auctionId, options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching bids for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/bids/${queryParams}`, {
      method: 'GET',
    });
  },
  
  // Add getBids as an alias to listBids for compatibility with our WebSocket fallback
  getBids: (auctionId, options = {}) => {
    if (browser) console.log('Fetching bids (fallback method) for auction:', auctionId);
    return auctionApi.listBids(auctionId, options);
  },
  
  uploadDocument: (auctionId, formData) => {
    if (browser) console.log('Uploading document for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/documents/upload/`, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set multipart/form-data boundary
    });
  },
  
  listDocuments: (auctionId, options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching documents for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/documents/${queryParams}`, {
      method: 'GET',
    });
  },
  
  createTransaction: (auctionId, transactionData) => {
    if (browser) console.log('Creating transaction for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/transactions/create/`, {
      method: 'POST',
      body: JSON.stringify(transactionData),
    });
  },

  // New: Upload main image
  uploadImage: (auctionId, formData) => {
    if (browser) console.log('Uploading main image for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/update/`, {
      method: 'PATCH',
      body: formData,
      headers: {}, // Let browser set multipart/form-data boundary
    });
  },

  // New: Upload additional images
  uploadAdditionalImages: (auctionId, formData) => {
    if (browser) console.log('Uploading additional images for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/images/upload/`, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set multipart/form-data boundary
    });
  },

  /**
   * List auctions won by the current user
   */
  listWon: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching won auctions with params:', params);
    return request(`/base/user/won-auctions/${queryParams}`, {
      method: 'GET',
    });
  },
};

/**
 * Bid API calls
 */
export const bidApi = {
  /**
   * List bids made by the current user
   * Uses the correct endpoint: /base/user/bids/ 
   */
  listUserBids: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching user bids with params:', params);
    return request(`/base/user/bids/${queryParams}`, {
      method: 'GET',
    });
  },
  
  /**
   * List bids for a specific auction
   */
  listAuctionBids: (auctionId, options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching bids for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/bids/${queryParams}`, {
      method: 'GET',
    });
  },
  
  /**
   * Create a new bid on an auction
   */
  createBid: (auctionId, bidData) => {
    if (browser) console.log('Creating bid for auction:', auctionId);
    return request(`/base/auctions/${auctionId}/bids/create/`, {
      method: 'POST',
      body: JSON.stringify(bidData),
    });
  },
  
  /**
   * Get bids for an auction (alias for listAuctionBids for WebSocket fallback)
   */
  getBids: (auctionId, options = {}) => {
    if (browser) console.log('Fetching bids (fallback method) for auction:', auctionId);
    return bidApi.listAuctionBids(auctionId, options);
  }
};


/**
 * Transaction API calls
 */
export const transactionApi = {
  list: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching transactions with params:', params);
    return request(`/base/transactions/${queryParams}`, {
      method: 'GET',
    });
  },
  
  getById: (transactionId) => {
    if (browser) console.log('Fetching transaction details:', transactionId);
    return request(`/base/transactions/${transactionId}/`, {
      method: 'GET',
    });
  },
  
  reportIssue: (transactionId, issueData) => {
    if (browser) console.log('Reporting issue for transaction:', transactionId);
    return request(`/base/transactions/${transactionId}/issue/`, {
      method: 'POST',
      body: JSON.stringify(issueData),
    });
  },
  
  export: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Exporting transactions with params:', params);
    return request(`/base/transactions/export/${queryParams}`, {
      method: 'GET',
    });
  },
  
  handleDispute: (transactionId, resolutionData) => {
    if (browser) console.log('Handling dispute for transaction:', transactionId);
    return request(`/base/transactions/${transactionId}/dispute/`, {
      method: 'POST',
      body: JSON.stringify(resolutionData),
    });
  },
  
  getTracking: (trackingNumber, carrier) => {
    if (browser) console.log('Getting tracking info for:', trackingNumber);
    return request(`/base/tracking/${carrier}/${trackingNumber}/`, {
      method: 'GET',
    });
  }
};

/**
 * Payment Method API calls
 */
export const paymentMethodApi = {
  add: (paymentData) => {
    if (browser) console.log('Adding new payment method');
    return request('/base/payment-methods/add/', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  },
  
  list: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching payment methods with params:', params);
    return request(`/base/payment-methods/${queryParams}`, {
      method: 'GET',
    });
  },
};

/**
 * Contract API calls
 */
export const contractApi = {
  create: (contractData) => {
    if (browser) console.log('Creating new contract');
    return request('/base/contracts/create/', {
      method: 'POST',
      body: JSON.stringify(contractData),
    });
  },
  
  list: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching contracts with params:', params);
    return request(`/base/contracts/${queryParams}`, {
      method: 'GET',
    });
  },
  
  review: (contractId, reviewData) => {
    if (browser) console.log('Reviewing contract:', contractId);
    return request(`/base/contracts/${contractId}/review/`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  },
};

/**
 * Message API calls
 */
export const messageApi = {
  getHistory: (roomId, options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching message history for room:', roomId);
    return request(`/base/messages/${roomId}/${queryParams}`, {
      method: 'GET',
    });
  },
};

/**
 * Dashboard API calls
 */
export const dashboardApi = {
  getUserDashboard: () => {
    if (browser) console.log('Fetching user dashboard data');
    return request('/base/dashboard/', {
      method: 'GET',
    });
  },
  
  getAdminDashboard: () => {
    if (browser) console.log('Fetching admin dashboard data');
    return request('/base/admin/dashboard/', {
      method: 'GET',
    });
  },
};

/**
 * Inspector API calls
 */
export const inspectorApi = {
  createInspectionReport: (auctionId, reportData) => {
    if (browser) console.log('Creating inspection report for auction:', auctionId);
    return request(`/base/inspections/create/${auctionId}/`, {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  },
  
  verifyDocument: (documentId) => {
    if (browser) console.log('Verifying document:', documentId);
    return request(`/base/documents/${documentId}/verify/`, {
      method: 'POST',
    });
  },
};

/**
 * Search API
 */
export const searchApi = {
  search: (options = {}) => {
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Searching with params:', params);
    return request(`/base/search/${queryParams}`, {
      method: 'GET',
    });
  },
};

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
    const { params = {} } = options;
    const queryParams = objectToQueryParams(params);
    if (browser) console.log('Fetching notifications with params:', params);
    return request(`/base/notifications/${queryParams}`, {
      method: 'GET',
    });
  },

  /**
   * Get a single notification by ID
   * @param {string} notificationId - Notification ID
   * @returns {Promise<Object>} - API response with notification
   */
  getById: (notificationId) => {
    if (browser) console.log('Fetching notification details:', notificationId);
    return request(`/base/notifications/${notificationId}/`, {
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
    return request(`/base/notifications/${notificationId}/read/`, {
      method: 'POST',
    });
  },

  /**
   * Mark all notifications as read
   * @returns {Promise<Object>} - API response
   */
  markAllAsRead: () => {
    if (browser) console.log('Marking all notifications as read');
    return request('/base/notifications/read-all/', {
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
    return request(`/base/notifications/${notificationId}/`, {
      method: 'DELETE',
    });
  },

  /**
   * Get notification settings
   * @returns {Promise<Object>} - API response with settings
   */
  getSettings: () => {
    if (browser) console.log('Fetching notification settings');
    return request('/base/notifications/settings/', {
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
    return request('/base/notifications/settings/', {
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
    return request('/base/notifications/unread-count/', {
      method: 'GET',
    });
  },

  /**
   * Get notification preferences
   * @returns {Promise<Object>} - API response with preferences
   */
  getPreferences: () => {
    if (browser) console.log('Fetching notification preferences');
    return request('/base/notifications/preferences/', {
      method: 'GET',
    });
  },

  /**
   * Update notification preferences
   * @param {Object} preferences - Preferences to update
   * @returns {Promise<Object>} - API response
   */
  updatePreferences: (preferences) => {
    if (browser) console.log('Updating notification preferences');
    return request('/base/notifications/preferences/', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }
};

/**
 * Clear all authentication data from local storage
 * Utility function for global logout/cleanup
 */
export function clearAuthData() {
  if (!browser) return;
  
  try {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('lastActivity');
  } catch (error) {
    console.error('Error clearing localStorage:', error);
  }
}

/**
 * Base API combining all API endpoints in one object for convenience
 */
export const baseApi = {
  category_list: categoryApi.list,
  category_create: categoryApi.create,
  category_detail: categoryApi.getBySlug,
  category_update: categoryApi.update,
  category_delete: categoryApi.delete,
  
  auction_list: auctionApi.list,
  auction_detail: auctionApi.getById,
  auction_create: auctionApi.create,
  auction_update: auctionApi.update,
  auction_delete: auctionApi.delete,
  create_bid: auctionApi.createBid,
  list_bids: auctionApi.listBids,
  get_bids: auctionApi.getBids, // Added new alias for WebSocket fallback
  document_upload: auctionApi.uploadDocument,
  document_list: auctionApi.listDocuments,
  create_transaction: auctionApi.createTransaction,
  user_won_auctions: auctionApi.listWon,
  
  user_bids: bidApi.listUserBids,
  
  transaction_list: transactionApi.list,
  transaction_detail: transactionApi.getById,
  transaction_report_issue: transactionApi.reportIssue,
  transaction_export: transactionApi.export,
  handle_dispute: transactionApi.handleDispute,
  get_tracking: transactionApi.getTracking,
  
  add_payment_method: paymentMethodApi.add,
  list_payment_methods: paymentMethodApi.list,
  
  create_contract: contractApi.create,
  list_contracts: contractApi.list,
  review_contract: contractApi.review,
  
  message_history: messageApi.getHistory,
  
  user_dashboard: dashboardApi.getUserDashboard,
  admin_dashboard: dashboardApi.getAdminDashboard,
  
  create_inspection_report: inspectorApi.createInspectionReport,
  verify_document: inspectorApi.verifyDocument,
  
  search: searchApi.search,
  
  // Notification endpoints
  notification_list: notificationApi.list,
  notification_detail: notificationApi.getById,
  notification_mark_read: notificationApi.markAsRead,
  notification_mark_all_read: notificationApi.markAllAsRead,
  notification_delete: notificationApi.delete,
  notification_settings: notificationApi.getSettings,
  notification_update_settings: notificationApi.updateSettings,
  notification_unread_count: notificationApi.getUnreadCount,
  notification_preferences: notificationApi.getPreferences,
  notification_update_preferences: notificationApi.updatePreferences,
  
  // Helper function
  objectToQueryParams
};

// Export combined API
export const api = {
  auth: authApi,
  profile: profileApi,
  role: roleApi,
  category: categoryApi,
  auction: auctionApi,
  bid: bidApi,
  transaction: transactionApi,
  payment: paymentMethodApi,
  contract: contractApi,
  message: messageApi,
  dashboard: dashboardApi,
  inspector: inspectorApi,
  search: searchApi,
  notification: notificationApi,
  base: baseApi,
  clearAuthData,
  refreshToken: refreshAccessToken,
  objectToQueryParams
};


// For testing purposes only
const callApi = async (endpoint, options = {}) => {
  if (!browser) return null;
  
  console.group(`API Call: ${endpoint}`);
  console.log('Options:', options);
  try {
    const response = await fetch(`/api/${endpoint}`, options);
    const data = await response.json();
    console.log('Response:', data);
    console.groupEnd();
    return data;
  } catch (error) {
    console.error('Error:', error);
    console.groupEnd();
    throw error;
  }
};

export default api;