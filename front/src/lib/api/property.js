// src/lib/api/property.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

// API endpoints (with trailing slashes for Django)
const API = {
  PROPERTIES: `${API_BASE_URL}/properties/`,
  MEDIA: `${API_BASE_URL}/media/`
};

/**
 * Base fetch function with auth and error handling
 */
async function api(endpoint, options = {}) {
  // Get token and prepare headers
  const token = localStorage.getItem('accessToken');
  const isFormData = options.body instanceof FormData;
  
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers
  };
  
  // Make the request
  try {
    let response = await fetch(endpoint, { ...options, headers });
    
    // Handle token expiration
    if (response.status === 401 && token) {
      try {
        const newToken = await refreshToken();
        headers.Authorization = `Bearer ${newToken}`;
        response = await fetch(endpoint, { ...options, headers });
      } catch (err) {
        console.error('Token refresh failed:', err);
        throw new Error('Your session has expired. Please log in again.');
      }
    }
    
    // Parse the response
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
    
    // Handle error responses
    if (!response.ok) {
      const message = parseErrorMessage(data);
      throw new Error(message);
    }
    
    return data.data || data;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Parse error messages from Django REST Framework
 */
function parseErrorMessage(data) {
  // Handle string errors
  if (typeof data === 'string') return data;
  
  // Handle DRF's error detail
  if (data?.error?.message) return data.error.message;
  if (data?.detail) return data.detail;
  
  // Handle validation errors
  if (typeof data === 'object') {
    const errors = [];
    
    // Handle nested error object from our custom response format
    if (data.error && typeof data.error === 'object') {
      for (const [field, message] of Object.entries(data.error)) {
        if (typeof message === 'string') {
          errors.push(`${field}: ${message}`);
        } else if (Array.isArray(message)) {
          errors.push(`${field}: ${message.join(', ')}`);
        }
      }
    } else {
      // Handle standard DRF validation errors
      for (const [field, message] of Object.entries(data)) {
        if (typeof message === 'string') {
          errors.push(`${field}: ${message}`);
        } else if (Array.isArray(message)) {
          errors.push(`${field}: ${message.join(', ')}`);
        }
      }
    }
    
    if (errors.length) return errors.join('; ');
  }
  
  return 'An unexpected error occurred';
}

/**
 * Format property data for API submission
 */
function formatPropertyData(data) {
  const formatted = { ...data };
  
  // Handle location data
  if (!formatted.location_data) {
    formatted.location_data = {
      city: formatted.city || '',
      state: formatted.state || '',
      country: formatted.country || 'المملكة العربية السعودية',
      postal_code: formatted.postal_code || '',
      latitude: formatted.latitude,
      longitude: formatted.longitude
    };
    
    // Remove fields now in location_data
    delete formatted.city;
    delete formatted.state;
    delete formatted.postal_code;
    delete formatted.latitude;
    delete formatted.longitude;
    delete formatted.country;
  }
  
  // Convert numeric fields
  ['size_sqm', 'market_value', 'minimum_bid'].forEach(field => {
    if (formatted[field]) formatted[field] = parseFloat(formatted[field]);
  });
  
  ['floors', 'year_built'].forEach(field => {
    if (formatted[field]) formatted[field] = parseInt(formatted[field]);
  });
  
  return formatted;
}

/**
 * Get properties with optional filtering
 */
export async function getProperties(filters = {}) {
  // Build query string from filters
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  });
  
  const queryString = params.toString();
  const url = queryString ? `${API.PROPERTIES}?${queryString}` : API.PROPERTIES;
  
  return await api(url, { method: 'GET' });
}

/**
 * Get a single property by ID
 */
export async function getProperty(id) {
  if (!id) throw new Error('Property ID is required');
  return await api(`${API.PROPERTIES}${id}/`, { method: 'GET' });
}

/**
 * Get a property by slug
 */
export async function getPropertyBySlug(slug) {
  if (!slug) throw new Error('Property slug is required');
  return await api(`${API.PROPERTIES}${slug}/`, { method: 'GET' });
}

/**
 * Create a new property
 */
export async function createProperty(propertyData) {
  const formattedData = formatPropertyData(propertyData);
  
  return await api(API.PROPERTIES, {
    method: 'POST',
    body: JSON.stringify(formattedData)
  });
}

/**
 * Update an existing property
 */
export async function updateProperty(id, propertyData) {
  if (!id) throw new Error('Property ID is required');
  
  const formattedData = formatPropertyData(propertyData);
  
  return await api(`${API.PROPERTIES}${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(formattedData)
  });
}

/**
 * Delete a property
 */
export async function deleteProperty(id) {
  if (!id) throw new Error('Property ID is required');
  return await api(`${API.PROPERTIES}${id}/`, { method: 'DELETE' });
}

/**
 * Upload media for a property
 */

export async function uploadPropertyMedia(propertyId, file, isPrimary = false) {
  if (!propertyId) throw new Error('Property ID is required');
  if (!file) throw new Error('File is required');
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('content_type_str', 'property');
  formData.append('object_id', propertyId);
  formData.append('is_primary', isPrimary ? 'true' : 'false');
  
  // Determine media type based on file MIME type
  let mediaType = 'document';
  if (file.type.startsWith('image/')) {
    mediaType = 'image';
  } else if (file.type.startsWith('video/')) {
    mediaType = 'video';
  }
  formData.append('media_type', mediaType);
  
  formData.append('name', file.name);
  
  const token = localStorage.getItem('accessToken');
  if (!token) {
    throw new Error('Authentication required');
  }
  
  try {
    const response = await fetch(API.MEDIA, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
        // Do NOT set Content-Type here - browser will set it with boundary for FormData
      },
      body: formData
    });
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(API.MEDIA, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${newToken}`
        },
        body: formData
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error?.message || 'Failed to upload media');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to upload media');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Media upload error:', error);
    throw error;
  }
}

/**
 * Upload multiple media files for a property
 */
export async function uploadPropertyMediaBatch(propertyId, files, onProgress) {
  if (!propertyId || !files.length) {
    throw new Error('Property ID and files are required');
  }
  
  const results = [];
  const errors = [];
  let completed = 0;
  const total = files.length;
  
  // Find first image to use as primary
  const firstImage = files.find(f => f.type.startsWith('image/'));
  
  // Upload primary image first if available
  if (firstImage) {
    try {
      const result = await uploadPropertyMedia(propertyId, firstImage, true);
      results.push(result);
    } catch (error) {
      errors.push({ file: firstImage.name, error: error.message });
    } finally {
      completed++;
      if (onProgress) onProgress(completed, total);
    }
  }
  
  // Upload remaining files
  for (const file of files) {
    if (file === firstImage) continue;
    
    try {
      const result = await uploadPropertyMedia(propertyId, file, false);
      results.push(result);
    } catch (error) {
      errors.push({ file: file.name, error: error.message });
    } finally {
      completed++;
      if (onProgress) onProgress(completed, total);
    }
  }
  
  return {
    success: results.length > 0,
    results,
    errors,
    stats: { total, succeeded: results.length, failed: errors.length }
  };
}