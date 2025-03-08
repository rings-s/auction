// Enhanced AuthStore.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { api } from '$lib/api';
import { notificationStore } from '$lib/stores/notificationStore';

// Initialize auth store state
const initialState = {
  user: null,
  isAuthenticated: false,
  isVerified: false,
  primaryRole: null,
  roles: [],
  loading: false,
  error: null,
};

function createAuthStore() {
  // Create writable store with initial state
  const { subscribe, set, update } = writable(initialState);

  // Function to clear tokens and state
  function clearAuth() {
    if (browser) {
      localStorage.removeItem('user');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('lastActivity');
    }
    set(initialState);
  }

  // Function to validate tokens
  async function validateToken() {
    const accessToken = browser ? localStorage.getItem('accessToken') : null;
    
    if (!accessToken) {
      clearAuth();
      return false;
    }
    
    try {
      await api.auth.verifyToken();
      return true;
    } catch (error) {
      console.error('Token validation failed:', error);
      // Don't clear auth immediately - let token refresh attempt to handle it
      if (error.code === 'token_refresh_failed') {
        clearAuth();
      }
      return false;
    }
  }

  // Function to set auth state from tokens and user data
  function setAuthState(userData, accessToken, refreshToken) {
    if (!userData || !accessToken || !refreshToken) {
      console.error('Incomplete auth data provided to setAuthState');
      return false;
    }
    
    // Ensure roles are properly formatted
    const formattedRoles = Array.isArray(userData.roles) 
      ? userData.roles 
      : (userData.roles ? [userData.roles] : []);
    
    if (browser) {
      // Ensure user object always has roles array property
      const userToStore = {
        ...userData,
        roles: formattedRoles
      };
      
      localStorage.setItem('user', JSON.stringify(userToStore));
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('lastActivity', Date.now().toString());
      
      // Set a cookie for server-side auth (read by hooks.server.js)
      document.cookie = `accessToken=${accessToken}; path=/; max-age=86400; SameSite=Strict`;
    }
    
    update(state => ({
      ...state,
      user: userData,
      isAuthenticated: true,
      isVerified: userData.is_verified,
      primaryRole: userData.primary_role,
      roles: formattedRoles,
      loading: false,
      error: null
    }));
    
    return true;
  }
  
  // Try to load auth state from localStorage on initialization (browser-only)
  if (browser) {
    const storedUser = localStorage.getItem('user');
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (storedUser && accessToken && refreshToken) {
      try {
        const user = JSON.parse(storedUser);
        
        // Format roles consistently
        const formattedRoles = Array.isArray(user.roles) 
          ? user.roles 
          : (user.roles ? [user.roles] : []);
        
        // Make sure the parsed user has consistent roles structure
        const formattedUser = {
          ...user,
          roles: formattedRoles
        };
        
        // Set cookie for server-side auth
        document.cookie = `accessToken=${accessToken}; path=/; max-age=86400; SameSite=Strict`;
        
        // Only set authenticated if the user is verified
        update(state => ({
          ...state,
          user: formattedUser,
          isAuthenticated: true,
          isVerified: formattedUser.is_verified,
          primaryRole: formattedUser.primary_role,
          roles: formattedRoles,
        }));
        
        // Validate token silently
        validateToken().catch(() => {});
      } catch (e) {
        console.error('Error parsing stored user:', e);
        clearAuth();
      }
    }
  }

  return {
    subscribe,
    
    /**
     * Register a new user
     */
    register: async (userData) => {
      console.group('User Registration');
      console.log('Starting registration process with data:', userData);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.register(userData);
        console.log('Registration succeeded:', result);
        
        update(state => ({ 
          ...state, 
          loading: false,
        }));
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Registration failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Registration failed' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Verify email with verification code
     */
    verifyEmail: async (email, verificationCode) => {
      console.group('Email Verification');
      console.log('Verifying email:', email);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.verifyEmail(email, verificationCode);
        console.log('Verification succeeded:', result);
        
        // Check if we got the expected data back
        if (!result.access || !result.refresh || !result.user) {
          throw {
            error: 'Invalid server response',
            code: 'invalid_response',
            status: 500
          };
        }
        
        // Set the authentication state
        setAuthState(result.user, result.access, result.refresh);
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Verification failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Email verification failed' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Resend verification email
     */
    resendVerification: async (email) => {
      console.group('Resend Verification');
      console.log('Resending verification for:', email);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.resendVerification(email);
        console.log('Resend verification succeeded:', result);
        
        update(state => ({ ...state, loading: false }));
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Resend verification failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Failed to resend verification email' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Login user
     */
    login: async (email, password) => {
      console.group('User Login');
      console.log('Attempting login for:', email);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.login(email, password);
        console.log('Login succeeded:', result);
        
        // Check if we got the expected data back
        if (!result.access || !result.refresh || !result.user) {
          throw {
            error: 'Invalid server response',
            code: 'invalid_response',
            status: 500
          };
        }
        
        // Check if user is verified - don't allow login if not verified
        if (!result.user.is_verified) {
          throw {
            error: 'Email not verified',
            code: 'email_not_verified',
            status: 401
          };
        }
        
        // Set the authentication state
        setAuthState(result.user, result.access, result.refresh);
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Login failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Login failed' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Logout user
     */
    logout: async () => {
      console.group('User Logout');
      
      update(state => ({ ...state, loading: true }));
      
      try {
        if (browser && localStorage.getItem('refreshToken')) {
          await api.auth.logout();
          console.log('Logout API call succeeded');
        }
      } catch (error) {
        console.error('Logout API call failed:', error);
        // Continue with logout even if API call fails
      } finally {
        // Clear authentication state
        clearAuth();
        
        // Also clear the auth cookie
        if (browser) {
          document.cookie = 'accessToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        }
        
        console.log('Auth state cleared');
        
        // Notify user
        notificationStore.success('You have been logged out successfully');
        
        // Redirect to home
        goto('/');
        
        console.groupEnd();
      }
    },
    
    /**
     * Verify token validity
     */
    verifyAuth: async () => {
      console.group('Verify Auth Token');
      
      try {
        const isValid = await validateToken();
        console.log('Token validation result:', isValid);
        console.groupEnd();
        return isValid;
      } catch (error) {
        console.error('Token validation error:', error);
        console.groupEnd();
        return false;
      }
    },
    
    /**
     * Request password reset code
     */
    requestPasswordReset: async (email) => {
      console.group('Password Reset Request');
      console.log('Requesting password reset for:', email);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.requestPasswordReset(email);
        console.log('Password reset request succeeded:', result);
        
        update(state => ({ 
          ...state, 
          loading: false,
        }));
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Password reset request failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Failed to request password reset' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Verify reset code
     */
    verifyResetCode: async (email, resetCode) => {
      console.group('Verify Reset Code');
      console.log('Verifying reset code for:', email);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.verifyResetCode(email, resetCode);
        console.log('Reset code verification succeeded:', result);
        
        update(state => ({ ...state, loading: false }));
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Reset code verification failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Failed to verify reset code' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Reset password with code
     */
    resetPassword: async (email, resetCode, newPassword, confirmPassword) => {
      console.group('Password Reset');
      console.log('Resetting password for:', email);
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const result = await api.auth.resetPassword(email, resetCode, newPassword, confirmPassword);
        console.log('Password reset succeeded:', result);
        
        // If the reset returns tokens, set them automatically
        if (result.access && result.refresh && result.user) {
          setAuthState(result.user, result.access, result.refresh);
        } else {
          update(state => ({ ...state, loading: false }));
        }
        
        console.groupEnd();
        return result;
      } catch (error) {
        console.error('Password reset failed:', error);
        
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Failed to reset password' 
        }));
        
        console.groupEnd();
        throw error;
      }
    },
    
    /**
     * Reset any errors
     */
    clearError: () => {
      update(state => ({ ...state, error: null }));
    },
    
    /**
     * Update user profile in the store after changes
     */
    updateUserProfile: (userData) => {
      if (!userData) {
        console.error('Invalid user data provided to updateUserProfile');
        return;
      }
      
      // Ensure roles are properly formatted
      const formattedRoles = Array.isArray(userData.roles) 
        ? userData.roles 
        : (userData.roles ? [userData.roles] : []);
      
      const formattedUser = {
        ...userData,
        roles: formattedRoles
      };
      
      if (browser) {
        localStorage.setItem('user', JSON.stringify(formattedUser));
      }
      
      update(state => ({ 
        ...state, 
        user: formattedUser,
        primaryRole: formattedUser.primary_role,
        roles: formattedRoles
      }));
    },
    
    /**
     * Function to refresh auth state - useful when user refreshes the page
     */
    refreshState: () => {
      if (!browser) return;
      
      const storedUser = localStorage.getItem('user');
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (storedUser && accessToken && refreshToken) {
        try {
          const user = JSON.parse(storedUser);
          
          // Format roles consistently
          const formattedRoles = Array.isArray(user.roles) 
            ? user.roles 
            : (user.roles ? [user.roles] : []);
          
          // Make sure the parsed user has consistent roles structure
          const formattedUser = {
            ...user,
            roles: formattedRoles
          };
          
          // Set cookie for server-side auth
          document.cookie = `accessToken=${accessToken}; path=/; max-age=86400; SameSite=Strict`;
          
          update(state => ({
            ...state,
            user: formattedUser,
            isAuthenticated: true,
            isVerified: formattedUser.is_verified,
            primaryRole: formattedUser.primary_role,
            roles: formattedRoles,
          }));
          
          // Validate token silently
          validateToken().catch(() => {});
          
          return true;
        } catch (e) {
          console.error('Error refreshing auth state:', e);
          clearAuth();
          return false;
        }
      }
      
      return false;
    }
  };
}

// Create and export the auth store
export const authStore = createAuthStore();

// Derived stores for convenience
export const user = derived(authStore, $auth => $auth.user);
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const isVerified = derived(authStore, $auth => $auth.isVerified);
export const primaryRole = derived(authStore, $auth => $auth.primaryRole);
export const roles = derived(authStore, $auth => $auth.roles);
export const hasRole = (role) => derived(authStore, $auth => 
  $auth.roles && $auth.roles.some(r => {
    // Handle both object roles and string roles
    if (typeof r === 'string') return r === role;
    if (r && r.code) return r.code === role;
    return false;
  })
);