// front/src/lib/api/messages.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const MESSAGES_URL = `${API_BASE_URL}/messages/`;

/**
 * Enhanced API request handler with better error handling
 */
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('accessToken');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };

  const requestOptions = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  console.log(`Messages API Request: ${options.method || 'GET'} ${url}`);

  try {
    let response = await fetch(url, requestOptions);
    
    // Handle token refresh for 401 responses
    if (response.status === 401 && token) {
      console.log('Token expired, attempting refresh...');
      try {
        const newToken = await refreshToken();
        requestOptions.headers.Authorization = `Bearer ${newToken}`;
        response = await fetch(url, requestOptions);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        throw new Error('Your session has expired. Please log in again.');
      }
    }

    // Parse response data
    let data;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    console.log(`Messages API Response (${response.status}):`, data);

    // Handle error responses
    if (!response.ok) {
      const errorMessage = extractErrorMessage(data, response.status);
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`Messages API Error (${url}):`, error);
    throw error;
  }
}

/**
 * Extract error message from different response formats
 */
function extractErrorMessage(data, status) {
  if (typeof data === 'string') {
    return data || `HTTP Error ${status}`;
  }

  if (data && typeof data === 'object') {
    if (data.error && data.error.message) {
      return data.error.message;
    }
    
    if (data.error && typeof data.error === 'string') {
      return data.error;
    }

    if (data.detail) {
      return data.detail;
    }

    if (data.message) {
      return data.message;
    }

    // Handle validation errors
    const validationErrors = [];
    for (const [field, messages] of Object.entries(data)) {
      if (field !== 'error' && field !== 'message' && field !== 'detail') {
        if (Array.isArray(messages)) {
          validationErrors.push(`${field}: ${messages.join(', ')}`);
        } else if (typeof messages === 'string') {
          validationErrors.push(`${field}: ${messages}`);
        }
      }
    }

    if (validationErrors.length > 0) {
      return validationErrors.join('; ');
    }
  }

  return `HTTP Error ${status}`;
}

/**
 * Get messages with filtering options
 */
export async function getMessages(filters = {}) {
  const queryParams = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  const url = `${MESSAGES_URL}?${queryParams.toString()}`;
  return await apiRequest(url, { method: 'GET' });
}

/**
 * Get a single message by ID
 */
export async function getMessage(id, includeThread = false) {
  if (!id) throw new Error('Message ID is required');
  
  const queryParams = includeThread ? '?include_thread=true' : '';
  return await apiRequest(`${MESSAGES_URL}${id}/${queryParams}`, { method: 'GET' });
}

/**
 * Send a new message
 */
export async function sendMessage(messageData) {
  if (!messageData) throw new Error('Message data is required');
  
  return await apiRequest(MESSAGES_URL, {
    method: 'POST',
    body: JSON.stringify(messageData)
  });
}

/**
 * Reply to a message
 */
export async function replyToMessage(messageId, replyData) {
  if (!messageId) throw new Error('Message ID is required');
  if (!replyData) throw new Error('Reply data is required');
  
  return await apiRequest(`${MESSAGES_URL}${messageId}/reply/`, {
    method: 'POST',
    body: JSON.stringify({
      ...replyData,
      parent_message: messageId
    })
  });
}

/**
 * Update message status
 */
export async function updateMessageStatus(id, status) {
  if (!id) throw new Error('Message ID is required');
  if (!status) throw new Error('Status is required');
  
  return await apiRequest(`${MESSAGES_URL}${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
}

/**
 * Mark message as read
 */
export async function markMessageAsRead(id) {
  return await updateMessageStatus(id, 'read');
}

/**
 * Mark message as archived
 */
export async function archiveMessage(id) {
  return await updateMessageStatus(id, 'archived');
}

/**
 * Get message thread
 */
export async function getMessageThread(threadId) {
  if (!threadId) throw new Error('Thread ID is required');
  
  return await apiRequest(`${MESSAGES_URL}thread/${threadId}/`, { method: 'GET' });
}

/**
 * Get message statistics
 */
export async function getMessageStats() {
  return await apiRequest(`${MESSAGES_URL}stats/`, { method: 'GET' });
}

/**
 * Contact property owner
 */
export async function contactPropertyOwner(propertyId, messageData) {
  if (!propertyId) throw new Error('Property ID is required');
  if (!messageData) throw new Error('Message data is required');
  
  return await apiRequest(`${API_BASE_URL}/properties/${propertyId}/contact/`, {
    method: 'POST',
    body: JSON.stringify(messageData)
  });
}

/**
 * Delete a message
 */
export async function deleteMessage(id) {
  if (!id) throw new Error('Message ID is required');
  
  await apiRequest(`${MESSAGES_URL}${id}/`, { method: 'DELETE' });
  return true;
}

/**
 * Search messages
 */
export async function searchMessages(query, filters = {}) {
  const searchFilters = {
    ...filters,
    search: query
  };
  
  return await getMessages(searchFilters);
}

/**
 * Get inbox messages
 */
export async function getInboxMessages(page = 1) {
  return await getMessages({
    box: 'inbox',
    page,
    ordering: '-created_at'
  });
}

/**
 * Get sent messages
 */
export async function getSentMessages(page = 1) {
  return await getMessages({
    box: 'sent',
    page,
    ordering: '-created_at'
  });
}

/**
 * Get unread messages
 */
export async function getUnreadMessages() {
  return await getMessages({
    box: 'unread',
    ordering: '-created_at'
  });
}