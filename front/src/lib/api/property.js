// src/lib/api/property.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

// API endpoints (with trailing slashes for Django)
const API = {
  PROPERTIES: `${API_BASE_URL}/properties/`,
  MEDIA: `${API_BASE_URL}/media/`,
  ROOMS: `${API_BASE_URL}/rooms/`
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
    throw error;
  }
}

/**
 * Helper function to extract error details from response
 */
async function extractErrorResponse(response) {
  try {
    const contentType = response.headers.get('content-type');
    let errorData = { status: response.status };
    
    if (contentType && contentType.includes('application/json')) {
      const jsonData = await response.json();
      errorData.data = jsonData;
      
      // Handle different error formats
      if (jsonData.error && jsonData.error.message) {
        errorData.message = jsonData.error.message;
      } else if (jsonData.detail) {
        errorData.message = jsonData.detail;
      } else if (jsonData.non_field_errors) {
        errorData.message = jsonData.non_field_errors.join(', ');
      } else {
        // Try to extract first error message from validation errors
        const firstError = Object.entries(jsonData)
          .filter(([key, value]) => key !== 'status' && value)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
          .join('; ');
          
        errorData.message = firstError || 'Unknown error occurred';
      }
    } else {
      // For non-JSON responses, get text content
      errorData.message = await response.text() || `HTTP error! status: ${response.status}`;
    }
    
    return errorData;
  } catch (parseError) {
    return { 
      status: response.status, 
      message: `Failed to parse error response. Status: ${response.status}`
    };
  }
}

/**
 * Parse error messages from Django REST Framework
 */
function parseErrorMessage(data) {
  // Handle string errors
  if (typeof data === 'string') return data;
  
  // Handle DRF's error detail (checking for data before accessing properties)
  if (data && data.error && typeof data.error.message === 'string') return data.error.message;
  if (data && typeof data.detail === 'string') return data.detail;
  
  // Handle validation errors (ensure data is a non-null, non-array object)
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    const errors = [];
    for (const key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        // Ensure data[key] is not null or undefined before trying to join or convert to string
        const value = data[key];
        if (value !== null && value !== undefined) {
          if (Array.isArray(value)) {
            errors.push(`${key}: ${value.join(', ')}`);
          } else {
            errors.push(`${key}: ${String(value)}`);
          }
        }
      }
    }
    if (errors.length > 0) return errors.join('; ');
    
    // Fallback for empty objects or objects not matching the above structure
    if (Object.keys(data).length === 0) return 'Error: Received an empty error object.';
    return JSON.stringify(data); 
  }
  
  return 'An unknown error occurred';
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
    if (formatted[field] !== undefined && formatted[field] !== null && formatted[field] !== '') {
      formatted[field] = parseFloat(formatted[field]);
    }
  });
  
  ['floors', 'year_built'].forEach(field => {
    if (formatted[field] !== undefined && formatted[field] !== null && formatted[field] !== '') {
      formatted[field] = parseInt(formatted[field], 10);
    }
  });
  
  // Ensure rooms have proper data types if present
  if (formatted.rooms && Array.isArray(formatted.rooms)) {
    formatted.rooms = formatted.rooms.map(room => {
      const formattedRoom = { ...room };
      
      // Convert room numeric fields
      if (formattedRoom.area_sqm) {
        formattedRoom.area_sqm = parseFloat(formattedRoom.area_sqm);
      }
      
      if (formattedRoom.floor) {
        formattedRoom.floor = parseInt(formattedRoom.floor, 10);
      }
      
      return formattedRoom;
    });
  }
  
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
  
  try {
    // Properly encode the slug to handle Arabic and other non-ASCII characters
    const encodedSlug = encodeURIComponent(slug);
    
    // Make the API request with the encoded slug
    return await api(`${API.PROPERTIES}${encodedSlug}/`, { method: 'GET' });
  } catch (error) {
    throw error;
  }
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
 * Upload a single media file for a property
 */
