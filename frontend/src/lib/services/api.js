// src/lib/services/api.js
// Core API service using SvelteFetch - Fully updated with authentication fixes

import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { get } from 'svelte/store';
import { language } from '$lib/i18n';
import { toast } from '$lib/stores/toast';

// API configuration
const API_BASE_URL = browser && import.meta.env ? import.meta.env.VITE_API_URL : 'http://localhost:8000/api';
const API_TIMEOUT = 30000; // 30 seconds

// Custom response error
class ResponseError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ResponseError';
    this.status = status;
    this.data = data;
  }
}

// Abort controller for request cancellation
const createAbortController = (timeout = API_TIMEOUT) => {
  if (!browser) return { signal: null, clear: () => {} };
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  return {
    signal: controller.signal,
    clear: () => clearTimeout(timeoutId)
  };
};

// Get access token from localStorage with validation
const getAccessToken = () => {
  if (!browser) return null;
  
  try {
    // First try direct accessToken
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken && typeof accessToken === 'string' && accessToken.trim().length > 0) {
      return accessToken;
    }
    
    // Fallback to auth object if exists
    const authData = localStorage.getItem('auth');
    if (authData) {
      const parsed = JSON.parse(authData);
      
      // Basic validation - make sure token is a non-empty string
      if (parsed && parsed.token && typeof parsed.token === 'string' && parsed.token.trim().length > 0) {
        return parsed.token;
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error retrieving access token:', error);
    // If there's an error, clear potentially corrupted tokens
    localStorage.removeItem('auth');
    localStorage.removeItem('accessToken');
    return null;
  }
};

// Get refresh token from localStorage with validation
const getRefreshToken = () => {
  if (!browser) return null;
  
  try {
    // First try direct refreshToken
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken && typeof refreshToken === 'string' && refreshToken.trim().length > 0) {
      return refreshToken;
    }
    
    // Fallback to auth object if exists
    const authData = localStorage.getItem('auth');
    if (authData) {
      const parsed = JSON.parse(authData);
      
      // Basic validation - make sure token is a non-empty string
      if (parsed && parsed.refreshToken && typeof parsed.refreshToken === 'string' && parsed.refreshToken.trim().length > 0) {
        return parsed.refreshToken;
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error retrieving refresh token:', error);
    return null;
  }
};

// Reset all auth data - use in case of invalid tokens
const clearAuthData = () => {
  if (!browser) return;
  
  try {
    // Clear all possible auth data
    localStorage.removeItem('auth');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('lastActivity');
    
    // Clear auth cookie
    document.cookie = 'accessToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  } catch (error) {
    console.error('Error clearing auth data:', error);
  }
};

// Set up standard HTTP headers
const getHeaders = (customHeaders = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...customHeaders
  };
  
  // Add language header if available
  if (browser) {
    try {
      const currentLanguage = get(language);
      if (currentLanguage) {
        headers['Accept-Language'] = currentLanguage;
      }
    } catch (error) {
      console.error('Error getting language:', error);
    }
  }
  
  // Add auth token if available
  const token = getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Handle server response
const handleResponse = async (response) => {
  let data;
  
  try {
    // Get raw data (text or JSON)
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const text = await response.text();
      try {
        data = text ? JSON.parse(text) : {};
      } catch (parseError) {
        console.error('Failed to parse JSON response:', parseError);
        data = { error: 'Invalid JSON response' };
      }
    } else {
      data = await response.text();
    }
    
    // Check response status
    if (!response.ok) {
      // Special handling for login endpoint when receiving 401
      const isLoginEndpoint = response.url.includes('/accounts/login/');
      
      if (response.status === 401 && isLoginEndpoint) {
        // For login endpoints, we want to return the error rather than redirecting
        throw new ResponseError(
          data.detail || data.error || data.non_field_errors?.join(', ') || 'Invalid credentials',
          response.status,
          data
        );
      }
      
      // Handle authentication errors for non-login endpoints
      if (response.status === 401 && !isLoginEndpoint) {
        // Look for specific token error messages
        const isTokenError = 
          (typeof data === 'object' && 
           (data.detail === 'Given token not valid for any token type' || 
            data.code === 'token_not_valid' ||
            data.error_code === 'token_expired')) ||
          (typeof data === 'string' && 
           (data.includes('token') && data.includes('invalid')));
        
        if (isTokenError && browser) {
          console.warn('Invalid token detected, attempting to refresh token');
          
          try {
            const refreshed = await refreshToken();
            if (refreshed) {
              // Will retry from outside this function
              return null;
            } else {
              // Refresh failed, log out
              console.warn('Token refresh failed, clearing auth data');
              clearAuthData();
              
              // Redirect to login
              if (typeof toast !== 'undefined') {
                toast.error('Your session has expired. Please log in again.');
              }
              goto('/auth/login');
            }
          } catch (error) {
            console.error('Token refresh failed:', error);
            clearAuthData();
            
            // Show toast notification if available
            if (typeof toast !== 'undefined') {
              toast.error('Your session has expired. Please log in again.');
            }
            
            goto('/auth/login');
          }
          return null;
        }
      }
      
      // Format error message
      let errorMessage = 'An unknown error occurred';
      
      if (typeof data === 'object' && data !== null) {
        // Check for different Django error message formats
        errorMessage = data.error || data.message || data.detail || errorMessage;
        
        // Check for non_field_errors (common in Django)
        if (data.non_field_errors && Array.isArray(data.non_field_errors)) {
          errorMessage = data.non_field_errors.join(', ');
        }
        
        // Handle validation errors (nested error objects)
        if (data.errors) {
          if (Array.isArray(data.errors)) {
            errorMessage = data.errors.map(e => e.message || e).join(', ');
          } else if (typeof data.errors === 'object') {
            errorMessage = Object.values(data.errors).flat().join(', ');
          }
        }
      } else if (typeof data === 'string' && data) {
        errorMessage = data;
      }
      
      // Throw error with response info
      throw new ResponseError(errorMessage, response.status, data);
    }
    
    return data;
  } catch (error) {
    if (error instanceof ResponseError) {
      throw error;
    }
    
    // Handle JSON parsing errors or other issues
    throw new ResponseError(
      error.message || 'Failed to process response',
      response.status || 0
    );
  }
};

// Function to refresh token
const refreshToken = async () => {
  if (!browser) return false;
  
  const refreshToken = getRefreshToken();
  
  if (!refreshToken) {
    console.warn('No refresh token available');
    return false;
  }
  
  try {
    console.log('Attempting to refresh token...');
    
    const response = await fetch(`${API_BASE_URL}/accounts/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
      credentials: 'include',
    });
    
    if (!response.ok) {
      console.warn('Refresh token response not OK:', response.status);
      return false;
    }
    
    const data = await response.json();
    
    if (!data.access) {
      console.warn('No access token in refresh response');
      return false;
    }
    
    // Update token in localStorage
    localStorage.setItem('accessToken', data.access);
    if (data.refresh) {
      localStorage.setItem('refreshToken', data.refresh);
    }
    
    // Set auth cookie for server-side auth
    if (typeof document !== 'undefined') {
      document.cookie = `accessToken=${data.access}; path=/; max-age=86400; SameSite=Strict`;
    }
    
    console.log('Token refreshed successfully');
    return true;
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
};

// Core request functions
export async function apiGet(endpoint, params = {}, customHeaders = {}) {
  // Create abort controller
  const controller = createAbortController();
  
  try {
    // Build URL with parameters
    const url = new URL(`${API_BASE_URL}/${endpoint}`);
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null) {
        url.searchParams.append(key, params[key]);
      }
    });
    
    console.log(`Making GET request to ${url.toString()}`);
    
    // Create request
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getHeaders(customHeaders),
      signal: controller.signal,
      credentials: 'include',
    });
    
    const result = await handleResponse(response);
    
    // If result is null, retry after token refresh
    if (result === null) {
      return await apiGet(endpoint, params, customHeaders);
    }
    
    return result;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request was cancelled due to timeout');
    }
    throw error;
  } finally {
    controller.clear();
  }
}

export async function apiPost(endpoint, data = {}, customHeaders = {}) {
  const controller = createAbortController();
  
  try {
    console.log(`Making POST request to ${API_BASE_URL}/${endpoint}`, { 
      data: endpoint.includes('password') ? { ...data, password: '[REDACTED]' } : data 
    });
    
    // Enhanced logging for auth-related endpoints
    const isAuthEndpoint = endpoint.includes('login') || 
                          endpoint.includes('register') || 
                          endpoint.includes('verify') ||
                          endpoint.includes('token');
    
    if (isAuthEndpoint) {
      console.log('Auth-related endpoint detected, ensuring proper headers and CORS settings');
    }
    
    // Improved request with better error handling
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: 'POST',
      headers: getHeaders(customHeaders),
      body: JSON.stringify(data),
      signal: controller.signal,
      credentials: 'include',
      mode: 'cors'
    });
    
    console.log(`Received response from ${endpoint}:`, {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries([...response.headers.entries()])
    });
    
    // Log the response body for debugging (clone to avoid consuming it)
    try {
      const responseClone = response.clone();
      const responseText = await responseClone.text();
      console.log(`Response body from ${endpoint}:`, 
        responseText.substring(0, 500) + (responseText.length > 500 ? '...[truncated]' : '')); 
    } catch (e) {
      console.warn('Could not log response body:', e);
    }
    
    const result = await handleResponse(response);
    
    // Handle special case for auth responses
    if (isAuthEndpoint && result && (result.access || result.token)) {
      console.log('Received auth tokens, storing in localStorage');
      
      // Store tokens
      if (result.access) {
        localStorage.setItem('accessToken', result.access);
        localStorage.setItem('refreshToken', result.refresh || '');
        
        // Set cookie for server-side auth
        if (typeof document !== 'undefined') {
          document.cookie = `accessToken=${result.access}; path=/; max-age=86400; SameSite=Strict`;
        }
      } else if (result.token) {
        localStorage.setItem('accessToken', result.token);
        
        // Set cookie for server-side auth
        if (typeof document !== 'undefined') {
          document.cookie = `accessToken=${result.token}; path=/; max-age=86400; SameSite=Strict`;
        }
      }
      
      // Store user data if present
      if (result.user) {
        localStorage.setItem('user', JSON.stringify(result.user));
        localStorage.setItem('lastActivity', Date.now().toString());
      }
    }
    
    if (result === null) {
      return await apiPost(endpoint, data, customHeaders);
    }
    
    return result;
  } catch (error) {
    console.error(`Error in apiPost to ${endpoint}:`, error);
    
    if (error.name === 'AbortError') {
      throw new Error('Request was cancelled due to timeout');
    }
    
    // Add more context to the error
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
      throw new Error(`Network error when connecting to ${API_BASE_URL}/${endpoint}. Please check API URL configuration and ensure CORS is properly set up on the server.`);
    }
    
    throw error;
  } finally {
    controller.clear();
  }
}

export async function apiPut(endpoint, data = {}, customHeaders = {}) {
  const controller = createAbortController();
  
  try {
    console.log(`Making PUT request to ${API_BASE_URL}/${endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: 'PUT',
      headers: getHeaders(customHeaders),
      body: JSON.stringify(data),
      signal: controller.signal,
      credentials: 'include',
    });
    
    const result = await handleResponse(response);
    
    if (result === null) {
      return await apiPut(endpoint, data, customHeaders);
    }
    
    return result;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request was cancelled due to timeout');
    }
    throw error;
  } finally {
    controller.clear();
  }
}

