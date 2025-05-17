// src/lib/api/auth.js
import { API_BASE_URL } from '$lib/constants';
import { user } from '$lib/stores/user';
import { goto } from '$app/navigation';


const AUTH_URL = `${API_BASE_URL}/accounts`;



export async function register(userData) {
  try {
    const response = await fetch(`${AUTH_URL}/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();
    
    // Debug line to see the exact error structure
    console.log("Registration response:", data);

    if (!response.ok) {
      // Handle different error formats properly
      if (data.error) {
        if (typeof data.error === 'string') {
          throw new Error(data.error);
        } else if (typeof data.error.message === 'object') {
          // If it's a validation error object with field-specific messages
          const errorMessages = Object.entries(data.error.message)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ');
          throw new Error(errorMessages);
        } else {
          throw new Error(`${data.error.message || 'Registration failed'}`);
        }
      } else {
        throw new Error('Registration failed with unknown error');
      }
    }

    return data;
  } catch (error) {
    console.error("Registration caught error:", error);
    throw error;
  }
}


export async function login(email, password) {
  const response = await fetch(`${AUTH_URL}/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'Login failed');
  }

  // Store tokens in localStorage
  localStorage.setItem('accessToken', data.data.tokens.access);
  localStorage.setItem('refreshToken', data.data.tokens.refresh);
  
  // Update user store
  user.set(data.data.user);

  return data.data;
}

export async function verifyEmail(email, verificationCode) {
  const response = await fetch(`${AUTH_URL}/verify-email/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, verification_code: verificationCode }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'Verification failed');
  }

  return data;
}

export async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch(`${AUTH_URL}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    const data = await response.json();

    if (!response.ok) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      user.set(null);
      throw new Error(data.error?.message || 'Token refresh failed');
    }

    localStorage.setItem('accessToken', data.data.access);
    return data.data.access;
  } catch (error) {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    user.set(null);
    throw error;
  }
}

export async function fetchUserProfile() {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('No access token available');
    }

    const response = await fetch(`${AUTH_URL}/profile/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        // Try refreshing the token once
        try {
          const newToken = await refreshToken();
          const retryResponse = await fetch(`${AUTH_URL}/profile/`, {
            headers: {
              'Authorization': `Bearer ${newToken}`,
            },
          });

          const retryData = await retryResponse.json();
          
          if (!retryResponse.ok) {
            throw new Error(retryData.error?.message || 'Failed to fetch user profile');
          }
          
          user.set(retryData.data.user);
          return retryData.data.user;
        } catch (refreshError) {
          // If refresh fails, clear auth and redirect to login
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          user.set(null);
          goto('/login');
          throw refreshError;
        }
      }
      
      throw new Error(data.error?.message || 'Failed to fetch user profile');
    }

    user.set(data.data.user);
    return data.data.user;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
}

export async function updateUserProfile(profileData) {
  const token = localStorage.getItem('accessToken');
  
  if (!token) {
    throw new Error('No access token available');
  }

  const response = await fetch(`${AUTH_URL}/profile/`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profileData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'Profile update failed');
  }

  // Update user store with new data
  user.set(data.data.user);
  return data.data.user;
}

export async function changePassword(currentPassword, newPassword, confirmPassword) {
  const token = localStorage.getItem('accessToken');
  
  if (!token) {
    throw new Error('No access token available');
  }

  const response = await fetch(`${AUTH_URL}/password/change/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'Password change failed');
  }

  return data;
}

export async function requestPasswordReset(email) {
  const response = await fetch(`${AUTH_URL}/password/reset/request/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'Password reset request failed');
  }

  return data;
}

export async function resetPassword(email, resetCode, newPassword, confirmPassword) {
  const response = await fetch(`${AUTH_URL}/password/reset/confirm/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      reset_code: resetCode,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'Password reset failed');
  }

  return data;
}

export async function logout() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (refreshToken) {
    try {
      const response = await fetch(`${AUTH_URL}/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        const data = await response.json();
        console.error('Logout error:', data.error?.message);
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  // Regardless of server response, clear local state
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  user.set(null);
}