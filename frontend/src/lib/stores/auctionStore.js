// /src/lib/stores/auctionStore.js
import { writable, derived } from 'svelte/store';
import { api } from '$lib/api';
import { notificationStore } from './notificationStore';

// Initialize auction store
function createAuctionStore() {
  const { subscribe, set, update } = writable({
    auctions: [],
    featuredAuctions: [],
    currentAuction: null,
    categories: [],
    bids: [],
    loading: {
      auctions: false,
      featured: false,
      details: false,
      categories: false,
      bids: false,
      create: false,
      bid: false
    },
    pagination: {
      count: 0,
      next: null,
      previous: null,
      total_pages: 0
    },
    filters: {
      category: null,
      status: 'ACTIVE',
      min_price: null,
      max_price: null,
      search: '',
      sort_by: 'created_at',
      direction: 'desc'
    },
    error: null
  });

  return {
    subscribe,
    
    /**
     * Load auctions with optional filters
     */
    loadAuctions: async (filters = {}) => {
      update(state => ({
        ...state,
        loading: { ...state.loading, auctions: true },
        error: null
      }));
      
      try {
        // Merge default filters with provided filters
        const currentFilters = { ...state.filters, ...filters };
        
        // Convert filters object to query params
        const params = {};
        for (const [key, value] of Object.entries(currentFilters)) {
          if (value !== null && value !== undefined && value !== '') {
            params[key] = value;
          }
        }
        
        const response = await api.base.auction_list({ params });
        
        update(state => ({
          ...state,
          auctions: response.results || [],
          pagination: {
            count: response.count || 0,
            next: response.next,
            previous: response.previous,
            total_pages: response.total_pages || 0
          },
          filters: currentFilters,
          loading: { ...state.loading, auctions: false }
        }));
        
        return response;
      } catch (error) {
        console.error('Error loading auctions:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, auctions: false },
          error: error.error || 'Failed to load auctions'
        }));
        
        notificationStore.error('Failed to load auctions');
        throw error;
      }
    },
    
    /**
     * Load featured auctions
     */
    loadFeaturedAuctions: async () => {
      update(state => ({
        ...state,
        loading: { ...state.loading, featured: true },
        error: null
      }));
      
      try {
        const response = await api.base.auction_list({
          params: {
            status: 'ACTIVE',
            sort_by: 'current_price', // Assuming highest price = featured
            direction: 'desc',
            page_size: 3
          }
        });
        
        update(state => ({
          ...state,
          featuredAuctions: response.results || [],
          loading: { ...state.loading, featured: false }
        }));
        
        return response.results;
      } catch (error) {
        console.error('Error loading featured auctions:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, featured: false },
          error: error.error || 'Failed to load featured auctions'
        }));
        
        notificationStore.error('Failed to load featured auctions');
        throw error;
      }
    },
    
    /**
     * Load auction details by ID
     */
    loadAuctionDetails: async (auctionId) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      update(state => ({
        ...state,
        loading: { ...state.loading, details: true },
        error: null
      }));
      
      try {
        const auction = await api.base.auction_detail(auctionId);
        
        update(state => ({
          ...state,
          currentAuction: auction,
          loading: { ...state.loading, details: false }
        }));
        
        return auction;
      } catch (error) {
        console.error('Error loading auction details:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, details: false },
          error: error.error || 'Failed to load auction details'
        }));
        
        notificationStore.error('Failed to load auction details');
        throw error;
      }
    },
    
    /**
     * Load categories
     */
    loadCategories: async () => {
      update(state => ({
        ...state,
        loading: { ...state.loading, categories: true },
        error: null
      }));
      
      try {
        const response = await api.base.category_list({
          params: {
            is_active: true,
            page_size: 100 // Get as many as possible
          }
        });
        
        update(state => ({
          ...state,
          categories: response.results || [],
          loading: { ...state.loading, categories: false }
        }));
        
        return response.results;
      } catch (error) {
        console.error('Error loading categories:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, categories: false },
          error: error.error || 'Failed to load categories'
        }));
        
        notificationStore.error('Failed to load categories');
        throw error;
      }
    },
    
    /**
     * Create a new auction
     */
    createAuction: async (auctionData) => {
      update(state => ({
        ...state,
        loading: { ...state.loading, create: true },
        error: null
      }));
      
      try {
        const response = await api.base.auction_create(auctionData);
        
        update(state => ({
          ...state,
          currentAuction: response,
          loading: { ...state.loading, create: false }
        }));
        
        notificationStore.success('Auction created successfully');
        return response;
      } catch (error) {
        console.error('Error creating auction:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, create: false },
          error: error.error || 'Failed to create auction'
        }));
        
        notificationStore.error('Failed to create auction');
        throw error;
      }
    },
    
    /**
     * Update an existing auction
     */
    updateAuction: async (auctionId, auctionData) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      update(state => ({
        ...state,
        loading: { ...state.loading, create: true }, // Reuse create loading flag
        error: null
      }));
      
      try {
        const response = await api.base.auction_update(auctionId, auctionData);
        
        update(state => ({
          ...state,
          currentAuction: response,
          loading: { ...state.loading, create: false }
        }));
        
        notificationStore.success('Auction updated successfully');
        return response;
      } catch (error) {
        console.error('Error updating auction:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, create: false },
          error: error.error || 'Failed to update auction'
        }));
        
        notificationStore.error('Failed to update auction');
        throw error;
      }
    },
    
    /**
     * Delete an auction
     */
    deleteAuction: async (auctionId) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      update(state => ({
        ...state,
        loading: { ...state.loading, details: true }, // Reuse details loading flag
        error: null
      }));
      
      try {
        await api.base.auction_delete(auctionId);
        
        update(state => {
          // Filter out the deleted auction from the list
          const updatedAuctions = state.auctions.filter(a => a.id !== auctionId);
          
          return {
            ...state,
            auctions: updatedAuctions,
            currentAuction: null,
            loading: { ...state.loading, details: false }
          };
        });
        
        notificationStore.success('Auction deleted successfully');
        return true;
      } catch (error) {
        console.error('Error deleting auction:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, details: false },
          error: error.error || 'Failed to delete auction'
        }));
        
        notificationStore.error('Failed to delete auction');
        throw error;
      }
    },
    
    /**
     * Load bids for an auction
     */
    loadBids: async (auctionId) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      update(state => ({
        ...state,
        loading: { ...state.loading, bids: true },
        error: null
      }));
      
      try {
        const response = await api.base.list_bids(auctionId);
        
        update(state => ({
          ...state,
          bids: response.results || [],
          loading: { ...state.loading, bids: false }
        }));
        
        return response.results;
      } catch (error) {
        console.error('Error loading bids:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, bids: false },
          error: error.error || 'Failed to load bids'
        }));
        
        notificationStore.error('Failed to load bids');
        throw error;
      }
    },
    
    /**
     * Place a bid on an auction
     */
    placeBid: async (auctionId, bidData) => {
      if (!auctionId) {
        notificationStore.error('Invalid auction ID');
        return;
      }
      
      update(state => ({
        ...state,
        loading: { ...state.loading, bid: true },
        error: null
      }));
      
      try {
        const response = await api.base.create_bid(auctionId, bidData);
        
        // Update current auction with new bid info
        update(state => {
          // Add the new bid to the bids array
          const updatedBids = [response, ...state.bids];
          
          // Update current auction if it matches
          let updatedCurrentAuction = state.currentAuction;
          if (updatedCurrentAuction && updatedCurrentAuction.id === auctionId) {
            updatedCurrentAuction = {
              ...updatedCurrentAuction,
              current_price: response.amount,
              current_highest_bid: response
            };
          }
          
          return {
            ...state,
            bids: updatedBids,
            currentAuction: updatedCurrentAuction,
            loading: { ...state.loading, bid: false }
          };
        });
        
        notificationStore.success('Bid placed successfully');
        return response;
      } catch (error) {
        console.error('Error placing bid:', error);
        
        update(state => ({ 
          ...state, 
          loading: { ...state.loading, bid: false },
          error: error.error || 'Failed to place bid'
        }));
        
        notificationStore.error(error.error || 'Failed to place bid');
        throw error;
      }
    },
    
    /**
     * Set filters for auction listings
     */
    setFilters: (newFilters) => {
      update(state => ({
        ...state,
        filters: { ...state.filters, ...newFilters }
      }));
    },
    
    /**
     * Clear all filters
     */
    clearFilters: () => {
      update(state => ({
        ...state,
        filters: {
          category: null,
          status: 'ACTIVE',
          min_price: null,
          max_price: null,
          search: '',
          sort_by: 'created_at',
          direction: 'desc'
        }
      }));
    },
    
    /**
     * Reset current auction
     */
    resetCurrentAuction: () => {
      update(state => ({
        ...state,
        currentAuction: null
      }));
    },
    
    /**
     * Clear error
     */
    clearError: () => {
      update(state => ({
        ...state,
        error: null
      }));
    },
    
    /**
     * Reset store to initial state
     */
    reset: () => {
      set({
        auctions: [],
        featuredAuctions: [],
        currentAuction: null,
        categories: [],
        bids: [],
        loading: {
          auctions: false,
          featured: false,
          details: false,
          categories: false,
          bids: false,
          create: false,
          bid: false
        },
        pagination: {
          count: 0,
          next: null,
          previous: null,
          total_pages: 0
        },
        filters: {
          category: null,
          status: 'ACTIVE',
          min_price: null,
          max_price: null,
          search: '',
          sort_by: 'created_at',
          direction: 'desc'
        },
        error: null
      });
    }
  };
}

// Create and export the auction store
export const auctionStore = createAuctionStore();

// Derived stores for convenience
export const auctions = derived(auctionStore, $store => $store.auctions);
export const featuredAuctions = derived(auctionStore, $store => $store.featuredAuctions);
export const currentAuction = derived(auctionStore, $store => $store.currentAuction);
export const categories = derived(auctionStore, $store => $store.categories);
export const auctionLoading = derived(auctionStore, $store => $store.loading);
export const auctionError = derived(auctionStore, $store => $store.error);