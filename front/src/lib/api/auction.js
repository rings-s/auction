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