// src/lib/stores/auction.js
// Auction Store - Unified Implementation

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { page } from '$app/stores';
import { t } from '$lib/i18n'; 
import { toast } from '$lib/stores/toast';
import api from '$lib/services/api';

/**
 * Initial state for auction store
 */
const initialState = {
    // Main auction collection
    auctions: [],
    totalCount: 0,
    totalPages: 1,
    currentPage: 1,
    
    // Loading states with detailed tracking
    loading: false,
    loadingMore: false,
    loadingCreate: false,
    loadingUpdate: false,
    loadingDelete: false,
    
    // Error states with detailed tracking
    error: null,
    createError: null,
    updateError: null,
    deleteError: null,
    bidError: null,
    
    // Current filters with expanded options
    filters: {
        status: null,
        auction_type: null,
        property_type: null,
        min_price: null,
        max_price: null,
        city: null,
        district: null,
        is_featured: null,
        start_date_from: null,
        start_date_to: null,
        end_date_from: null,
        end_date_to: null,
        sort_by: 'start_date',
        order: 'desc',
        page_size: 12
    },
    
    // Current auction being viewed
    currentAuction: null,
    currentAuctionLoading: false,
    currentAuctionError: null,
    
    // Bid history
    currentBids: [],
    bidsLoading: false,
    bidsError: null,
    
    // Bid placement
    placingBid: false,
    
    // Cache for performance
    auctionCache: {},
    
    // Last successful action timestamp (for optimistic updates)
    lastSuccessfulAction: null
};

// Create the writable store
const auctionStore = writable(initialState);

/**
 * Check if cache entry is still fresh (< 5 minutes old)
 * @param {Object} cachedItem - Cached item to check
 * @returns {boolean} - True if cache is still fresh
 */
const isCacheFresh = (cachedItem) => {
    if (!cachedItem?.lastFetched) return false;
    
    const now = new Date().getTime();
    const maxAge = 5 * 60 * 1000; // 5 minutes in milliseconds
    return (now - cachedItem.lastFetched) < maxAge;
};

