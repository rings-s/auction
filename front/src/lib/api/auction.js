// src/lib/api/auction.js
import { API_BASE_URL } from '$lib/constants';
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

  console.log(`API Request: ${options.method || 'GET'} ${url}`);
  if (options.body) {
    console.log('Request body:', options.body);
  }

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

    console.log(`API Response (${response.status}):`, data);

    // Handle error responses
    if (!response.ok) {
      const errorMessage = extractErrorMessage(data, response.status);
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`API Error (${url}):`, error);
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
  return await apiRequest(`${AUCTION_URL}/${slug}/`, { method: 'GET' });
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
    console.error('Error fetching auction bids by slug:', error);
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
 * Debug auction state for bidding
 */
export async function debugAuctionBiddingState(auctionId) {
  try {
    const auction = await fetchAuctionById(auctionId);
    const now = new Date();
    const startDate = new Date(auction.start_date);
    const endDate = new Date(auction.end_date);
    
    console.log('🔍 AUCTION DEBUGGING INFO:');
    console.log('Auction ID:', auctionId);
    console.log('Auction Status:', auction.status);
    console.log('Is Published:', auction.is_published);
    console.log('Current Time:', now.toISOString());
    console.log('Start Date:', startDate.toISOString());
    console.log('End Date:', endDate.toISOString());
    console.log('Is Current Time After Start?', now >= startDate);
    console.log('Is Current Time Before End?', now < endDate);
    console.log('Starting Bid:', auction.starting_bid);
    console.log('Current Bid:', auction.current_bid);
    console.log('Minimum Increment:', auction.minimum_increment);
    
    // Calculate if auction should be active
    const shouldBeActive = (
      auction.status === 'live' &&
      auction.is_published &&
      now >= startDate &&
      now < endDate
    );
    
    console.log('Should Be Active:', shouldBeActive);
    
    return {
      auction,
      debugInfo: {
        shouldBeActive,
        currentTime: now,
        isAfterStart: now >= startDate,
        isBeforeEnd: now < endDate,
        isPublished: auction.is_published,
        status: auction.status
      }
    };
  } catch (error) {
    console.error('Error debugging auction:', error);
    throw error;
  }
}

/**
 * FIXED: Place a bid on an auction with comprehensive debugging
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

    console.log('🔍 PLACING BID - DEBUG INFO:');
    
    // Debug auction state first
    const debugInfo = await debugAuctionBiddingState(auctionId);
    
    if (!debugInfo.debugInfo.shouldBeActive) {
      console.error('❌ AUCTION NOT ACTIVE:');
      console.error('Status:', debugInfo.auction.status);
      console.error('Published:', debugInfo.auction.is_published);
      console.error('Current Time:', debugInfo.debugInfo.currentTime);
      console.error('Is After Start:', debugInfo.debugInfo.isAfterStart);
      console.error('Is Before End:', debugInfo.debugInfo.isBeforeEnd);
      
      // Provide specific error message based on issue
      if (debugInfo.auction.status !== 'live') {
        throw new Error(`Auction status is "${debugInfo.auction.status}" but must be "live" to accept bids`);
      }
      if (!debugInfo.auction.is_published) {
        throw new Error('Auction is not published and cannot accept bids');
      }
      if (!debugInfo.debugInfo.isAfterStart) {
        throw new Error('Auction has not started yet');
      }
      if (!debugInfo.debugInfo.isBeforeEnd) {
        throw new Error('Auction has already ended');
      }
    }

    // Calculate minimum bid
    const currentBid = debugInfo.auction.current_bid || debugInfo.auction.starting_bid;
    const minimumBid = parseFloat(currentBid) + parseFloat(debugInfo.auction.minimum_increment);
    
    console.log('💰 BID AMOUNT VALIDATION:');
    console.log('Bid Amount:', bidAmount);
    console.log('Current Bid:', currentBid);
    console.log('Minimum Required:', minimumBid);
    console.log('Is Valid:', parseFloat(bidAmount) >= minimumBid);
    
    if (parseFloat(bidAmount) < minimumBid) {
      throw new Error(`Bid amount must be at least $${minimumBid.toLocaleString()}`);
    }

    // Prepare bid data
    const requestData = {
      auction: parseInt(auctionId),
      bid_amount: parseFloat(bidAmount)
    };
    
    if (maxBidAmount && !isNaN(maxBidAmount) && maxBidAmount > 0) {
      requestData.max_bid_amount = parseFloat(maxBidAmount);
    }
    
    console.log('📤 SENDING BID REQUEST:', requestData);
    
    // Make the API request
    const response = await apiRequest(`${BID_URL}/`, {
      method: 'POST',
      body: JSON.stringify(requestData)
    });
    
    console.log('✅ BID PLACED SUCCESSFULLY:', response);
    return response;
    
  } catch (error) {
    console.error('❌ ERROR PLACING BID:', error);
    
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
    } else if (errorMessage.includes('own auction')) {
      errorMessage = 'You cannot bid on your own auction';
    }
    
    // Create enhanced error object
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    throw enhancedError;
  }
}

/**
 * Check if auction can accept bids
 */
export async function canAuctionAcceptBids(auctionId) {
  try {
    const debugInfo = await debugAuctionBiddingState(auctionId);
    return {
      canAcceptBids: debugInfo.debugInfo.shouldBeActive,
      reason: debugInfo.debugInfo.shouldBeActive ? 'Auction is active' : 'Auction is not active',
      details: debugInfo.debugInfo
    };
  } catch (error) {
    return {
      canAcceptBids: false,
      reason: error.message,
      details: null
    };
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
    console.error('Error placing bid by slug:', error);
    throw error;
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

// Extend auction
export async function extendAuction(id, extensionData) {
  if (!id) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({
      action: 'extend',
      ...extensionData
    })
  });
}

// Complete auction
export async function completeAuction(id, completionData) {
  if (!id) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({
      action: 'complete',
      ...completionData
    })
  });
}

// Get auction statistics for owners
export async function getAuctionStats(id) {
  if (!id) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${id}/stats/`, { method: 'GET' });
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
    return await apiRequest(`${AUCTION_URL}/${auctionId}/can-bid/`, { method: 'GET' });
  } catch (error) {
    console.error('Error checking bidding eligibility:', error);
    return { canBid: false, reason: error.message || 'Failed to check eligibility' };
  }
}

/**
 * Register for an auction
 */
export async function registerForAuction(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${auctionId}/register/`, { method: 'POST' });
}

/**
 * Get auction status and real-time data
 */
export async function getAuctionStatus(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${auctionId}/status/`, { method: 'GET' });
}

/**
 * Watch an auction (add to watchlist)
 */
export async function watchAuction(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${auctionId}/watch/`, { method: 'POST' });
}

/**
 * Unwatch an auction (remove from watchlist)
 */
export async function unwatchAuction(auctionId) {
  if (!auctionId) throw new Error('Auction ID is required');
  
  return await apiRequest(`${AUCTION_URL}/${auctionId}/watch/`, { method: 'DELETE' });
}

/**
 * Cancel a bid (if allowed)
 */
export async function cancelBid(bidId) {
  if (!bidId) throw new Error('Bid ID is required');
  
  return await apiRequest(`${BID_URL}/${bidId}/`, { method: 'DELETE' });
}