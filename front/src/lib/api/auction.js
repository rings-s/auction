// src/lib/api/auction.js
import { API_BASE_URL, WS_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const AUCTION_URL = `${API_BASE_URL}/auctions`;
const BID_URL = `${API_BASE_URL}/bids`;

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

  try {
    let response = await fetch(url, requestOptions);
    
    // Handle token refresh for 401 responses
    if (response.status === 401 && token) {
      try {
        const newToken = await refreshToken();
        requestOptions.headers.Authorization = `Bearer ${newToken}`;
        response = await fetch(url, requestOptions);
      } catch (refreshError) {
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

    // Handle error responses
    if (!response.ok) {
      const errorMessage = extractErrorMessage(data, response.status);
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    throw error;
  }
}

/**
 * Extract error message from different response formats
 */
function extractErrorMessage(data, status) {
  // Handle string responses
  if (typeof data === 'string') {
    return data || `HTTP Error ${status}`;
  }

  // Handle structured error responses
  if (data && typeof data === 'object') {
    // Check for nested error object with message
    if (data.error && data.error.message) {
      return data.error.message;
    }
    
    // Check for direct error message
    if (data.error && typeof data.error === 'string') {
      return data.error;
    }

    // Check for Django REST framework 'detail' field
    if (data.detail) {
      return data.detail;
    }

    // Check for direct message field
    if (data.message) {
      return data.message;
    }

    // Handle validation errors (field-specific errors)
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

// Fetch auctions with filtering, pagination, and search
export async function fetchAuctions(filters = {}) {
  const queryParams = new URLSearchParams();
  
  // Add filters to query params
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  const url = `${AUCTION_URL}/?${queryParams.toString()}`;
  return await apiRequest(url, { method: 'GET' });
}

// Fetch a single auction by ID
export async function fetchAuctionById(id) {
  if (!id) throw new Error('Auction ID is required');
  return await apiRequest(`${AUCTION_URL}/${id}/`, { method: 'GET' });
}

// Fetch an auction by slug
export async function fetchAuctionBySlug(slug) {
  if (!slug) throw new Error('Auction slug is required');
  const encodedSlug = encodeURIComponent(slug);
  return await apiRequest(`${AUCTION_URL}/${encodedSlug}/`, { method: 'GET' });
}

// Get all bids for a specific auction by slug
export async function fetchAuctionBidsBySlug(slug) {
  if (!slug) throw new Error('Auction slug is required');
  
  try {
    // First get the auction to get its ID
    const auction = await fetchAuctionBySlug(slug);
    
    // Then fetch bids for that auction
    const url = `${BID_URL}/?auction=${auction.id}&ordering=-bid_time`;
    return await apiRequest(url, { method: 'GET' });
  } catch (error) {
    throw error;
  }
}

// Get all bids for an auction by ID
export async function fetchAuctionBids(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  const url = `${BID_URL}/?auction=${auctionId}&ordering=-bid_time`;
  return await apiRequest(url, { method: 'GET' });
}

/**
 * Get auction status and real-time data
 */
export async function getAuctionStatus(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${auctionId}/status/`, { method: 'GET' });
}

/**
 * Place a bid with improved status checking
 */
export async function placeBid(auctionId, bidAmount, maxBidAmount = null) {
  try {
    // Validate inputs
    if (!auctionId) {
      throw new Error('Auction ID is required');
    }

    if (!bidAmount || isNaN(bidAmount) || bidAmount <= 0) {
      throw new Error('Valid bid amount is required');
    }

    // Check authentication
    const token = localStorage.getItem('accessToken');
    if (!token) {
      throw new Error('Authentication required to place bid');
    }

    // First check auction status using the new endpoint
    const statusCheck = await getAuctionStatus(auctionId);

    if (!statusCheck.is_biddable) {
      throw new Error(`Auction is ${statusCheck.status_display} and not accepting bids`);
    }

    // Prepare bid data
    const requestData = {
      auction: parseInt(auctionId),
      bid_amount: parseFloat(bidAmount)
    };
    
    if (maxBidAmount && !isNaN(maxBidAmount) && maxBidAmount > 0) {
      requestData.max_bid_amount = parseFloat(maxBidAmount);
    }
    
    // Make the API request
    const response = await apiRequest(`${BID_URL}/`, {
      method: 'POST',
      body: JSON.stringify(requestData)
    });
    
    return response;
    
  } catch (error) {
    // Enhanced error handling for specific bid errors
    let errorMessage = error.message;
    
    // Handle specific error patterns
    if (errorMessage.includes('not currently accepting bids')) {
      errorMessage = 'This auction is not currently accepting bids. Please check the auction status and timing.';
    } else if (errorMessage.includes('Authentication required')) {
      errorMessage = 'Please log in to place a bid';
    } else if (errorMessage.includes('verification')) {
      errorMessage = 'Please verify your email address to place bids';
    } else if (errorMessage.includes('minimum') || errorMessage.includes('too low')) {
      errorMessage = 'Your bid amount is too low. Please increase your bid.';
    } else if (errorMessage.includes('ended')) {
      errorMessage = 'This auction has ended and is no longer accepting bids';
    } else if (errorMessage.includes('scheduled')) {
      errorMessage = 'This auction has not started yet';
    }
    
    // Create enhanced error object
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    throw enhancedError;
  }
}

// Place a bid using auction slug
export async function placeBidBySlug(slug, bidAmount, maxBidAmount = null) {
  try {
    // First get the auction to get its ID
    const auction = await fetchAuctionBySlug(slug);
    
    // Then place the bid using the auction ID
    return await placeBid(auction.id, bidAmount, maxBidAmount);
  } catch (error) {
    throw error;
  }
}

/**
 * Check if auction can accept bids
 */
export async function canAuctionAcceptBids(auctionId) {
  try {
    const statusInfo = await getAuctionStatus(auctionId);
    return {
      canAcceptBids: statusInfo.is_biddable,
      reason: statusInfo.is_biddable ? 'Auction is active' : `Auction is ${statusInfo.status_display}`,
      details: statusInfo
    };
  } catch (error) {
    return {
      canAcceptBids: false,
      reason: error.message,
      details: null
    };
  }
}

// Create a new auction
export async function createAuction(auctionData) {
  if (!auctionData) throw new Error('Auction data is required');
  
  // Handle auction type compatibility with backend
  const processedData = { ...auctionData };
  if (processedData.auction_type === 'reserve') {
    processedData.auction_type = 'private';
  } else if (processedData.auction_type === 'no_reserve') {
    processedData.auction_type = 'public';
  }
  
  return await apiRequest(`${AUCTION_URL}/`, {
    method: 'POST',
    body: JSON.stringify(processedData)
  });
}

// Update an existing auction
export async function updateAuction(id, auctionData) {
  if (!id) throw new Error('Auction ID is required');
  if (!auctionData) throw new Error('Auction data is required');
  
  // Handle auction type compatibility with backend
  const processedData = { ...auctionData };
  if (processedData.auction_type === 'reserve') {
    processedData.auction_type = 'private';
  } else if (processedData.auction_type === 'no_reserve') {
    processedData.auction_type = 'public';
  }
  
  return await apiRequest(`${AUCTION_URL}/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(processedData)
  });
}

// Delete an auction
export async function deleteAuction(id) {
  if (!id) throw new Error('Auction ID is required');
  
  await apiRequest(`${AUCTION_URL}/${id}/`, { method: 'DELETE' });
  return true;
}

// Get user's bids
export async function fetchUserBids() {
  const token = localStorage.getItem('accessToken');
  if (!token) throw new Error('Authentication required');
  
  return await apiRequest(`${BID_URL}/?bidder=current`, { method: 'GET' });
}

/**
 * Check if user can bid on auction
 */
export async function checkBiddingEligibility(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  const token = localStorage.getItem('accessToken');
  if (!token) {
    return { canBid: false, reason: 'Authentication required' };
  }

  try {
    const statusInfo = await getAuctionStatus(auctionId);
    return { 
      canBid: statusInfo.is_biddable, 
      reason: statusInfo.is_biddable ? 'Ready to bid' : `Auction is ${statusInfo.status_display}`
    };
  } catch (error) {
    return { canBid: false, reason: error.message || 'Failed to check eligibility' };
  }
}

/**
 * Debug auction state for bidding
 */
export async function debugAuctionBiddingState(auctionId) {
  try {
    const auction = await fetchAuctionById(auctionId);
    const statusInfo = await getAuctionStatus(auctionId);
    
    return {
      auction,
      statusInfo,
      debugInfo: {
        shouldBeActive: statusInfo.is_biddable,
        currentTime: new Date(),
        isPublished: auction.is_published,
        status: auction.status,
        backendChecked: true
      }
    };
  } catch (error) {
    throw error;
  }
}

// WebSocket connection for real-time updates
export function createAuctionWebSocket(auctionId, callbacks = {}) {
  const token = localStorage.getItem('accessToken');
  const wsUrl = `${WS_BASE_URL}/auction/${auctionId}/`;
  
  const socket = new WebSocket(wsUrl);
  
  socket.onopen = function(event) {
    if (callbacks.onOpen) callbacks.onOpen(event);
  };
  
  socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'auction_update' && callbacks.onAuctionUpdate) {
      callbacks.onAuctionUpdate(data.auction);
    }
    
    if (data.type === 'auction_update' && data.new_bid && callbacks.onNewBid) {
      callbacks.onNewBid(data.new_bid);
    }
    
    if (data.type === 'status_changed' && callbacks.onStatusChange) {
      callbacks.onStatusChange(data);
    }
    
    if (data.type === 'error' && callbacks.onError) {
      callbacks.onError(data.message);
    }
  };
  
  socket.onclose = function(event) {
    if (callbacks.onClose) callbacks.onClose(event);
  };
  
  socket.onerror = function(error) {
    if (callbacks.onError) callbacks.onError('WebSocket connection error');
  };
  
  return socket;
}

// Send bid through WebSocket
export function sendBidThroughWebSocket(socket, auctionId, bidAmount, maxBidAmount = null) {
  const bidData = {
    type: 'place_bid',
    auction: auctionId,
    amount: parseFloat(bidAmount)
  };
  
  if (maxBidAmount) {
    bidData.max_bid = parseFloat(maxBidAmount);
  }
  
  socket.send(JSON.stringify(bidData));
}

// Remaining export functions...
export async function registerForAuction(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  return await apiRequest(`${AUCTION_URL}/${auctionId}/register/`, { method: 'POST' });
}

export async function watchAuction(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  return await apiRequest(`${AUCTION_URL}/${auctionId}/watch/`, { method: 'POST' });
}

export async function unwatchAuction(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  return await apiRequest(`${AUCTION_URL}/${auctionId}/watch/`, { method: 'DELETE' });
}

export async function cancelBid(bidId) {
  if (!bidId) throw new Error('Bid ID is required');
  return await apiRequest(`${BID_URL}/${bidId}/`, { method: 'DELETE' });
}