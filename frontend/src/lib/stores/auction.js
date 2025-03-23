// src/lib/stores/auction.js
// مخزن بيانات المزادات - Auction Store

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import auctionService from '$lib/services/auction';
import { page } from '$app/stores';
import { t } from '$lib/i18n'; 

// State structure for auctions
const initialState = {
    // Main auction collection
    auctions: [],
    // Total number of auctions
    totalCount: 0,
    // Total pages
    totalPages: 1,
    // Current page
    currentPage: 1,
    // Loading states
    loading: false,
    loadingMore: false,
    // Error states
    error: null,
    // Current filters
    filters: {
        status: null,
        auction_type: null,
        property_type: null,
        min_price: null,
        max_price: null,
        city: null,
        district: null,
        is_featured: null,
        sort_by: 'start_date',
        order: 'desc',
        page_size: 12
    },
    // Currently viewed auction detail
    currentAuction: null,
    currentAuctionLoading: false,
    currentAuctionError: null,
    // Bid history for current auction
    currentBids: [],
    bidsLoading: false,
    bidsError: null,
    // New bid being placed
    placingBid: false,
    bidError: null,
    // Cache of auctions by ID 
    auctionCache: {}
};

// Create the writable store
const auctionStore = writable(initialState);

// Action functions to update the store
const auctionActions = {
    /**
     * تحميل قائمة المزادات مع إمكانية التصفية
     * Load a list of auctions with optional filtering
     * 
     * @param {Object} filters - معايير التصفية
     * @param {boolean} append - إضافة النتائج إلى القائمة الحالية (للتحميل عند التمرير)
     */
    async loadAuctions(filters = {}, append = false) {
        const currentState = get(auctionStore);
        
        // If already loading, don't start another request
        if ((currentState.loading && !append) || (currentState.loadingMore && append)) {
            return;
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loading: !append,
            loadingMore: append,
            error: null
        }));

        // Apply existing filters with any new ones
        const appliedFilters = {
            ...currentState.filters,
            ...filters,
            page: append ? currentState.currentPage + 1 : 1
        };

        try {
            const result = await auctionService.getAuctions(appliedFilters);

            if (result.success) {
                const data = result.data;
                // Only update relevant parts of the store
                auctionStore.update(state => {
                    // Cache the fetched auctions
                    const newCache = { ...state.auctionCache };
                    
                    if (data.results && Array.isArray(data.results)) {
                        data.results.forEach(auction => {
                            newCache[auction.id] = {
                                ...auction,
                                lastFetched: new Date().getTime()
                            };
                        });
                    }

                    return {
                        ...state,
                        auctions: append 
                            ? [...state.auctions, ...(data.results || [])]
                            : (data.results || []),
                        totalCount: data.count || 0,
                        totalPages: data.total_pages || 1,
                        currentPage: append ? state.currentPage + 1 : 1,
                        loading: false,
                        loadingMore: false,
                        error: null,
                        filters: appliedFilters,
                        auctionCache: newCache
                    };
                });
            } else {
                auctionStore.update(state => ({
                    ...state,
                    loading: false,
                    loadingMore: false,
                    error: result.error || t('general.error_occurred')
                }));
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                loading: false,
                loadingMore: false,
                error: error.message || t('general.error_occurred')
            }));
        }
    },

    /**
     * تحميل تفاصيل مزاد محدد
     * Load details for a specific auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @param {boolean} includeBids - تضمين المزايدات
     * @param {boolean} includeProperty - تضمين تفاصيل العقار
     * @param {boolean} forceRefresh - إجبار التحديث حتى لو كان المزاد في ذاكرة التخزين المؤقت
     */
    async loadAuctionDetail(auctionId, includeBids = true, includeProperty = true, forceRefresh = false) {
        if (!auctionId) return;

        // Get current state
        const currentState = get(auctionStore);
        
        // Check if auction is already in cache and was recently fetched (within last 5 minutes)
        const cachedAuction = currentState.auctionCache[auctionId];
        const now = new Date().getTime();
        const isCacheFresh = cachedAuction && 
                             cachedAuction.lastFetched && 
                             (now - cachedAuction.lastFetched < 5 * 60 * 1000);

        // If we have a fresh cached version and don't need to refresh, use that
        if (isCacheFresh && !forceRefresh) {
            auctionStore.update(state => ({
                ...state,
                currentAuction: cachedAuction,
                currentAuctionLoading: false,
                currentAuctionError: null
            }));
            
            // Optionally load bids even if using cached auction
            if (includeBids) {
                this.loadAuctionBids(auctionId);
            }
            
            return;
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            currentAuctionLoading: true,
            currentAuctionError: null
        }));

        try {
            const options = {
                include_bids: includeBids,
                include_property: includeProperty,
                include_documents: true
            };

            const result = await auctionService.getAuctionDetails(auctionId, options);

            if (result.success && result.data && result.data.auction) {
                const auctionData = result.data.auction;
                
                // Update the store with auction details
                auctionStore.update(state => {
                    // Add to cache with timestamp
                    const newCache = { 
                        ...state.auctionCache,
                        [auctionId]: {
                            ...auctionData,
                            lastFetched: now
                        }
                    };

                    return {
                        ...state,
                        currentAuction: auctionData,
                        currentAuctionLoading: false,
                        currentAuctionError: null,
                        auctionCache: newCache,
                        // If bids are included in the response, update them too
                        currentBids: auctionData.recent_bids || state.currentBids,
                        bidsLoading: false
                    };
                });
            } else {
                auctionStore.update(state => ({
                    ...state,
                    currentAuctionLoading: false,
                    currentAuctionError: result.error || t('general.error_occurred')
                }));
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                currentAuctionLoading: false,
                currentAuctionError: error.message || t('general.error_occurred')
            }));
        }
    },

    /**
     * تحميل مزايدات المزاد الحالي
     * Load bids for the current auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @param {Object} options - خيارات التصفية
     */
    async loadAuctionBids(auctionId, options = {}) {
        if (!auctionId) return;

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            bidsLoading: true,
            bidsError: null
        }));

        try {
            const result = await auctionService.getAuctionBids(auctionId, options);

            if (result.success && result.data) {
                auctionStore.update(state => ({
                    ...state,
                    currentBids: result.data.results || [],
                    bidsLoading: false,
                    bidsError: null
                }));
            } else {
                auctionStore.update(state => ({
                    ...state,
                    bidsLoading: false,
                    bidsError: result.error || t('general.error_occurred')
                }));
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                bidsLoading: false,
                bidsError: error.message || t('general.error_occurred')
            }));
        }
    },

    /**
     * تقديم مزايدة جديدة
     * Place a new bid on an auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @param {number} bidAmount - قيمة المزايدة
     * @param {boolean} isAutoBid - هل هي مزايدة تلقائية
     * @param {number} maxBidAmount - الحد الأقصى للمزايدة التلقائية (اختياري)
     */
    async placeBid(auctionId, bidAmount, isAutoBid = false, maxBidAmount = null) {
        if (!auctionId || !bidAmount) return;

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            placingBid: true,
            bidError: null
        }));

        try {
            const bidData = {
                auction: auctionId,
                bid_amount: bidAmount,
                is_auto_bid: isAutoBid
            };

            // Add max bid amount for auto bidding
            if (isAutoBid && maxBidAmount) {
                bidData.max_bid_amount = maxBidAmount;
            }

            const result = await auctionService.placeBid(bidData);

            if (result.success && result.data) {
                // Update the store
                auctionStore.update(state => {
                    // Add the new bid to the current bids
                    const newBids = [result.data.bid, ...state.currentBids];
                    
                    // Update the auction with new current bid if available
                    let updatedAuction = { ...state.currentAuction };
                    if (result.data.bid && result.data.bid.bid_amount > (updatedAuction.current_bid || 0)) {
                        updatedAuction.current_bid = result.data.bid.bid_amount;
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
                        auctionCache: newCache
                    };
                });
            } else {
                auctionStore.update(state => ({
                    ...state,
                    placingBid: false,
                    bidError: result.error || t('general.error_occurred')
                }));
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                placingBid: false,
                bidError: error.message || t('general.error_occurred')
            }));
        }
    },

    /**
     * إنشاء مزاد جديد
     * Create a new auction
     * 
     * @param {Object} auctionData - بيانات المزاد الجديد
     * @returns {Promise<Object>} - نتيجة العملية
     */
    async createAuction(auctionData) {
        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loading: true,
            error: null
        }));

        try {
            const result = await auctionService.createAuction(auctionData);

            if (result.success && result.data && result.data.auction) {
                const newAuction = result.data.auction;

                // Update the store
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
                        loading: false,
                        error: null,
                        auctionCache: newCache
                    };
                });

                return { success: true, data: result.data.auction };
            } else {
                auctionStore.update(state => ({
                    ...state,
                    loading: false,
                    error: result.error || t('general.error_occurred')
                }));

                return { success: false, error: result.error };
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                loading: false,
                error: error.message || t('general.error_occurred')
            }));

            return { success: false, error: error.message };
        }
    },

    /**
     * تحديث مزاد موجود
     * Update an existing auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @param {Object} updateData - بيانات التحديث
     * @param {boolean} partial - تحديث جزئي (PATCH) أو كلي (PUT)
     * @returns {Promise<Object>} - نتيجة العملية
     */
    async updateAuction(auctionId, updateData, partial = true) {
        if (!auctionId) {
            return { success: false, error: 'Auction ID is required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            currentAuctionLoading: true,
            currentAuctionError: null
        }));

        try {
            const result = await auctionService.updateAuction(auctionId, updateData, partial);

            if (result.success && result.data && result.data.auction) {
                const updatedAuction = result.data.auction;

                // Update the store
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
                        currentAuction: state.currentAuction?.id === auctionId ? updatedAuction : state.currentAuction,
                        currentAuctionLoading: false,
                        currentAuctionError: null,
                        auctionCache: newCache
                    };
                });

                return { success: true, data: updatedAuction };
            } else {
                auctionStore.update(state => ({
                    ...state,
                    currentAuctionLoading: false,
                    currentAuctionError: result.error || t('general.error_occurred')
                }));

                return { success: false, error: result.error };
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                currentAuctionLoading: false,
                currentAuctionError: error.message || t('general.error_occurred')
            }));

            return { success: false, error: error.message };
        }
    },

    /**
     * حذف مزاد
     * Delete an auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @returns {Promise<Object>} - نتيجة العملية
     */
    async deleteAuction(auctionId) {
        if (!auctionId) {
            return { success: false, error: 'Auction ID is required' };
        }

        // Update loading state
        auctionStore.update(state => ({
            ...state,
            loading: true,
            error: null
        }));

        try {
            const result = await auctionService.deleteAuction(auctionId);

            if (result.success) {
                // Update the store
                auctionStore.update(state => {
                    // Remove from auctions list
                    const updatedAuctions = state.auctions.filter(auction => auction.id !== auctionId);
                    
                    // Remove from cache
                    const newCache = { ...state.auctionCache };
                    delete newCache[auctionId];

                    // Clear current auction if it's the deleted one
                    const currentAuction = state.currentAuction?.id === auctionId ? null : state.currentAuction;

                    return {
                        ...state,
                        auctions: updatedAuctions,
                        currentAuction,
                        loading: false,
                        error: null,
                        auctionCache: newCache
                    };
                });

                return { success: true };
            } else {
                auctionStore.update(state => ({
                    ...state,
                    loading: false,
                    error: result.error || t('general.error_occurred')
                }));

                return { success: false, error: result.error };
            }
        } catch (error) {
            auctionStore.update(state => ({
                ...state,
                loading: false,
                error: error.message || t('general.error_occurred')
            }));

            return { success: false, error: error.message };
        }
    },

    /**
     * إعادة تعيين حالة المزاد الحالي
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
     * إعادة تعيين حالة الخطأ
     * Reset error states
     */
    resetErrors() {
        auctionStore.update(state => ({
            ...state,
            error: null,
            currentAuctionError: null,
            bidsError: null,
            bidError: null
        }));
    }
};

// Create derived stores for common queries
const loading = derived(auctionStore, $store => $store.loading);
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
    bidError: $store.bidError
}));

// Set up URL parameter sync for filters if in browser
if (browser) {
    // Subscribe to page store changes
    page.subscribe(($page) => {
        const currentState = get(auctionStore);
        
        // Don't do anything if we're not on an auction-related page
        if (!$page.url.pathname.includes('/auctions')) {
            return;
        }
        
        // Extract filters from URL parameters
        const urlParams = $page.url.searchParams;
        const filtersFromUrl = {};
        
        // Map URL parameters to filters
        for (const key of urlParams.keys()) {
            if (key in currentState.filters) {
                const value = urlParams.get(key);
                
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
            auctionActions.loadAuctions(filtersFromUrl);
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