export async function apiPatch(endpoint, data = {}, customHeaders = {}) {
  const controller = createAbortController();
  
  try {
    console.log(`Making PATCH request to ${API_BASE_URL}/${endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: 'PATCH',
      headers: getHeaders(customHeaders),
      body: JSON.stringify(data),
      signal: controller.signal,
      credentials: 'include',
    });
    
    const result = await handleResponse(response);
    
    if (result === null) {
      return await apiPatch(endpoint, data, customHeaders);
    }
    
    return result;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request was cancelled due to timeout');
    }
    throw error;
  } finally {
    controller.clear();
  }
}

export async function apiDelete(endpoint, customHeaders = {}) {
  const controller = createAbortController();
  
  try {
    console.log(`Making DELETE request to ${API_BASE_URL}/${endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
      method: 'DELETE',
      headers: getHeaders(customHeaders),
      signal: controller.signal,
      credentials: 'include',
    });
    
    const result = await handleResponse(response);
    
    if (result === null) {
      return await apiDelete(endpoint, customHeaders);
    }
    
    return result;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request was cancelled due to timeout');
    }
    throw error;
  } finally {
    controller.clear();
  }
}

// File uploads
export async function apiUploadFile(endpoint, file, onProgress = null, customHeaders = {}) {
  if (!browser) {
    throw new Error('File uploads are only supported in browser environment');
  }
  
  const controller = createAbortController();
  
  try {
    const formData = new FormData();
    
    if (file instanceof File) {
      formData.append('file', file);
    } else if (typeof file === 'object') {
      // Allow passing object with field name and file pairs
      Object.entries(file).forEach(([fieldName, fileObject]) => {
        formData.append(fieldName, fileObject);
      });
    } else {
      throw new Error('Invalid file object');
    }
    
    console.log(`Making file upload request to ${API_BASE_URL}/${endpoint}`);
    
    // Set up XHR with progress monitoring
    const xhr = new XMLHttpRequest();
    
    // Promise to convert XHR to promise
    const uploadPromise = new Promise((resolve, reject) => {
      xhr.open('POST', `${API_BASE_URL}/${endpoint}`);
      
      // Add headers
      const headers = getHeaders({ 'Content-Type': 'multipart/form-data', ...customHeaders });
      Object.keys(headers).forEach(key => {
        // Skip content-type for FormData - browser will set with boundary
        if (key.toLowerCase() !== 'content-type') {
          xhr.setRequestHeader(key, headers[key]);
        }
      });
      
      // Set withCredentials for CORS requests with cookies
      xhr.withCredentials = true;
      
      // Handle events
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          let response;
          try {
            response = JSON.parse(xhr.responseText);
          } catch {
            response = xhr.responseText;
          }
          resolve(response);
        } else {
          let errorData;
          try {
            errorData = JSON.parse(xhr.responseText);
          } catch {
            errorData = xhr.statusText;
          }
          reject(new ResponseError(
            errorData.error || errorData.detail || 'Upload failed',
            xhr.status,
            errorData
          ));
        }
      };
      
      xhr.onerror = () => reject(new Error('A network error occurred'));
      xhr.ontimeout = () => reject(new Error('Request timed out'));
      
      // Add progress monitoring if available
      if (onProgress && typeof onProgress === 'function') {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            onProgress(percentComplete);
          }
        };
      }
      
      // Send data
      xhr.send(formData);
      
      // Cancel on timeout
      controller.signal.addEventListener('abort', () => xhr.abort());
    });
    
    return await uploadPromise;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Upload was cancelled due to timeout');
    }
    throw error;
  } finally {
    controller.clear();
  }
}

