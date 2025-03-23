// src/lib/services/auth.js
// Authentication Services - Fixed version based on working implementation

import { browser } from '$app/environment';
import api from './api';

/**
 * Authentication service with methods for user authentication
 */
export const authService = {
  /**
   * Login a user with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} - Login response with tokens
   */
  login: async (email, password) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      console.log('Attempting login with credentials:', { email, password: '******' });
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      console.log('API Base URL:', apiBaseUrl);
      
      // Make direct fetch to login endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password
        }),
        credentials: 'include'
      });
      
      console.log('Login response status:', response.status);
      
      // Get response body as text first to handle both JSON and non-JSON responses
      const responseText = await response.text();
      let data;
      
      try {
        // Try to parse as JSON
        data = responseText ? JSON.parse(responseText) : {};
      } catch (e) {
        // If not JSON, use text as is
        console.warn('Response is not valid JSON:', e);
        data = { message: responseText };
      }
      
      if (!response.ok) {
        // Extract error message from response
        let errorMessage = 'Login failed';
        
        if (data) {
          if (typeof data === 'object') {
            errorMessage = data.detail || data.error || data.message || 
                          (data.non_field_errors && data.non_field_errors.join(', ')) || 
                          'Authentication failed';
          } else if (typeof data === 'string') {
            errorMessage = data;
          }
        }
        
        console.error('Login error:', errorMessage);
        throw new Error(errorMessage);
      }
      
      console.log('Login successful:', data);
      
      // Store authentication data
      if (data.access) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh || '');
        
        // Store user data if present
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
          localStorage.setItem('lastActivity', Date.now().toString());
        }
        
        // Set auth cookie for server-side auth
        document.cookie = `accessToken=${data.access}; path=/; max-age=86400; SameSite=Strict`;
      } else {
        console.warn('No access token in login response:', data);
      }
      
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} - Registration response
   */
  register: async (userData) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      console.log('Registering new user:', { ...userData, password: '******' });
      
      // Ensure both password field formats are included for Django compatibility
      const formattedUserData = { ...userData };
      if (formattedUserData.password && !formattedUserData.password_confirmation && formattedUserData.confirm_password) {
        formattedUserData.password_confirmation = formattedUserData.confirm_password;
      } else if (formattedUserData.password && !formattedUserData.confirm_password && formattedUserData.password_confirmation) {
        formattedUserData.confirm_password = formattedUserData.password_confirmation;
      }
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to register endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formattedUserData),
        credentials: 'include'
      });
      
      // Get response body
      const responseText = await response.text();
      let data;
      
      try {
        // Try to parse as JSON
        data = responseText ? JSON.parse(responseText) : {};
      } catch (e) {
        // If not JSON, use text as is
        console.warn('Response is not valid JSON:', e);
        data = { message: responseText };
      }
      
      if (!response.ok) {
        // Extract error message from response
        let errorMessage = 'Registration failed';
        
        if (data) {
          if (typeof data === 'object') {
            errorMessage = data.detail || data.error || data.message || 
                          'Registration failed';
          } else if (typeof data === 'string') {
            errorMessage = data;
          }
        }
        
        console.error('Registration error:', errorMessage);
        throw new Error(errorMessage);
      }
      
      console.log('Registration successful:', data);
      return { success: true, ...data };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  /**
   * Verify user email with verification code
   * @param {string} email - User email
   * @param {string} verificationCode - Email verification code
   * @returns {Promise<Object>} - Verification response
   */
  verifyEmail: async (email, verificationCode) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      console.log('Verifying email:', email);
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to verify email endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/verify-email/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          email,
          verification_code: verificationCode
        }),
        credentials: 'include'
      });
      
      // Get response body
      const responseText = await response.text();
      let data;
      
      try {
        // Try to parse as JSON
        data = responseText ? JSON.parse(responseText) : {};
      } catch (e) {
        // If not JSON, use text as is
        console.warn('Response is not valid JSON:', e);
        data = { message: responseText };
      }
      
      if (!response.ok) {
        // Extract error message from response
        let errorMessage = 'Email verification failed';
        
        if (data) {
          if (typeof data === 'object') {
            errorMessage = data.detail || data.error || data.message || 
                          'Email verification failed';
          } else if (typeof data === 'string') {
            errorMessage = data;
          }
        }
        
        console.error('Email verification error:', errorMessage);
        throw new Error(errorMessage);
      }
      
      console.log('Email verification successful:', data);
      
      // Store authentication data if provided
      if (data.access && data.refresh) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        
        // Store user data if present
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
          localStorage.setItem('lastActivity', Date.now().toString());
        }
        
        // Set auth cookie for server-side auth
        document.cookie = `accessToken=${data.access}; path=/; max-age=86400; SameSite=Strict`;
      }
      
      return { success: true, ...data };
    } catch (error) {
      console.error('Email verification error:', error);
      throw error;
    }
  },
  
  /**
   * Refresh authentication token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} - New tokens
   */
  refreshToken: async (refreshToken = null) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      // If refresh token not provided, try to get from localStorage
      if (!refreshToken) {
        refreshToken = localStorage.getItem('refreshToken');
      }
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to refresh token endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          refresh: refreshToken
        }),
        credentials: 'include'
      });
      
      // Get response body
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }
      
      // Update stored tokens
      if (data.access) {
        localStorage.setItem('accessToken', data.access);
        
        // If a new refresh token is provided, update it too
        if (data.refresh) {
          localStorage.setItem('refreshToken', data.refresh);
        }
        
        // Set auth cookie for server-side auth
        document.cookie = `accessToken=${data.access}; path=/; max-age=86400; SameSite=Strict`;
      }
      
      return data;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  },
  
  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise<Object>} - Reset request response
   */
  requestPasswordReset: async (email) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      console.log('Requesting password reset for:', email);
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to password reset endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/password/reset/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ email }),
        credentials: 'include'
      });
      
      // Get response body
      const data = await response.json();
      
      if (!response.ok) {
        // Extract error message from response
        let errorMessage = data.detail || data.error || data.message || 'Failed to request password reset';
        throw new Error(errorMessage);
      }
      
      return { success: true, ...data };
    } catch (error) {
      console.error('Password reset request error:', error);
      throw error;
    }
  },
  
  /**
   * Reset password with verification code
   * @param {string} email - User email
   * @param {string} resetCode - Password reset code
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Confirm new password
   * @returns {Promise<Object>} - Password reset response
   */
  resetPassword: async (email, resetCode, newPassword, confirmPassword) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      console.log('Resetting password for:', email);
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to password reset confirm endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/password/reset/confirm/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          email,
          reset_code: resetCode,
          new_password: newPassword,
          confirm_password: confirmPassword
        }),
        credentials: 'include'
      });
      
      // Get response body
      const data = await response.json();
      
      if (!response.ok) {
        // Extract error message from response
        let errorMessage = data.detail || data.error || data.message || 'Failed to reset password';
        throw new Error(errorMessage);
      }
      
      // Store authentication data if provided
      if (data.access && data.refresh) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        
        // Store user data if present
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
          localStorage.setItem('lastActivity', Date.now().toString());
        }
        
        // Set auth cookie for server-side auth
        document.cookie = `accessToken=${data.access}; path=/; max-age=86400; SameSite=Strict`;
      }
      
      return { success: true, ...data };
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  },
  
  /**
   * Logout user (invalidate refresh token)
   * @param {string} refreshToken - Refresh token to invalidate
   * @returns {Promise<Object>} - Logout response
   */
  logout: async (refreshToken = null) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      // If refresh token not provided, try to get from localStorage
      if (!refreshToken) {
        refreshToken = localStorage.getItem('refreshToken');
      }
      
      if (!refreshToken) {
        // Return success even if no token to avoid errors
        return { status: 'success', message: 'Already logged out' };
      }
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to logout endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          refresh: refreshToken
        }),
        credentials: 'include'
      });
      
      // Clear stored auth data
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      localStorage.removeItem('lastActivity');
      
      // Clear auth cookie
      document.cookie = 'accessToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      
      if (!response.ok) {
        // Still consider logout successful if clearing local data
        console.warn('Logout API request failed, but local data cleared');
        return { status: 'success', message: 'Logged out locally' };
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Logout error:', error);
      
      // Clear stored auth data even if API call fails
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      localStorage.removeItem('lastActivity');
      
      // Clear auth cookie
      document.cookie = 'accessToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      
      return { status: 'success', message: 'Logged out locally' };
    }
  },
  
  /**
   * Resend verification email
   * @param {string} email - User email
   * @returns {Promise<Object>} - Resend verification response
   */
  resendVerification: async (email) => {
    if (!browser) {
      return Promise.reject(new Error('Authentication is only available in browser environment'));
    }
    
    try {
      console.log('Resending verification email for:', email);
      
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to resend verification endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/resend-verification/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ email }),
        credentials: 'include'
      });
      
      // Get response body
      const data = await response.json();
      
      if (!response.ok) {
        // Extract error message from response
        let errorMessage = data.detail || data.error || data.message || 'Failed to resend verification email';
        throw new Error(errorMessage);
      }
      
      return { success: true, ...data };
    } catch (error) {
      console.error('Resend verification error:', error);
      throw error;
    }
  },
  
  /**
   * Check if token is valid
   * @returns {Promise<boolean>} - Whether token is valid
   */
  isAuthenticated: async () => {
    if (!browser) {
      return false;
    }
    
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      return false;
    }
    
    try {
      // Get API base URL
      const apiBaseUrl = api.getBaseUrl ? api.getBaseUrl() : 'http://localhost:8000/api';
      
      // Make direct fetch to token verify endpoint
      const response = await fetch(`${apiBaseUrl}/accounts/token/verify/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ token: accessToken }),
        credentials: 'include'
      });
      
      return response.ok;
    } catch (error) {
      console.error('Token verification error:', error);
      return false;
    }
  }
};

export default authService;