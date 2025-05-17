// src/lib/utils/api.js

import { refreshToken } from '$lib/api/auth';
import { goto } from '$app/navigation';

export async function authenticatedFetch(url, options = {}) {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    goto('/login');
    return null;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...options.headers
  };

  try {
    let response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      // Try token refresh
      try {
        const newToken = await refreshToken();
        headers.Authorization = `Bearer ${newToken}`;
        response = await fetch(url, { ...options, headers });
        
        if (!response.ok) {
          goto('/login');
          return null;
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        goto('/login');
        return null;
      }
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    return null;
  }
}