// Action functions to update the store
const auctionActions = {
    /**
     * Load auctions with filtering
     * @param {Object} filters - Filter parameters
     * @param {boolean} append - Whether to append results or replace
     * @returns {Promise<Object>} - Operation result
     */
    async loadAuctions(filters = {}, append = false) {
        const currentState = get(auctionStore);
        
        // Don't start a new request if already loading
        if ((currentState.loading && !append) || (currentState.loadingMore && append)) {
            return { success: false, error: 'Request already in progress' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loading: !append,
            loadingMore: append,
            error: null
        }));

        // Apply filters
        const appliedFilters = {
            ...currentState.filters,
            ...filters,
            page: append ? currentState.currentPage + 1 : 1
        };

        try {
            // Build query params from filters
            const queryParams = {};
            
            for (const [key, value] of Object.entries(appliedFilters)) {
                if (value !== null && value !== undefined && value !== '') {
                    queryParams[key] = value;
                }
            }
            
            // Call API service
            const response = await api.get('/auctions', queryParams);
            
            if (response) {
                auctionStore.update(state => {
                    // Update cache
                    const newCache = { ...state.auctionCache };
                    response.results?.forEach(auction => {
                        newCache[auction.id] = {
                            ...auction,
                            lastFetched: new Date().getTime()
                        };
                    });

                    return {
                        ...state,
                        auctions: append 
                            ? [...state.auctions, ...(response.results || [])]
                            : (response.results || []),
                        totalCount: response.count || 0,
                        totalPages: response.total_pages || 1,
                        currentPage: append ? state.currentPage + 1 : 1,
                        loading: false,
                        loadingMore: false,
                        error: null,
                        filters: appliedFilters,
                        auctionCache: newCache,
                        lastSuccessfulAction: new Date().getTime()
                    };
                });
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.load_error');
                
                auctionStore.update(state => ({
                    ...state,
                    loading: false,
                    loadingMore: false,
                    error: errorMessage
                }));
                
                // Show toast notification for error
                toast.error(errorMessage);
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                loading: false,
                loadingMore: false,
                error: errorMessage
            }));
            
            // Show toast notification for error
            toast.error(errorMessage);
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Load details for a specific auction
     * @param {string|number} auctionId - Auction ID
     * @param {boolean} includeBids - Include bid history
     * @param {boolean} includeProperty - Include property details
     * @param {boolean} forceRefresh - Force refresh even if cached
     * @returns {Promise<Object>} - Operation result
     */
    async loadAuctionDetail(auctionId, includeBids = true, includeProperty = true, forceRefresh = false) {
        if (!auctionId) {
            return { success: false, error: 'Auction ID is required' };
        }

        // Get current state
        const currentState = get(auctionStore);
        
        // Check cache
        const cachedAuction = currentState.auctionCache[auctionId];
        
        // If we have a fresh cached version and don't need to refresh, use that
        if (isCacheFresh(cachedAuction) && !forceRefresh) {
            auctionStore.update(state => ({
                ...state,
                currentAuction: cachedAuction,
                currentAuctionLoading: false,
                currentAuctionError: null
            }));
            
            // Optionally load bids even with cached auction
            if (includeBids) {
                this.loadAuctionBids(auctionId);
            }
            
            return { success: true, data: { auction: cachedAuction } };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            currentAuctionLoading: true,
            currentAuctionError: null
        }));

        const options = {
            include_bids: includeBids,
            include_property: includeProperty,
            include_documents: true
        };

        try {
            // Call API service
            const response = await api.get(`/auctions/${auctionId}`, options);
            
            if (response) {
                const auctionData = response.auction;
                
                if (!auctionData) {
                    throw new Error('No auction data returned');
                }
                
                auctionStore.update(state => {
                    // Add to cache with timestamp
                    const newCache = { 
                        ...state.auctionCache,
                        [auctionId]: {
                            ...auctionData,
                            lastFetched: new Date().getTime()
                        }
                    };

                    return {
                        ...state,
                        currentAuction: auctionData,
                        currentAuctionLoading: false,
                        currentAuctionError: null,
                        auctionCache: newCache,
                        // If bids included, update them too
                        currentBids: auctionData.recent_bids || state.currentBids,
                        bidsLoading: false,
                        lastSuccessfulAction: new Date().getTime()
                    };
                });
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.load_detail_error');
                
                auctionStore.update(state => ({
                    ...state,
                    currentAuctionLoading: false,
                    currentAuctionError: errorMessage
                }));
                
                // Show toast notification for error
                toast.error(errorMessage);
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                currentAuctionLoading: false,
                currentAuctionError: errorMessage
            }));
            
            // Show toast notification for error
            toast.error(errorMessage);
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Load bids for the current auction
     * @param {string|number} auctionId - Auction ID
     * @param {Object} options - Filtering options
     * @returns {Promise<Object>} - Operation result
     */
    async loadAuctionBids(auctionId, options = {}) {
        if (!auctionId) {
            return { success: false, error: 'Auction ID is required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            bidsLoading: true,
            bidsError: null
        }));

        try {
            // Prepare query params
            const queryParams = {
                auction_id: auctionId,
                ...options
            };
            
            // Call API service
            const response = await api.get('/bids', queryParams);
            
            if (response) {
                auctionStore.update(state => ({
                    ...state,
                    currentBids: response.results || [],
                    bidsLoading: false,
                    bidsError: null
                }));
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.load_bids_error');
                
                auctionStore.update(state => ({
                    ...state,
                    bidsLoading: false,
                    bidsError: errorMessage
                }));
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                bidsLoading: false,
                bidsError: errorMessage
            }));
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Place a new bid on an auction
     * @param {string|number} auctionId - Auction ID
     * @param {number} bidAmount - Bid amount
     * @param {boolean} isAutoBid - Is this an automatic bid
     * @param {number} maxBidAmount - Maximum bid amount (for auto-bidding)
     * @returns {Promise<Object>} - Operation result
     */
    async placeBid(auctionId, bidAmount, isAutoBid = false, maxBidAmount = null) {
        if (!auctionId || !bidAmount) {
            return { success: false, error: 'Auction ID and bid amount are required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            placingBid: true,
            bidError: null
        }));

        const bidData = {
            auction: auctionId,
            bid_amount: bidAmount,
            is_auto_bid: isAutoBid
        };

        // Add max bid amount for auto bidding
        if (isAutoBid && maxBidAmount) {
            bidData.max_bid_amount = maxBidAmount;
        }

        try {
            // Call API service
            const response = await api.post('/bids/place', bidData);
            
            if (response) {
                const newBid = response.bid;
                
                if (!newBid) {
                    throw new Error('No bid data returned');
                }
                
                auctionStore.update(state => {
                    // Add the new bid to the current bids
                    const newBids = [newBid, ...state.currentBids];
                    
                    // Update the auction with new current bid if higher
                    let updatedAuction = { ...state.currentAuction };
                    if (newBid.bid_amount > (updatedAuction?.current_bid || 0)) {
                        updatedAuction.current_bid = newBid.bid_amount;
                        updatedAuction.bid_count = (updatedAuction.bid_count || 0) + 1;
                    }
                    
                    // Update cache
                    const newCache = {
                        ...state.auctionCache,
                        [auctionId]: {
                            ...updatedAuction,
                            lastFetched: new Date().getTime()
                        }
                    };

                    return {
                        ...state,
                        currentAuction: updatedAuction,
                        currentBids: newBids,
                        placingBid: false,
                        bidError: null,
                        auctionCache: newCache,
                        lastSuccessfulAction: new Date().getTime()
                    };
                });
                
                // Show success toast
                toast.success(t('auctions.bid_placed_successfully'));
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.bid_error');
                
                auctionStore.update(state => ({
                    ...state,
                    placingBid: false,
                    bidError: errorMessage
                }));
                
                // Show toast notification for error
                toast.error(errorMessage);
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                placingBid: false,
                bidError: errorMessage
            }));
            
            // Show toast notification for error
            toast.error(errorMessage);
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Create a new auction
     * @param {Object} auctionData - New auction data
     * @returns {Promise<Object>} - Operation result with new auction
     */
    async createAuction(auctionData) {
        if (!auctionData) {
            return { success: false, error: 'Auction data is required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loadingCreate: true,
            createError: null
        }));

        try {
            // Call API service
            const response = await api.post('/auctions/create', auctionData);
            
            if (response) {
                const newAuction = response.auction;
                
                if (!newAuction) {
                    throw new Error('No auction data returned');
                }
                
                auctionStore.update(state => {
                    // Add to cache
                    const newCache = {
                        ...state.auctionCache,
                        [newAuction.id]: {
                            ...newAuction,
                            lastFetched: new Date().getTime()
                        }
                    };

                    return {
                        ...state,
                        auctions: [newAuction, ...state.auctions],
                        currentAuction: newAuction,
                        loadingCreate: false,
                        createError: null,
                        auctionCache: newCache,
                        lastSuccessfulAction: new Date().getTime()
                    };
                });
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.create_error');
                
                auctionStore.update(state => ({
                    ...state,
                    loadingCreate: false,
                    createError: errorMessage
                }));
                
                // Show toast notification for error
                toast.error(errorMessage);
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                loadingCreate: false,
                createError: errorMessage
            }));
            
            // Show toast notification for error
            toast.error(errorMessage);
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Update an existing auction
     * @param {string|number} auctionId - Auction ID
     * @param {Object} updateData - Data to update
     * @param {boolean} partial - True for PATCH, false for PUT
     * @returns {Promise<Object>} - Operation result
     */
    async updateAuction(auctionId, updateData, partial = true) {
        if (!auctionId) {
            return { success: false, error: 'Auction ID is required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loadingUpdate: true,
            updateError: null
        }));

        try {
            // Call API service
            const response = await api[partial ? 'patch' : 'put'](`/auctions/${auctionId}/update`, updateData);
            
            if (response) {
                const updatedAuction = response.auction;
                
                if (!updatedAuction) {
                    throw new Error('No auction data returned');
                }
                
                auctionStore.update(state => {
                    // Update auctions list if this auction is in it
                    const updatedAuctions = state.auctions.map(auction => 
                        auction.id === auctionId ? updatedAuction : auction
                    );

                    // Update cache
                    const newCache = {
                        ...state.auctionCache,
                        [auctionId]: {
                            ...updatedAuction,
                            lastFetched: new Date().getTime()
                        }
                    };

                    return {
                        ...state,
                        auctions: updatedAuctions,
                        currentAuction: state.currentAuction?.id === auctionId 
                            ? updatedAuction 
                            : state.currentAuction,
                        loadingUpdate: false,
                        updateError: null,
                        auctionCache: newCache,
                        lastSuccessfulAction: new Date().getTime()
                    };
                });
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.update_error');
                
                auctionStore.update(state => ({
                    ...state,
                    loadingUpdate: false,
                    updateError: errorMessage
                }));
                
                // Show toast notification for error
                toast.error(errorMessage);
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                loadingUpdate: false,
                updateError: errorMessage
            }));
            
            // Show toast notification for error
            toast.error(errorMessage);
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Delete an auction
     * @param {string|number} auctionId - Auction ID
     * @returns {Promise<Object>} - Operation result
     */
    async deleteAuction(auctionId) {
        if (!auctionId) {
            return { success: false, error: 'Auction ID is required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loadingDelete: true,
            deleteError: null
        }));

        try {
            // Call API service
            const response = await api.delete(`/auctions/${auctionId}`);
            
            if (response) {
                auctionStore.update(state => {
                    // Remove from auctions list
                    const updatedAuctions = state.auctions.filter(auction => 
                        auction.id !== auctionId
                    );
                    
                    // Remove from cache
                    const newCache = { ...state.auctionCache };
                    delete newCache[auctionId];

                    return {
                        ...state,
                        auctions: updatedAuctions,
                        currentAuction: state.currentAuction?.id === auctionId 
                            ? null 
                            : state.currentAuction,
                        loadingDelete: false,
                        deleteError: null,
                        auctionCache: newCache,
                        lastSuccessfulAction: new Date().getTime()
                    };
                });
                
                return { success: true, data: response };
            } else {
                const errorMessage = t('auctions.delete_error');
                
                auctionStore.update(state => ({
                    ...state,
                    loadingDelete: false,
                    deleteError: errorMessage
                }));
                
                // Show toast notification for error
                toast.error(errorMessage);
                
                return { success: false, error: errorMessage };
            }
        } catch (error) {
            const errorMessage = error?.message || t('general.error_occurred');
            
            auctionStore.update(state => ({
                ...state,
                loadingDelete: false,
                deleteError: errorMessage
            }));
            
            // Show toast notification for error
            toast.error(errorMessage);
            
            return { success: false, error: errorMessage };
        }
    },

    /**
     * Reset the current auction state
     */
    resetCurrentAuction() {
        auctionStore.update(state => ({
            ...state,
            currentAuction: null,
            currentAuctionLoading: false,
            currentAuctionError: null,
            currentBids: [],
            bidsLoading: false,
            bidsError: null
        }));
    },

    /**
     * Reset error states
     */
    resetErrors() {
        auctionStore.update(state => ({
            ...state,
            error: null,
            currentAuctionError: null,
            bidsError: null,
            bidError: null,
            createError: null,
            updateError: null,
            deleteError: null
        }));
    },
    
    /**
     * Apply filters from URL parameters
     * @param {URLSearchParams} params - URL search parameters
     */
    applyUrlFilters(params) {
        if (!params) return;
        
        const currentState = get(auctionStore);
        const filtersFromUrl = {};
        
        // Map URL parameters to filters
        for (const key of params.keys()) {
            if (key in currentState.filters) {
                const value = params.get(key);
                
                // Handle boolean values
                if (value === 'true') filtersFromUrl[key] = true;
                else if (value === 'false') filtersFromUrl[key] = false;
                // Handle numeric values
                else if (/^\d+$/.test(value)) filtersFromUrl[key] = parseInt(value, 10);
                else if (/^\d+\.\d+$/.test(value)) filtersFromUrl[key] = parseFloat(value);
                // String values
                else filtersFromUrl[key] = value;
            }
        }
        
        // Only reload if filters have changed
        const hasFilterChanges = Object.keys(filtersFromUrl).some(
            key => filtersFromUrl[key] !== currentState.filters[key]
        );
        
        if (hasFilterChanges && Object.keys(filtersFromUrl).length > 0) {
            this.loadAuctions(filtersFromUrl);
        }
    }
};