export async function uploadPropertyMedia(propertyId, file, isPrimary = false) {
  if (!propertyId) throw new Error('Property ID is required');
  if (!file) throw new Error('File is required');
  
  const formData = new FormData();
  formData.append('file', file);
  
  // Use the fully qualified content type format to ensure correct resolution
  formData.append('content_type_str', 'base.property');
  formData.append('object_id', propertyId);
  formData.append('is_primary', isPrimary ? 'true' : 'false');
  
  // Determine media type based on file MIME type and extension
  let mediaType = 'other';
  if (file.type && file.type.startsWith('image/')) {
    mediaType = 'image';
  } else if (file.type && file.type.startsWith('video/')) {
    mediaType = 'video';
  } else if (file.type === 'application/pdf' || (file.name && file.name.toLowerCase().endsWith('.pdf'))) {
    mediaType = 'document';
  }
  
  formData.append('media_type', mediaType);
  
  // Set name if file has one
  formData.append('name', file.name || `file-${Date.now()}`);
  
  const token = localStorage.getItem('accessToken');
  if (!token) {
    throw new Error('Authentication required');
  }
  
  // Add a retry mechanism for better reliability
  let retries = 0;
  const maxRetries = 2;
  
  while (retries <= maxRetries) {
    try {
      const response = await fetch(API.MEDIA, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
          // Do NOT set Content-Type here - browser will set with boundary
        },
        body: formData
      });
      
      // Handle non-200 responses with better error messages
      if (!response.ok) {
        const errorData = await extractErrorResponse(response);
        
        // If we have retries left, try again after a delay
        if (retries < maxRetries) {
          retries++;
          // Exponential backoff: 1s, 2s, 4s, etc.
          const delay = Math.pow(2, retries) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
        
        throw new Error(errorData.message || `Upload failed with status ${response.status}`);
      }
      
      // Success!
      const result = await response.json();
      return result;
    } catch (error) {
      // If this is our last retry, or it's a client-side error (not network related)
      const isTypeError = error && typeof error === 'object' && error.name === 'TypeError';
      if (retries >= maxRetries || !isTypeError) {
        throw error;
      }
      
      retries++;
      const delay = Math.pow(2, retries) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
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
  const firstImage = files.find(f => f && f.type && f.type.startsWith('image/'));
  
  // Upload primary image first if available
  if (firstImage) {
    try {
      const result = await uploadPropertyMedia(propertyId, firstImage, true);
      results.push(result);
    } catch (error) {
      // Get error message safely without TypeScript instanceof
      const errorMessage = error && error.message ? error.message : 'Unknown error';
      errors.push({ file: firstImage.name, error: errorMessage });
    } finally {
      completed++;
      if (onProgress) onProgress(completed, total);
    }
  }
  
  // Upload remaining files with a small delay between uploads
  for (const file of files) {
    if (file === firstImage) continue;
    
    try {
      // Add a small delay between uploads to prevent server overload
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const result = await uploadPropertyMedia(propertyId, file, false);
      results.push(result);
    } catch (error) {
      // Get error message safely without TypeScript instanceof
      const errorMessage = error && error.message ? error.message : 'Unknown error';
      errors.push({ file: file.name, error: errorMessage });
    } finally {
      completed++;
      if (onProgress) onProgress(completed, total);
    }
  }
  
  // If all uploads failed, throw an error to notify the caller
  if (results.length === 0 && errors.length > 0) {
    throw new Error(`All ${errors.length} media uploads failed. Check console for details.`);
  }
  
  return {
    success: results.length > 0,
    results,
    errors,
    stats: { total, succeeded: results.length, failed: errors.length }
  };
}

/**
 * Set a media item as primary for a property
 */
export async function setPropertyMediaPrimary(mediaId) {
  if (!mediaId) throw new Error('Media ID is required');
  
  return await api(`${API.MEDIA}${mediaId}/`, {
    method: 'PATCH',
    body: JSON.stringify({ is_primary: true })
  });
}

/**
 * Delete a property media item
 */
export async function deletePropertyMedia(mediaId) {
  if (!mediaId) throw new Error('Media ID is required');
  
  return await api(`${API.MEDIA}${mediaId}/`, {
    method: 'DELETE'
  });
}

/**
 * Add a room to a property
 */
export async function addPropertyRoom(propertyId, roomData) {
  if (!propertyId) throw new Error('Property ID is required');
  
  const formatted = { ...roomData, property: propertyId };
  
  // Convert numeric fields
  if (formatted.area_sqm) {
    formatted.area_sqm = parseFloat(formatted.area_sqm);
  }
  
  if (formatted.floor) {
    formatted.floor = parseInt(formatted.floor, 10);
  }
  
  return await api(API.ROOMS, {
    method: 'POST',
    body: JSON.stringify(formatted)
  });
}

/**
 * Update a property room
 */
export async function updatePropertyRoom(roomId, roomData) {
  if (!roomId) throw new Error('Room ID is required');
  
  const formatted = { ...roomData };
  
  // Convert numeric fields
  if (formatted.area_sqm) {
    formatted.area_sqm = parseFloat(formatted.area_sqm);
  }
  
  if (formatted.floor) {
    formatted.floor = parseInt(formatted.floor, 10);
  }
  
  return await api(`${API.ROOMS}${roomId}/`, {
    method: 'PATCH',
    body: JSON.stringify(formatted)
  });
}

/**
 * Delete a property room
 */
export async function deletePropertyRoom(roomId) {
  if (!roomId) throw new Error('Room ID is required');
  
  return await api(`${API.ROOMS}${roomId}/`, {
    method: 'DELETE'
  });
}

/**
 * Upload media for a property room
 */
export async function uploadRoomMedia(roomId, file, isPrimary = false) {
  if (!roomId) throw new Error('Room ID is required');
  if (!file) throw new Error('File is required');
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('content_type_str', 'base.room');
  formData.append('object_id', roomId);
  formData.append('is_primary', isPrimary ? 'true' : 'false');
  
  // Determine media type based on file MIME type
  let mediaType = 'document';
  if (file.type.startsWith('image/')) {
    mediaType = 'image';
  } else if (file.type.startsWith('video/')) {
    mediaType = 'video';
  }
  formData.append('media_type', mediaType);
  
  formData.append('name', file.name || `room-file-${Date.now()}`);
  
  const token = localStorage.getItem('accessToken');
  if (!token) {
    throw new Error('Authentication required');
  }
  
  try {
    const response = await fetch(API.MEDIA, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    if (response.status === 401) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(API.MEDIA, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${newToken}`
        },
        body: formData
      });
      
      if (!retryResponse.ok) {
        const errorData = await extractErrorResponse(retryResponse);
        throw new Error(errorData.message || 'Failed to upload room media');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await extractErrorResponse(response);
      throw new Error(errorData.message || 'Failed to upload room media');
    }
    
    return await response.json();
  } catch (error) {
    throw error;
  }
}

/**
 * Get featured properties
 */
export async function getFeaturedProperties(limit = 6) {
  return await getProperties({ is_featured: true, limit });
}

/**
 * Search properties
 */
export async function searchProperties(query) {
  return await getProperties({ search: query });
}

/**
 * Get properties by type
 */
export async function getPropertiesByType(propertyType) {
  return await getProperties({ property_type: propertyType });
}

/**
 * Get property statistics (for dashboards)
 */
export async function getPropertyStats() {
  return await api(`${API_BASE_URL}/property-stats/`, { method: 'GET' });
}