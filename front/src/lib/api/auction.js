// src/lib/api/auction.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const AUCTION_URL = `${API_BASE_URL}/auctions`;
const BID_URL = `${API_BASE_URL}/bids`;

// Fetch auctions with filtering, pagination, and search
export async function fetchAuctions(filters = {}) {
  let queryParams = new URLSearchParams();
  
  // Add filters to query params
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });
  
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${AUCTION_URL}/?${queryParams.toString()}`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/?${queryParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch auctions');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch auctions');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching auctions:', error);
    throw error;
  }
}

// Fetch a single auction by ID
export async function fetchAuctionById(id) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${AUCTION_URL}/${id}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${id}/`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch auction details');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch auction details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching auction details:', error);
    throw error;
  }
}

// Fetch an auction by slug
export async function fetchAuctionBySlug(slug) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    // Fixed: Use correct URL structure for slug
    const response = await fetch(`${AUCTION_URL}/${slug}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${slug}/`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch auction details');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch auction details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching auction details:', error);
    throw error;
  }
}


// Add this function to your auction.js file

// Place a bid using auction slug
export async function placeBidBySlug(slug, bidAmount) {
  try {
    // First get the auction to get its ID
    const auction = await fetchAuctionBySlug(slug);
    
    // Then place the bid using the auction ID
    return await placeBid(auction.id, bidAmount);
  } catch (error) {
    console.error('Error placing bid by slug:', error);
    throw error;
  }
}

// Get all bids for a specific auction by slug
export async function fetchAuctionBidsBySlug(slug) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    // First get the auction to get its ID
    const auction = await fetchAuctionBySlug(slug);
    
    // Then fetch bids for that auction
    const response = await fetch(`${BID_URL}/?auction=${auction.id}&ordering=-bid_time`, {
      headers
    });
    
    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${BID_URL}/?auction=${auction.id}&ordering=-bid_time`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch auction bids');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch auction bids');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching auction bids:', error);
    throw error;
  }
}

// Create a new auction
export async function createAuction(auctionData) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    // Handle auction type compatibility with backend
    if (auctionData.auction_type === 'reserve') {
      auctionData.auction_type = 'private';
    } else if (auctionData.auction_type === 'no_reserve') {
      auctionData.auction_type = 'public';
    }
    
    const response = await fetch(`${AUCTION_URL}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(auctionData)
    });
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(auctionData)
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error?.message || 'Failed to create auction');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to create auction');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating auction:', error);
    throw error;
  }
}

// Place a bid on an auction
export async function placeBid(auctionId, bidAmount, maxBidAmount = null) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required to place bid');
    }
    
    const requestData = {
      auction: auctionId,
      bid_amount: bidAmount
    };
    
    if (maxBidAmount) {
      requestData.max_bid_amount = maxBidAmount;
    }
    
    console.log('Placing bid with data:', requestData);
    
    const response = await fetch(`${API_BASE_URL}/bids/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    const responseData = await response.json();
    console.log('Bid response:', responseData);
    
    if (!response.ok) {
      // Handle different error formats
      if (responseData.error) {
        const errorMessage = responseData.error.message || 'Failed to place bid';
        const errorCode = responseData.error.code;
        
        // Create an error with additional context
        const error = new Error(errorMessage);
        error.code = errorCode;
        error.details = responseData.error.details;
        
        // Handle specific error codes
        switch (errorCode) {
          case 'AUTH_REQUIRED':
            error.message = 'Please log in to place a bid';
            break;
          case 'VERIFICATION_REQUIRED':
            error.message = 'Please verify your email address to place bids';
            break;
          case 'ACCOUNT_INACTIVE':
            error.message = 'Your account is inactive. Please contact support.';
            break;
          case 'BID_TOO_LOW':
            error.message = `Bid must be at least $${responseData.error.minimum_bid?.toLocaleString() || 'higher'}`;
            break;
          case 'AUCTION_INACTIVE':
            error.message = 'This auction is not currently accepting bids';
            break;
          case 'AUCTION_ENDED':
            error.message = 'This auction has ended';
            break;
          case 'SELF_BID_NOT_ALLOWED':
            error.message = 'You cannot bid on your own auction';
            break;
        }
        
        throw error;
      } else {
        throw new Error('Failed to place bid');
      }
    }
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${API_BASE_URL}/bids/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      if (!retryResponse.ok) {
        const retryData = await retryResponse.json();
        throw new Error(retryData.error?.message || 'Failed to place bid after token refresh');
      }
      
      return await retryResponse.json();
    }
    
    return responseData;
    
  } catch (error) {
    console.error('Error placing bid:', error);
    throw error;
  }
}

// Get user's bids
export async function fetchUserBids() {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await fetch(`${BID_URL}/?bidder=current`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${BID_URL}/?bidder=current`, {
        headers: {
          'Authorization': `Bearer ${newToken}`
        }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch bids');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch bids');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching user bids:', error);
    throw error;
  }
}

// Get all bids for an auction
export async function fetchAuctionBids(auctionId) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${BID_URL}/?auction=${auctionId}`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${BID_URL}/?auction=${auctionId}`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch auction bids');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch auction bids');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching auction bids:', error);
    throw error;
  }
}

// Update an existing auction
export async function updateAuction(id, auctionData) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    // Handle auction type compatibility with backend
    if (auctionData.auction_type === 'reserve') {
      auctionData.auction_type = 'private';
    } else if (auctionData.auction_type === 'no_reserve') {
      auctionData.auction_type = 'public';
    }
    
    const response = await fetch(`${AUCTION_URL}/${id}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(auctionData)
    });
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${id}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(auctionData)
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error?.message || 'Failed to update auction');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to update auction');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating auction:', error);
    throw error;
  }
}

// Delete an auction
export async function deleteAuction(id) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await fetch(`${AUCTION_URL}/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${newToken}`
        }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to delete auction');
      }
      
      return true;
    }
    
    if (!response.ok) {
      throw new Error('Failed to delete auction');
    }
    
    return true;
  } catch (error) {
    console.error('Error deleting auction:', error);
    throw error;
  }
}


// Extend auction
export async function extendAuction(id, extensionData) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await fetch(`${AUCTION_URL}/${id}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        action: 'extend',
        ...extensionData
      })
    });
    
    if (response.status === 401) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: 'extend',
          ...extensionData
        })
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error || 'Failed to extend auction');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to extend auction');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error extending auction:', error);
    throw error;
  }
}

// Complete auction
export async function completeAuction(id, completionData) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await fetch(`${AUCTION_URL}/${id}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        action: 'complete',
        ...completionData
      })
    });
    
    if (response.status === 401) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: 'complete',
          ...completionData
        })
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error || 'Failed to complete auction');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to complete auction');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error completing auction:', error);
    throw error;
  }
}

// Get auction statistics for owners
export async function getAuctionStats(id) {
  try {
    const token = localStorage.getItem('accessToken');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    const response = await fetch(`${AUCTION_URL}/${id}/stats/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/${id}/stats/`, {
        headers: { 'Authorization': `Bearer ${newToken}` }
      });
      
      if (!retryResponse.ok) {
        throw new Error('Failed to fetch auction stats');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch auction stats');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching auction stats:', error);
    throw error;
  }
}