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
    
    const response = await fetch(`${AUCTION_URL}/slug/${slug}/`, {
      headers
    });
    
    if (response.status === 401 && token) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${AUCTION_URL}/slug/${slug}/`, {
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

// Create a new auction
export async function createAuction(auctionData) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
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
export async function placeBid(auctionId, bidAmount) {
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await fetch(`${BID_URL}/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        auction: auctionId,
        bid_amount: bidAmount
      })
    });
    
    if (response.status === 401) {
      // Try to refresh token and retry
      const newToken = await refreshToken();
      const retryResponse = await fetch(`${BID_URL}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          auction: auctionId,
          bid_amount: bidAmount
        })
      });
      
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json();
        throw new Error(errorData.error?.message || 'Failed to place bid');
      }
      
      return await retryResponse.json();
    }
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || 'Failed to place bid');
    }
    
    return await response.json();
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