// Create derived stores for common queries
const loading = derived(auctionStore, $store => ({
    auctionsLoading: $store.loading,
    currentAuctionLoading: $store.currentAuctionLoading,
    bidsLoading: $store.bidsLoading,
    placingBid: $store.placingBid,
    loadingMore: $store.loadingMore,
    loadingCreate: $store.loadingCreate,
    loadingUpdate: $store.loadingUpdate,
    loadingDelete: $store.loadingDelete,
    anyLoading: $store.loading || $store.currentAuctionLoading || 
                $store.bidsLoading || $store.placingBid || $store.loadingMore ||
                $store.loadingCreate || $store.loadingUpdate || $store.loadingDelete
}));

const auctionsList = derived(auctionStore, $store => $store.auctions);

const auctionsMetadata = derived(auctionStore, $store => ({
    totalCount: $store.totalCount,
    totalPages: $store.totalPages,
    currentPage: $store.currentPage,
    hasMore: $store.currentPage < $store.totalPages
}));

const currentAuction = derived(auctionStore, $store => $store.currentAuction);
const currentBids = derived(auctionStore, $store => $store.currentBids);
const currentFilters = derived(auctionStore, $store => $store.filters);

const errors = derived(auctionStore, $store => ({
    listError: $store.error,
    detailError: $store.currentAuctionError,
    bidsError: $store.bidsError,
    bidError: $store.bidError,
    createError: $store.createError,
    updateError: $store.updateError,
    deleteError: $store.deleteError,
    hasErrors: Boolean($store.error || $store.currentAuctionError || 
                      $store.bidsError || $store.bidError || $store.createError ||
                      $store.updateError || $store.deleteError)
}));

// Set up URL parameter sync for filters if in browser
if (browser) {
    // Subscribe to page store changes
    page.subscribe(($page) => {
        // Safely check if page and URL are defined
        if (!$page || !$page.url) {
            return;
        }
        
        const pathname = $page.url.pathname;
        
        // Only apply filters on auction-related pages
        if (pathname && pathname.includes('/auctions')) {
            auctionActions.applyUrlFilters($page.url.searchParams);
        }
    });
}

// Export the store and actions
export {
    auctionStore,
    auctionActions,
    loading,
    auctionsList,
    auctionsMetadata,
    currentAuction,
    currentBids,
    currentFilters,
    errors
};

// Convenience export for common usage
export default {
    subscribe: auctionStore.subscribe,
    ...auctionActions
};