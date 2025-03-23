// src/lib/stores/auth.js
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { jwtDecode } from 'jwt-decode';
import authService from '$lib/services/auth';
import { toast } from '$lib/stores/toast';
import api from '$lib/services/api';

// Default auth state
const defaultState = {
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  tokenExpiry: null,
  roles: [],
  isLoading: false,
  error: null
};

// Create the auth store with initial state
const createAuthStore = () => {
  // Function to get initial state - only runs in browser
  function getInitialState() {
    if (!browser) return defaultState;
    
    try {
      const storedAuth = localStorage.getItem('auth');
      if (storedAuth) {
        const parsedAuth = JSON.parse(storedAuth);

        // Validate the token format
        if (!parsedAuth || !parsedAuth.token || typeof parsedAuth.token !== 'string') {
          console.warn('Invalid token format in localStorage');
          localStorage.removeItem('auth');
          return defaultState;
        }

        // Check if token is expired
        try {
          if (parsedAuth.token) {
            const decoded = jwtDecode(parsedAuth.token);
            const currentTime = Date.now() / 1000;

            // Extra validation
            if (!decoded || !decoded.exp) {
              console.warn('Token missing expiration');
              localStorage.removeItem('auth');
              return defaultState;
            }

            if (decoded.exp < currentTime) {
              // Token expired, clear storage
              console.warn('Token expired');
              localStorage.removeItem('auth');
              return defaultState;
            }

            // Update expiry time
            parsedAuth.tokenExpiry = decoded.exp;
          }
        } catch (decodeError) {
          console.error('Error decoding JWT token:', decodeError);
          localStorage.removeItem('auth');
          return defaultState;
        }

        return { ...defaultState, ...parsedAuth };
      }
    } catch (error) {
      console.error('Error parsing auth data from localStorage:', error);
      if (browser) localStorage.removeItem('auth');
    }

    return defaultState;
  }

  // Create the writable store
  const store = writable(getInitialState());
  
  // Create derived stores
  const isAuthenticated = derived(store, $store => $store.isAuthenticated);
  const currentUser = derived(store, $store => $store.user);
  const userRoles = derived(store, $store => $store.roles || []);
  const isLoading = derived(store, $store => $store.isLoading);
  const authError = derived(store, $store => $store.error);

  // Function to save auth state to localStorage
  const saveAuthState = (state) => {
    if (!browser) return;
    
    try {
      // Only save necessary fields to avoid clutter
      const authData = {
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        tokenExpiry: state.tokenExpiry,
        roles: state.roles
      };
      
      localStorage.setItem('auth', JSON.stringify(authData));
    } catch (error) {
      console.error('Error saving auth state:', error);
    }
  };

  // Auth store with methods
  const authStore = {
    subscribe: store.subscribe,
    
    // Getter for the current state (useful for other modules)
    getState: () => get(store),

    // Initialize auth store (safe to call on both server and client)
    initialize: () => {
      if (browser) {
        // Re-evaluate initial state, which will properly check localStorage
        const initialState = getInitialState();
        store.set(initialState);
        
        // If we have a token, verify it with the server
        if (initialState.isAuthenticated && initialState.token) {
          // Silently validate the token
          authService.isAuthenticated()
            .catch(error => {
              console.warn('Token validation failed:', error);
              // Clear auth data if token is invalid
              api.clearAuthData();
              store.set(defaultState);
            });
        }
      }
    },

    /**
     * Login with email and password
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} - Result of login attempt
     */
    login: async (email, password) => {
      store.update(state => ({ ...state, isLoading: true, error: null }));

      try {
        console.log("Starting login process for:", email);
        
        // Prepare the login data with multiple formats to handle different backend expectations
        const loginData = {
          email: email.trim(),        // Django DRF may expect 'email'
          username: email.trim(),     // Django may expect 'username'
          password: password          // Password is always 'password'
        };
        
        console.log("Sending login request with data:", { 
          ...loginData, 
          password: '******' 
        });
        
        const response = await authService.login(email, password);
        console.log("Login response processed:", { 
          hasAccess: !!response.access, 
          hasRefresh: !!response.refresh
        });

        // Check for token in various possible response formats
        // Django REST framework and SimpleJWT might return tokens in different formats
        let accessToken, refreshToken;

        if (response.access && response.refresh) {
          // Standard SimpleJWT format
          accessToken = response.access;
          refreshToken = response.refresh;
        } else if (response.token && response.refresh_token) {
          // Alternative format
          accessToken = response.token;
          refreshToken = response.refresh_token;
        } else if (response.token && response.token.access) {
          // Nested format
          accessToken = response.token.access;
          refreshToken = response.token.refresh;
        } else if (response.data && response.data.access) {
          // Response within data object
          accessToken = response.data.access;
          refreshToken = response.data.refresh;
        } else if (response.key) {
          // Django REST Auth format
          accessToken = response.key;
          refreshToken = response.key; // Some implementations use the same token
        }

        if (!accessToken) {
          console.error("No valid tokens found in response:", response);
          throw new Error('Invalid credentials or token format not recognized');
        }

        // Decode JWT to get user info
        let decodedPayload;
        try {
          decodedPayload = jwtDecode(accessToken);
          console.log("Decoded JWT payload:", decodedPayload);
        } catch (decodeError) {
          console.warn("Error decoding JWT, might be using a different token format:", decodeError);
          // If we can't decode the JWT, create a minimal payload
          // This handles cases where the token might not be a standard JWT
          decodedPayload = {
            exp: Math.floor(Date.now() / 1000) + 3600, // Default 1 hour expiry
            user_id: response.user_id || response.id || 'unknown'
          };
        }
        
        if (!decodedPayload || !decodedPayload.exp) {
          console.warn("Creating default expiry time for token");
          decodedPayload = {
            ...decodedPayload,
            exp: Math.floor(Date.now() / 1000) + 3600 // Default 1 hour expiry
          };
        }

        // Extract user information from token or response
        const userData = {
          id: decodedPayload.user_id || response.user_id || response.id || 'unknown',
          email: decodedPayload.email || response.email || email,
          firstName: decodedPayload.first_name || response.first_name || '',
          lastName: decodedPayload.last_name || response.last_name || '',
          tokenExpiry: decodedPayload.exp
        };

        const authData = {
          isAuthenticated: true,
          user: userData,
          token: accessToken,
          refreshToken: refreshToken,
          tokenExpiry: decodedPayload.exp,
          roles: decodedPayload.roles || response.roles || [],
          isLoading: false,
          error: null
        };

        // Update store
        store.set(authData);
        
        // Save to local storage
        saveAuthState(authData);
        
        // For backward compatibility
        if (browser) {
          localStorage.setItem('accessToken', accessToken);
          localStorage.setItem('refreshToken', refreshToken);
        }

        return { success: true };
      } catch (error) {
        console.error("Login error:", error);
        const errorMessage = error.message || 'An error occurred during login';

        store.update(state => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));

        return { success: false, error: errorMessage };
      }
    },

    /**
     * Register a new user
     * @param {Object} userData - User registration data
     * @returns {Promise<Object>} - Result of registration attempt
     */
    register: async (userData) => {
      store.update(state => ({ ...state, isLoading: true, error: null }));

      try {
        // Ensure both password field formats are included for backend compatibility
        if (userData.password && !userData.password_confirmation && userData.confirm_password) {
          userData.password_confirmation = userData.confirm_password;
        } else if (userData.password && !userData.confirm_password && userData.password_confirmation) {
          userData.confirm_password = userData.password_confirmation;
        }
        
        const response = await authService.register(userData);

        store.update(state => ({ ...state, isLoading: false }));

        return { success: true, data: response };
      } catch (error) {
        const errorMessage = error.message || 'An error occurred during registration';

        store.update(state => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));

        if (browser) {
          toast.error(errorMessage);
        }

        return { success: false, error: errorMessage };
      }
    },

    /**
     * Verify user email with verification code
     * @param {string} email - User email
     * @param {string} code - Verification code
     * @returns {Promise<Object>} - Result of verification attempt
     */
    verifyEmail: async (email, code) => {
      store.update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response = await authService.verifyEmail(email, code);

        // Check if response includes tokens (auto-login)
        let accessToken, refreshToken;
        
        if (response.access && response.refresh) {
          accessToken = response.access;
          refreshToken = response.refresh;
        } else if (response.token && response.refresh_token) {
          accessToken = response.token;
          refreshToken = response.refresh_token;
        } else if (response.key) {
          accessToken = response.key;
          refreshToken = response.key;
        }
        
        if (accessToken && refreshToken) {
          try {
            let decodedPayload;
            try {
              decodedPayload = jwtDecode(accessToken);
            } catch (decodeError) {
              console.warn("Error decoding JWT during verification:", decodeError);
              decodedPayload = {
                exp: Math.floor(Date.now() / 1000) + 3600,
                user_id: response.user_id || response.id || 'unknown'
              };
            }
            
            if (!decodedPayload || !decodedPayload.exp) {
              decodedPayload = {
                ...decodedPayload,
                exp: Math.floor(Date.now() / 1000) + 3600
              };
            }

            // Extract user information
            const userData = {
              id: decodedPayload.user_id || response.user_id || response.id || 'unknown',
              email: decodedPayload.email || response.email || email,
              firstName: decodedPayload.first_name || response.first_name || '',
              lastName: decodedPayload.last_name || response.last_name || '',
              tokenExpiry: decodedPayload.exp
            };

            const authData = {
              isAuthenticated: true,
              user: userData,
              token: accessToken,
              refreshToken: refreshToken,
              tokenExpiry: decodedPayload.exp,
              roles: decodedPayload.roles || response.roles || [],
              isLoading: false,
              error: null
            };

            // Update store
            store.set(authData);
            
            // Save to local storage
            saveAuthState(authData);
            
            // For backward compatibility
            if (browser) {
              localStorage.setItem('accessToken', accessToken);
              localStorage.setItem('refreshToken', refreshToken);
            }
          } catch (decodeError) {
            console.error('Error processing tokens after verification:', decodeError);
            store.update(state => ({ ...state, isLoading: false }));
          }
        } else {
          store.update(state => ({ ...state, isLoading: false }));
        }

        return { success: true };
      } catch (error) {
        const errorMessage = error.message || 'An error occurred during email verification';

        store.update(state => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));

        return { success: false, error: errorMessage };
      }
    },

    /**
     * Log out the current user
     */
    logout: () => {
      let currentState = get(store);
      
      store.update(state => ({
        ...defaultState, 
        isLoading: true
      }));

      // Call logout API to invalidate the token
      if (browser && currentState.refreshToken) {
        authService.logout(currentState.refreshToken)
          .catch(err => console.error('Error during logout:', err))
          .finally(() => {
            // Reset store
            store.set(defaultState);
            
            // Clear localStorage
            localStorage.removeItem('auth');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            
            // Redirect to login page
            goto('/auth/login');
          });
      } else {
        // Reset store
        store.set(defaultState);
        
        if (browser) {
          // Clear localStorage
          localStorage.removeItem('auth');
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        }
        
        // Redirect to login page
        goto('/auth/login');
      }
    },

    /**
     * Refresh the auth token
     * @returns {Promise<Object>} - Result of refresh attempt
     */
    refreshToken: async () => {
      let currentState = get(store);
      
      if (!currentState.refreshToken) {
        return { success: false, error: 'No refresh token available' };
      }

      store.update(state => ({ ...state, isLoading: true }));

      try {
        const response = await authService.refreshToken(currentState.refreshToken);

        // Check different token formats
        let accessToken;
        if (response.access) {
          accessToken = response.access;
        } else if (response.token) {
          accessToken = response.token;
        } else if (response.key) {
          accessToken = response.key;
        }

        if (!accessToken) {
          throw new Error('Failed to refresh token - invalid response format');
        }

        // Decode new token
        let decodedPayload;
        try {
          decodedPayload = jwtDecode(accessToken);
        } catch (decodeError) {
          console.warn("Error decoding JWT during refresh:", decodeError);
          decodedPayload = {
            exp: Math.floor(Date.now() / 1000) + 3600,
            user_id: currentState.user?.id || 'unknown'
          };
        }
        
        if (!decodedPayload || !decodedPayload.exp) {
          decodedPayload = {
            ...decodedPayload,
            exp: Math.floor(Date.now() / 1000) + 3600
          };
        }

        const authData = {
          ...currentState,
          token: accessToken,
          tokenExpiry: decodedPayload.exp,
          isLoading: false,
          error: null
        };

        // Update user tokenExpiry
        if (authData.user) {
          authData.user.tokenExpiry = decodedPayload.exp;
        }

        // Update store
        store.set(authData);
        
        // Save to local storage
        saveAuthState(authData);
        
        // For backward compatibility
        if (browser) {
          localStorage.setItem('accessToken', accessToken);
        }

        return { success: true };
      } catch (error) {
        console.error('Token refresh failed:', error);

        // Don't immediately log out on refresh failure, just update the error
        store.update(state => ({ 
          ...state, 
          isLoading: false,
          error: 'Failed to refresh session'
        }));

        return { success: false, error: 'Failed to refresh session. Please log in again.' };
      }
    },

    /**
     * Request a password reset
     * @param {string} email - User email
     * @returns {Promise<Object>} - Result of reset request
     */
    requestPasswordReset: async (email) => {
      store.update(state => ({ ...state, isLoading: true, error: null }));

      try {
        await authService.requestPasswordReset(email);

        store.update(state => ({ ...state, isLoading: false }));

        return { success: true };
      } catch (error) {
        const errorMessage = error.message || 'An error occurred while requesting password reset';

        store.update(state => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));

        return { success: false, error: errorMessage };
      }
    },

    /**
     * Reset password with code
     * @param {string} email - User email
     * @param {string} resetCode - Reset code
     * @param {string} newPassword - New password
     * @param {string} confirmPassword - Confirm password
     * @returns {Promise<Object>} - Result of password reset
     */
    resetPassword: async (email, resetCode, newPassword, confirmPassword) => {
      store.update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response = await authService.resetPassword(
          email,
          resetCode,
          newPassword,
          confirmPassword
        );

        // Check if response includes tokens (auto-login)
        let accessToken, refreshToken;
        
        if (response.access && response.refresh) {
          accessToken = response.access;
          refreshToken = response.refresh;
        } else if (response.token && response.refresh_token) {
          accessToken = response.token;
          refreshToken = response.refresh_token;
        } else if (response.key) {
          accessToken = response.key;
          refreshToken = response.key;
        }
        
        if (accessToken && refreshToken) {
          try {
            // Process token and user data similar to login
            let decodedPayload;
            try {
              decodedPayload = jwtDecode(accessToken);
            } catch (decodeError) {
              console.warn("Error decoding JWT after password reset:", decodeError);
              decodedPayload = {
                exp: Math.floor(Date.now() / 1000) + 3600,
                user_id: response.user_id || response.id || 'unknown'
              };
            }
            
            if (!decodedPayload || !decodedPayload.exp) {
              decodedPayload = {
                ...decodedPayload,
                exp: Math.floor(Date.now() / 1000) + 3600
              };
            }

            // Extract user information
            const userData = {
              id: decodedPayload.user_id || response.user_id || response.id || 'unknown',
              email: decodedPayload.email || response.email || email,
              firstName: decodedPayload.first_name || response.first_name || '',
              lastName: decodedPayload.last_name || response.last_name || '',
              tokenExpiry: decodedPayload.exp
            };

            const authData = {
              isAuthenticated: true,
              user: userData,
              token: accessToken,
              refreshToken: refreshToken,
              tokenExpiry: decodedPayload.exp,
              roles: decodedPayload.roles || response.roles || [],
              isLoading: false,
              error: null
            };

            // Update store
            store.set(authData);
            
            // Save to local storage
            saveAuthState(authData);
            
            // For backward compatibility
            if (browser) {
              localStorage.setItem('accessToken', accessToken);
              localStorage.setItem('refreshToken', refreshToken);
            }
          } catch (decodeError) {
            console.error('Error processing tokens after password reset:', decodeError);
            store.update(state => ({ ...state, isLoading: false }));
          }
        } else {
          store.update(state => ({ ...state, isLoading: false }));
        }

        return { success: true };
      } catch (error) {
        const errorMessage = error.message || 'An error occurred while resetting password';

        store.update(state => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));

        return { success: false, error: errorMessage };
      }
    },

    /**
     * Check if current user has a specific role
     * @param {string} role - Role to check
     * @returns {boolean} - True if user has the role
     */
    hasRole: (role) => {
      const state = get(store);
      return state.roles?.includes(role) || false;
    },

    /**
     * Check if current user has any of the specified roles
     * @param {Array<string>} roles - Array of roles to check
     * @returns {boolean} - True if user has any of the roles
     */
    hasAnyRole: (roles) => {
      const state = get(store);
      return roles.some(role => state.roles?.includes(role));
    },

    /**
     * Clear any error in the store
     */
    clearError: () => {
      store.update(state => ({ ...state, error: null }));
    },

    /**
     * Set a custom error
     * @param {string} error - Error message
     */
    setError: (error) => {
      store.update(state => ({ ...state, error }));
    }
  };

  return {
    store,
    authStore,
    isAuthenticated,
    currentUser,
    userRoles,
    isLoading,
    authError
  };
};

// Create and export the auth store and derived stores
const { authStore, isAuthenticated, currentUser, userRoles, isLoading, authError } = createAuthStore();

// Initialize the auth store if in browser
if (browser) {
  // Safe to initialize immediately since we're using a factory function
  authStore.initialize();
}

export { authStore, isAuthenticated, currentUser, userRoles, isLoading, authError };
export default authStore;