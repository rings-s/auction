// /src/lib/stores/bidStore.js
import { writable, derived, get } from 'svelte/store';
import { api } from '$lib/api';
import { notificationStore } from './notificationStore';

// Initialize bid store
function createBidStore() {
  const { subscribe, set, update } = writable({
    userBids: [],
    auctionBids: {},  // Map of auction ID to bids for that auction
    loading: false,
    bidding: false,
    error: null,
    pagination: {
      count: 0,
      next: null,
      previous: null,
      total_pages: 0
    }
  });

  return {
    subscribe,
    
    /**
     * Load all bids made by the current user
     */
    loadUserBids: async (filters = {}) => {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        // Use the API helper instead of direct fetch
        const response = await api.bid.listUserBids({ params: filters });
        
        update(state => ({
          ...state,
          userBids: response.results || [],
          pagination: {
            count: response.count || 0,
            next: response.next,
            previous: response.previous,
            total_pages: response.total_pages || 0
          },
          loading: false
        }));
        
        return response.results;
      } catch (error) {
        console.error('Error loading user bids:', error);
        
        update(state => ({ 
          ...state, 
          loading: false,
          error: error.error || 'Failed to load your bids'
        }));
        
        notificationStore.error('Failed to load your bids');
        throw error;
      }
    },
    
    /**
     * Load all bids for a specific auction
     */
    loadAuctionBids: async (auctionId, filters = {}) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        // Use the API helper for auction bids
        const response = await api.bid.listAuctionBids(auctionId, { params: filters });
        
        update(state => {
          const updatedAuctionBids = { ...state.auctionBids };
          updatedAuctionBids[auctionId] = response.results || [];
          
          return {
            ...state,
            auctionBids: updatedAuctionBids,
            pagination: {
              count: response.count || 0,
              next: response.next,
              previous: response.previous,
              total_pages: response.total_pages || 0
            },
            loading: false
          };
        });
        
        return response.results;
      } catch (error) {
        console.error('Error loading auction bids:', error);
        
        update(state => ({ 
          ...state, 
          loading: false,
          error: error.error || 'Failed to load bids for this auction'
        }));
        
        notificationStore.error('Failed to load bids for this auction');
        throw error;
      }
    },
    
    /**
     * Place a bid on an auction
     */
    placeBid: async (auctionId, amount, autoBidLimit = null) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      if (!amount || amount <= 0) {
        notificationStore.error('Invalid bid amount');
        return;
      }
      
      update(state => ({ ...state, bidding: true, error: null }));
      
      try {
        const bidData = {
          amount: parseFloat(amount),
          auto_bid_limit: autoBidLimit ? parseFloat(autoBidLimit) : null
        };
        
        // Use the API helper for creating bids
        const response = await api.bid.createBid(auctionId, bidData);
        
        // Update both user bids and auction bids
        update(state => {
          // Add to user bids
          const updatedUserBids = [response, ...state.userBids];
          
          // Add to auction bids if we're tracking this auction
          const updatedAuctionBids = { ...state.auctionBids };
          if (updatedAuctionBids[auctionId]) {
            updatedAuctionBids[auctionId] = [response, ...updatedAuctionBids[auctionId]];
          }
          
          return {
            ...state,
            userBids: updatedUserBids,
            auctionBids: updatedAuctionBids,
            bidding: false
          };
        });
        
        notificationStore.success('Bid placed successfully!');
        return response;
      } catch (error) {
        console.error('Error placing bid:', error);
        
        update(state => ({ 
          ...state, 
          bidding: false,
          error: error.error || 'Failed to place bid'
        }));
        
        notificationStore.error(error.error || 'Failed to place bid');
        throw error;
      }
    },
    
    /**
     * Check if the user has the highest bid on an auction
     */
    isHighestBidder: (auctionId, userId) => {
      const state = get(bidStore);
      
      // Get bids for this auction
      const auctionBids = state.auctionBids[auctionId];
      if (!auctionBids || auctionBids.length === 0) {
        return false;
      }
      
      // Sort by amount descending
      const sortedBids = [...auctionBids].sort((a, b) => b.amount - a.amount);
      
      // Check if the highest bid is from this user
      return sortedBids[0].bidder === userId;
    },
    
    /**
     * Get the highest bid amount for an auction
     */
    getHighestBidAmount: (auctionId) => {
      const state = get(bidStore);
      
      // Get bids for this auction
      const auctionBids = state.auctionBids[auctionId];
      if (!auctionBids || auctionBids.length === 0) {
        return 0;
      }
      
      // Find highest amount
      return Math.max(...auctionBids.map(bid => bid.amount));
    },
    
    /**
     * Clear error
     */
    clearError: () => {
      update(state => ({ ...state, error: null }));
    },
    
    /**
     * Reset store
     */
    reset: () => {
      set({
        userBids: [],
        auctionBids: {},
        loading: false,
        bidding: false,
        error: null,
        pagination: {
          count: 0,
          next: null,
          previous: null,
          total_pages: 0
        }
      });
    }
  };
}

// Create and export the bid store
export const bidStore = createBidStore();

// Derived stores for convenience
export const userBids = derived(bidStore, $store => $store.userBids);
export const bidLoading = derived(bidStore, $store => $store.loading);
export const bidding = derived(bidStore, $store => $store.bidding);
export const bidError = derived(bidStore, $store => $store.error);