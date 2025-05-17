// src/lib/api/property.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

// API endpoints (with trailing slashes for Django)
const API = {
  PROPERTIES: `${API_BASE_URL}/properties/`,
  TYPES: {
    PROPERTY: `${API_BASE_URL}/types/property/`,
    BUILDING: `${API_BASE_URL}/types/building/`
  },
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
    
    return { data, status: response.status };
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
  if (data?.detail) return data.detail;
  
  // Handle validation errors
  if (typeof data === 'object') {
    const errors = [];
    for (const [field, message] of Object.entries(data)) {
      if (typeof message === 'string') {
        errors.push(`${field}: ${message}`);
      } else if (Array.isArray(message)) {
        errors.push(`${field}: ${message.join(', ')}`);
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
  
  // Convert property_type and building_type objects to IDs
  if (formatted.property_type && !formatted.property_type_id) {
    formatted.property_type_id = formatted.property_type.id;
    delete formatted.property_type;
  }
  
  if (formatted.building_type && !formatted.building_type_id) {
    formatted.building_type_id = formatted.building_type.id;
    delete formatted.building_type;
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

// CRUD OPERATIONS

/**
 * Get property types
 */
export async function getPropertyTypes() {
  const response = await api(API.TYPES.PROPERTY, { method: 'GET' });
  return response.data;
}

/**
 * Get building types
 */
export async function getBuildingTypes() {
  const response = await api(API.TYPES.BUILDING, { method: 'GET' });
  return response.data;
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
  
  const response = await api(url, { method: 'GET' });
  return response.data;
}

/**
 * Get a single property by ID
 */
export async function getProperty(id) {
  if (!id) throw new Error('Property ID is required');
  const response = await api(`${API.PROPERTIES}${id}/`, { method: 'GET' });
  return response.data;
}

/**
 * Create a new property
 */
export async function createProperty(propertyData) {
  const formattedData = formatPropertyData(propertyData);
  console.log('Creating property:', formattedData);
  
  const response = await api(API.PROPERTIES, {
    method: 'POST',
    body: JSON.stringify(formattedData)
  });
  
  return response;
}

/**
 * Update an existing property
 */
export async function updateProperty(id, propertyData) {
  if (!id) throw new Error('Property ID is required');
  
  const formattedData = formatPropertyData(propertyData);
  const response = await api(`${API.PROPERTIES}${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(formattedData)
  });
  
  return response;
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
  formData.append('content_type_str', 'property'); // Key field for Django ContentType
  formData.append('object_id', propertyId);
  formData.append('is_primary', isPrimary ? 'true' : 'false');
  formData.append('media_type', file.type.startsWith('image/') ? 'image' : 'document');
  formData.append('name', file.name);
  
  console.log(`Uploading media for property ${propertyId}`, {
    file: file.name,
    type: file.type,
    isPrimary
  });
  
  const response = await api(API.MEDIA, {
    method: 'POST',
    body: formData
  });
  
  return response.data;
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