// Initialize function for auth store
export async function initialize() {
  if (!browser) return false;
  
  try {
    // First check if we have valid tokens
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();
    
    if (!accessToken && !refreshToken) {
      clearAuthData();
      return false;
    }
    
    if (accessToken) {
      // Try to validate the token
      try {
        const response = await fetch(`${API_BASE_URL}/accounts/token/verify/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ token: accessToken }),
          credentials: 'include'
        });
        
        if (response.ok) {
          // Token is valid
          console.log('Access token is valid');
          return true;
        }
        
        // Token is invalid, try to refresh
        console.log('Access token is invalid, trying to refresh...');
      } catch (error) {
        console.error('Error validating token:', error);
      }
    }
    
    // Try to refresh the token
    if (refreshToken) {
      const refreshed = await refreshToken();
      if (refreshed) {
        console.log('Token refreshed successfully');
        return true;
      }
    }
    
    // If we get here, all attempts failed
    clearAuthData();
    return false;
  } catch (error) {
    console.error('Error initializing auth:', error);
    clearAuthData();
    return false;
  }
}

// Export additional helper methods
export default {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  patch: apiPatch,
  delete: apiDelete,
  upload: apiUploadFile,
  refreshToken,
  clearAuthData,
  getBaseUrl: () => API_BASE_URL,
  initialize
};